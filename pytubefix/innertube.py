"""This module is designed to interact with the innertube API.

This module is NOT intended to be used directly by end users, as each of the
interfaces returns raw results. These should instead be parsed to extract
the useful information for the end user.
"""
# Native python imports
import json
import os
import pathlib
import time
from urllib import parse

# Local imports
from pytubefix import request

# YouTube on TV client secrets
_client_id = '861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com'
_client_secret = 'SboVhoG9s0rNafixCSGGKXAT'

# Extracted API keys -- unclear what these are linked to.
# API keys are not required, see: https://github.com/TeamNewPipe/NewPipeExtractor/pull/1168
_api_keys = [
    'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
    'AIzaSyCtkvNIR1HCEwzsqK6JuE6KqpyjusIRI30',
    'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w',
    'AIzaSyC8UYZpvA2eknNex0Pjid0_eTLJoDu6los',
    'AIzaSyCjc_pVEDi4qsv5MtC2dMXzpIaDoRFLsxw',
    'AIzaSyDHQ9ipnphqTzDqZsbtd8_Ru4_kiKVQe2k'
]

_default_clients = {
    'WEB': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'osName': 'Windows',
                    'osVersion': '10.0',
                    'clientVersion': '2.20240709.01.00',
                    'platform': 'DESKTOP'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0',
            'X-Youtube-Client-Name': '1',
            'X-Youtube-Client-Version': '2.20240709.01.00'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'WEB_EMBED': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'WEB_EMBEDDED_PLAYER',
                    'osName': 'Windows',
                    'osVersion': '10.0',
                    'clientVersion': '2.20240530.02.00',
                    'clientScreen': 'EMBED'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0',
            'X-Youtube-Client-Name': '56'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'WEB_MUSIC': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'WEB_REMIX',
                    'clientVersion': '1.20240403.01.00'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0',
            'X-Youtube-Client-Name': '67'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'WEB_CREATOR': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'WEB_CREATOR',
                    'clientVersion': '1.20220726.00.00'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0',
            'X-Youtube-Client-Name': '62'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'WEB_SAFARI': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'clientVersion': '2.20240726.00.00',
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15,gzip(gfe)',
            'X-Youtube-Client-Name': '1'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'MWEB': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'MWEB',
                    'clientVersion': '2.20240726.01.00'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
            'X-Youtube-Client-Name': '2'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'ANDROID': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'ANDROID',
                    'clientVersion': '19.29.37',
                    'platform': 'MOBILE',
                    'osName': 'Android',
                    'osVersion': '14',
                    'androidSdkVersion': '34'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.android.youtube/',
            'X-Youtube-Client-Name': '3'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    # Deprecated
    #   'ANDROID_EMBED': {
    #     'innertube_context': {
    #         'context': {
    #             'client': {
    #                 'clientName': 'ANDROID_EMBEDDED_PLAYER',
    #                 'clientVersion': '19.13.36',
    #                 'clientScreen': 'EMBED',
    #                 'androidSdkVersion': '30'
    #             }
    #         }
    #     },
    #     'header': {
    #         'User-Agent': 'com.google.android.youtube/',
    #         'X-Youtube-Client-Name': '55',
    #         'X-Youtube-Client-Version': '19.13.36'
    #     },
    #     'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
    #     'require_js_player': False
    # },

    'ANDROID_VR': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'ANDROID_VR',
                    'clientVersion': '1.57.29',
                    'deviceMake': 'Oculus',
                    'deviceModel': 'Quest 3',
                    'osName': 'Android',
                    'osVersion': '12L',
                    'androidSdkVersion': '32'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.android.apps.youtube.vr.oculus/1.57.29 (Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip',
            'X-Youtube-Client-Name': '28'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'ANDROID_MUSIC': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'ANDROID_MUSIC',
                    'clientVersion': '7.11.50',
                    'androidSdkVersion': '30',
                    'osName': 'Android',
                    'osVersion': '11'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.android.apps.youtube.music/7.11.50 (Linux; U; Android 11) gzip',
            'X-Youtube-Client-Name': '21'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'ANDROID_CREATOR': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'ANDROID_CREATOR',
                    'clientVersion': '24.30.100',
                    'androidSdkVersion': '30',
                    'osName': 'Android',
                    'osVersion': '11'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.android.apps.youtube.creator/24.30.100 (Linux; U; Android 11) gzip',
            'X-Youtube-Client-Name': '14'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'ANDROID_TESTSUITE': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'ANDROID_TESTSUITE',
                    'clientVersion': '1.9',
                    'platform': 'MOBILE',
                    'osName': 'Android',
                    'osVersion': '14',
                    'androidSdkVersion': '34'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.android.youtube/',
            'X-Youtube-Client-Name': '30',
            'X-Youtube-Client-Version': '1.9'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'ANDROID_PRODUCER': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'ANDROID_PRODUCER',
                    'clientVersion': '0.111.1',
                    'androidSdkVersion': '30',
                    'osName': 'Android',
                    'osVersion': '11'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.android.apps.youtube.producer/0.111.1 (Linux; U; Android 11) gzip',
            'X-Youtube-Client-Name': '91'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'IOS': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'IOS',
                    'clientVersion': '19.29.1',
                    'deviceMake': 'Apple',
                    'platform': 'MOBILE',
                    'osName': 'iPhone',
                    'osVersion': '17.5.1.21F90',
                    'deviceModel': 'iPhone16,2'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
            'X-Youtube-Client-Name': '5'
        },
        'api_key': 'AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc',
        'require_js_player': False
    },

    # Deprecated
    # 'IOS_EMBED': {
    #     'innertube_context': {
    #         'context': {
    #             'client': {
    #                 'clientName': 'IOS_MESSAGES_EXTENSION',
    #                 'clientVersion': '19.16.3',
    #                 'deviceMake': 'Apple',
    #                 'platform': 'MOBILE',
    #                 'osName': 'iOS',
    #                 'osVersion': '17.4.1.21E237',
    #                 'deviceModel': 'iPhone15,5'
    #             }
    #         }
    #     },
    #     'header': {
    #         'User-Agent': 'com.google.ios.youtube/',
    #         'X-Youtube-Client-Name': '66'
    #     },
    #     'api_key': 'AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc',
    #     'require_js_player': False
    # },

    'IOS_MUSIC': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'IOS_MUSIC',
                    'clientVersion': '7.08.2',
                    'deviceMake': 'Apple',
                    'platform': 'MOBILE',
                    'osName': 'iPhone',
                    'osVersion': '17.5.1.21F90',
                    'deviceModel': 'iPhone16,2'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.ios.youtubemusic/7.08.2 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
            'X-Youtube-Client-Name': '26'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'IOS_CREATOR': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'IOS_CREATOR',
                    'clientVersion': '24.30.100',
                    'deviceMake': 'Apple',
                    'deviceModel': 'iPhone16,2',
                    'osName': 'iPhone',
                    'osVersion': '17.5.1.21F90'
                }
            }
        },
        'header': {
            'User-Agent': 'com.google.ios.ytcreator/24.30.100 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X;)',
            'X-Youtube-Client-Name': '15'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    },

    'TV_EMBED': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'TVHTML5_SIMPLY_EMBEDDED_PLAYER',
                    'clientVersion': '2.0',
                    'clientScreen': 'EMBED',
                    'platform': 'TV'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0',
            'X-Youtube-Client-Name': '85'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': True
    },

    'MEDIA_CONNECT': {
        'innertube_context': {
            'context': {
                'client': {
                    'clientName': 'MEDIA_CONNECT_FRONTEND',
                    'clientVersion': '0.1'
                }
            }
        },
        'header': {
            'User-Agent': 'Mozilla/5.0',
            'X-Youtube-Client-Name': '95'
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'require_js_player': False
    }
}
_token_timeout = 1800
_cache_dir = pathlib.Path(__file__).parent.resolve() / '__cache__'
_token_file = os.path.join(_cache_dir, 'tokens.json')


def _default_oauth_verifier(verification_url: str, user_code: str):
    """ Default `print(...)` and `input(...)` for oauth verification """
    print(f'Please open {verification_url} and input code {user_code}')
    input('Press enter when you have completed this step.')



class InnerTube:
    """Object for interacting with the innertube API."""

    def __init__(self, client='ANDROID_TESTSUITE', use_oauth=False, allow_cache=True, token_file=None, oauth_verifier=None):
        """Initialize an InnerTube object.

        :param str client:
            Client to use for the object.
            The default is ANDROID_TESTSUITE because there is no need to decrypt the
            signature cipher and throttling parameter.
        :param bool use_oauth:
            Whether or not to authenticate to YouTube.
        :param bool allow_cache:
            Allows caching of oauth tokens on the machine.
        :param Callable oauth_verifier:
            Verifier to be used for getting outh tokens. 
            Verification URL and User-Code will be passed to it respectively. 
            (if passed, else default verifier will be used)
        """
        self.innertube_context = _default_clients[client]['innertube_context']
        self.header = _default_clients[client]['header']
        self.api_key = _default_clients[client]['api_key']
        self.require_js_player = _default_clients[client]['require_js_player']
        self.access_token = None
        self.refresh_token = None
        self.use_oauth = use_oauth
        self.allow_cache = allow_cache
        self.oauth_verifier = oauth_verifier or _default_oauth_verifier

        # Stored as epoch time
        self.expires = None

        # Try to load from file if specified
        self.token_file = token_file or _token_file
        if self.use_oauth and self.allow_cache and os.path.exists(self.token_file):
            with open(self.token_file) as f:
                data = json.load(f)
                self.access_token = data['access_token']
                self.refresh_token = data['refresh_token']
                self.expires = data['expires']
                self.refresh_bearer_token()

    def cache_tokens(self):
        """Cache tokens to file if allowed."""
        if not self.allow_cache:
            return

        data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires': self.expires
        }
        if not os.path.exists(_cache_dir):
            os.mkdir(_cache_dir)
        with open(self.token_file, 'w') as f:
            json.dump(data, f)

    def refresh_bearer_token(self, force=False):
        """Refreshes the OAuth token if necessary.

        :param bool force:
            Force-refresh the bearer token.
        """
        if not self.use_oauth:
            return
        # Skip refresh if it's not necessary and not forced
        if self.expires > time.time() and not force:
            return

        # Subtracting 30 seconds is arbitrary to avoid potential time discrepencies
        start_time = int(time.time() - 30)
        data = {
            'client_id': _client_id,
            'client_secret': _client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        response = request._execute_request(
            'https://oauth2.googleapis.com/token',
            'POST',
            headers={
                'Content-Type': 'application/json'
            },
            data=data
        )
        response_data = json.loads(response.read())

        self.access_token = response_data['access_token']
        self.expires = start_time + response_data['expires_in']
        self.cache_tokens()

    def fetch_bearer_token(self):
        """Fetch an OAuth token."""
        # Subtracting 30 seconds is arbitrary to avoid potential time discrepencies
        start_time = int(time.time() - 30)
        data = {
            'client_id': _client_id,
            'scope': 'https://www.googleapis.com/auth/youtube'
        }
        response = request._execute_request(
            'https://oauth2.googleapis.com/device/code',
            'POST',
            headers={
                'Content-Type': 'application/json'
            },
            data=data
        )
        response_data = json.loads(response.read())
        verification_url = response_data['verification_url']
        user_code = response_data['user_code']
        self.oauth_verifier(verification_url, user_code)

        data = {
            'client_id': _client_id,
            'client_secret': _client_secret,
            'device_code': response_data['device_code'],
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
        }
        response = request._execute_request(
            'https://oauth2.googleapis.com/token',
            'POST',
            headers={
                'Content-Type': 'application/json'
            },
            data=data
        )
        response_data = json.loads(response.read())

        self.access_token = response_data['access_token']
        self.refresh_token = response_data['refresh_token']
        self.expires = start_time + response_data['expires_in']
        self.cache_tokens()

    @property
    def base_url(self):
        """Return the base url endpoint for the innertube API."""
        return 'https://www.youtube.com/youtubei/v1'

    @property
    def base_data(self) -> dict:
        """Return the base json data to transmit to the innertube API."""
        return self.innertube_context

    @property
    def base_params(self):
        """Return the base query parameters to transmit to the innertube API."""
        return {
            'prettyPrint': "false"
        }

    def _call_api(self, endpoint, query, data):
        """Make a request to a given endpoint with the provided query parameters and data."""
        # When YouTube used an API key, it was necessary to remove it when using oauth
        # if self.use_oauth:
        #     del query['key']

        endpoint_url = f'{endpoint}?{parse.urlencode(query)}'
        headers = {
            'Content-Type': 'application/json',
        }
        # Add the bearer token if applicable
        if self.use_oauth:
            if self.access_token:
                self.refresh_bearer_token()
            else:
                self.fetch_bearer_token()

            headers['Authorization'] = f'Bearer {self.access_token}'

        headers.update(self.header)

        response = request._execute_request(
            endpoint_url,
            'POST',
            headers=headers,
            data=data
        )
        return json.loads(response.read())

    def browse(self):
        """Make a request to the browse endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/browse'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def config(self):
        """Make a request to the config endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/config'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def guide(self):
        """Make a request to the guide endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/guide'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def next(self):
        """Make a request to the next endpoint.

        TODO: Figure out how we can use this
        """
        # endpoint = f'{self.base_url}/next'  # noqa:E800
        ...
        # return self._call_api(endpoint, query, self.base_data)  # noqa:E800

    def player(self, video_id):
        """Make a request to the player endpoint.

        :param str video_id:
            The video id to get player info for.
        :rtype: dict
        :returns:
            Raw player info results.
        """
        endpoint = f'{self.base_url}/player'
        query = self.base_params

        self.base_data.update({'videoId': video_id, 'contentCheckOk': "true"})
        return self._call_api(endpoint, query, self.base_data)

    def search(self, search_query, continuation=None):
        """Make a request to the search endpoint.

        :param str search_query:
            The query to search.
        :rtype: dict
        :returns:
            Raw search query results.
        """
        endpoint = f'{self.base_url}/search'
        query = self.base_params
        data = {}
        self.base_data.update({'query': search_query})
        if continuation:
            data['continuation'] = continuation
        data.update(self.base_data)
        return self._call_api(endpoint, query, data)

    def verify_age(self, video_id):
        """Make a request to the age_verify endpoint.

        Notable examples of the types of video this verification step is for:
        * https://www.youtube.com/watch?v=QLdAhwSBZ3w
        * https://www.youtube.com/watch?v=hc0ZDaAZQT0

        :param str video_id:
            The video id to get player info for.
        :rtype: dict
        :returns:
            Returns information that includes a URL for bypassing certain restrictions.
        """
        endpoint = f'{self.base_url}/verify_age'
        data = {
            'nextEndpoint': {
                'watchEndpoint': {
                    'racyCheckOk': True,
                    'contentCheckOk': True,
                    'videoId': video_id
                }
            },
            'setControvercy': True
        }
        data.update(self.base_data)
        result = self._call_api(endpoint, self.base_params, data)
        return result

    def get_transcript(self, video_id):
        """Make a request to the get_transcript endpoint.

        This is likely related to captioning for videos, but is currently untested.
        """
        endpoint = f'{self.base_url}/get_transcript'
        query = {
            'videoId': video_id,
        }
        query.update(self.base_params)
        result = self._call_api(endpoint, query, self.base_data)
        return result
