"""Module for interacting with YouTube search."""
# Native python imports
import logging
from enum import Enum
from typing import List, Optional, Dict, Callable, Tuple, Set

# Local imports
from pytubefix import YouTube, Channel, Playlist
from pytubefix.helpers import install_proxy
from pytubefix.innertube import InnerTube
from pytubefix.protobuf import encode_protobuf

logger = logging.getLogger(__name__)

class Filter:
    class Type(Enum):
        VIDEO = {2: 1}
        CHANNEL = {2: 2}
        PLAYLIST = {2: 3}
        MOVIE = {2: 4}

    class Duration(Enum):
        UNDER_4_MINUTES = {3: 1}
        OVER_20_MINUTES = {3: 2}
        BETWEEN_4_20_MINUTES = {3: 3}

    class UploadDate(Enum):
        LAST_HOUR = {1: 1}
        TODAY = {1: 2}
        THIS_WEEK = {1: 3}
        THIS_MONTH = {1: 4}
        THIS_YEAR = {1: 5}

    class Features(Enum):
        LIVE = {8: 1}
        _4K = {14: 1}
        HD = {4: 1}
        SUBTITLES_CC = {5: 1}
        CREATIVE_COMMONS = {6: 1}
        _360 = {15: 1}
        VR180 = {26: 1}
        _3D = {7: 1}
        HDR = {25: 1}
        LOCATION = {23: 1}
        PURCHASED = {9: 1}

    class SortBy(Enum):
        RELEVANCE = {1: 0}
        UPLOAD_DATE = {1: 2}
        VIEW_COUNT = {1: 3}
        RATING = {1: 1}

    def __init__(self):
        self._type = None
        self._upload_date = None
        self._duration = None
        self._sort_by = None
        self._features = set()

        # TODO: Remove legacy implementation

        ################################# legacy implementation ####################################

        self.filters = {
            'upload_date': None,
            'type': None,
            'duration': None,
            'features': [],
            'sort_by': None
        }

    def set_filters(self, filter_dict):
        """
        Applies multiple filters at once using a dictionary.
        """
        for category, value in filter_dict.items():
            if category == 'features':
                if isinstance(value, list):
                    logger.debug("Filter features is a list")
                    self.filters['features'].extend(value)
                else:
                    self.filters['features'].append(value)
            else:
                self.filters[category] = value

    def clear_filters(self):
        """
        Clear all filters
        """
        for category in self.filters:
            if category == 'features':
                self.filters[category] = []
            else:
                self.filters[category] = None

    def get_filters_params(self):
        """
        Combines selected filters into a final structure
        """
        combined = {}

        if self.filters['sort_by']:
            combined.update(self.filters['sort_by'])

        combined[2] = {}

        if self.filters['type']:
            combined[2].update(self.filters['type'])

        if self.filters['duration']:
            combined[2].update(self.filters['duration'])

        if self.filters['features']:
            for feature in self.filters['features']:
                combined[2].update(feature)

        if self.filters['upload_date']:
            combined[2].update(self.filters['upload_date'])

        combined[2] = dict(sorted(combined.get(2, {}).items()))

        logger.debug(f"Combined filters: {combined}")

        encoded_filters = encode_protobuf(str(combined))

        logger.debug(f"Filter encoded in protobuf: {encoded_filters}")

        return encoded_filters

    @staticmethod
    def get_upload_date(option: str) -> dict:
        """
        Last Hour,
        Today,
        This Week,
        This Month,
        This Year
        """
        filters = {
            "Last Hour": {1: 1},
            "Today": {1: 2},
            "This Week": {1: 3},
            "This Month": {1: 4},
            "This Year": {1: 5},
        }
        return filters.get(option)

    @staticmethod
    def get_type(option: str) -> dict:
        """
        Video,
        Channel,
        Playlist,
        Movie
        """
        filters = {
            "Video": {2: 1},
            "Channel": {2: 2},
            "Playlist": {2: 3},
            "Movie": {2: 4},
        }
        return filters.get(option)

    @staticmethod
    def get_duration(option: str) -> dict:
        """
        Under 4 minutes,
        Over 20 minutes,
        4 - 20 minutes
        """
        filters = {
            "Under 4 minutes": {3: 1},
            "Over 20 minutes": {3: 2},
            "4 - 20 minutes": {3: 3},
        }
        return filters.get(option)

    @staticmethod
    def get_features(option: str) -> dict:
        """
        Live,
        4K,
        HD,
        Subtitles/CC,
        Creative Commons,
        360,
        VR180,
        3D,
        HDR,
        Location,
        Purchased
        """
        filters = {
            "Live": {8: 1},
            "4K": {14: 1},
            "HD": {4: 1},
            "Subtitles/CC": {5: 1},
            "Creative Commons": {6: 1},
            "360": {15: 1},
            "VR180": {26: 1},
            "3D": {7: 1},
            "HDR": {25: 1},
            "Location": {23: 1},
            "Purchased": {9: 1},
        }
        return filters.get(option)

    @staticmethod
    def get_sort_by(option: str) -> dict:
        """
        Relevance,
        Upload date,
        View count,
        Rating
        """
        filters = {
            "Relevance": {1: 0},
            "Upload date": {1: 2},
            "View count": {1: 3},
            "Rating": {1: 1},
        }
        return filters.get(option)

    ################################# legacy implementation ####################################

    @classmethod
    def create(cls):
        return cls()

    def type(self, t: Type):
        self._type = t
        return self

    def upload_date(self, u: UploadDate):
        self._upload_date = u
        return self

    def duration(self, d: Duration):
        self._duration = d
        return self

    def sort_by(self, s: SortBy):
        self._sort_by = s
        return self

    def feature(self, features: List[Features]):
        if isinstance(features, list):
            self._features.update(features)
        else:
            self._features.update([features])
        return self

    def merge(self):
        result = {}
        group_2 = {}

        if self._sort_by is not None:
            sort_dict = self._sort_by.value
            if len(sort_dict) != 1 or 1 not in sort_dict:
                raise ValueError("SortBy must have exactly {1: <value>}")
            result[1] = sort_dict[1]

        for val in [self._type, self._upload_date, self._duration]:
            if val is not None:
                for k, v in val.value.items():
                    group_2[k] = v

        for f in self._features:
            for k, v in f.value.items():
                group_2[k] = v

        if group_2:
            result[2] = group_2

        logger.debug(f"Combined filters: {result}")

        return str(result)

    def __repr__(self):
        return (f"Filter(type={self._type}, upload_date={self._upload_date}, "
                f"duration={self._duration}, sort_by={self._sort_by}, "
                f"features={[f.name for f in self._features]})")


class Search:
    def __init__(
            self, query: str,
            client: str = InnerTube().client_name,
            proxies: Optional[Dict[str, str]] = None,
            use_oauth: bool = False,
            allow_oauth_cache: bool = True,
            token_file: Optional[str] = None,
            oauth_verifier: Optional[Callable[[str, str], None]] = None,
            use_po_token: Optional[bool] = False,
            po_token_verifier: Optional[Callable[[None], Tuple[str, str]]] = None,
            filters: Optional[Filter] = None
    ):
        """Initialize Search object.

        :param str query:
            Search query provided by the user.
        :param dict proxies:
            (Optional) A dict mapping protocol to proxy address which will be used by pytube.
        :param bool use_oauth:
            (Optional) Prompt the user to authenticate to YouTube.
            If allow_oauth_cache is set to True, the user should only be prompted once.
        :param bool allow_oauth_cache:
            (Optional) Cache OAuth tokens locally on the machine. Defaults to True.
            These tokens are only generated if use_oauth is set to True as well.
        :param str token_file:
            (Optional) Path to the file where the OAuth tokens will be stored.
            Defaults to None, which means the tokens will be stored in the pytubefix/__cache__ directory.
        :param Callable oauth_verifier:
            (optional) Verifier to be used for getting OAuth tokens. 
            Verification URL and User-Code will be passed to it respectively.
            (if passed, else default verifier will be used)
        :param bool use_po_token:
            (Optional) Prompt the user to use the proof of origin token on YouTube.
            It must be sent with the API along with the linked visitorData and
            then passed as a `po_token` query parameter to affected clients.
            If allow_oauth_cache is set to True, the user should only be prompted once.
        :param Callable po_token_verifier:
            (Optional) Verified used to obtain the visitorData and po_token.
            The verifier will return the visitorData and po_token respectively.
            (if passed, else default verifier will be used)
        :param Filter filters:
            (Optional) Apply filters when searching.
            Can be used: `upload_date`, `type`, `duration`, `features`, `sort_by`.
            features can be combined into a list with other parameters of the same type.
        """
        self.query = query
        self.client = client
        self.use_oauth = use_oauth
        self.allow_oauth_cache = allow_oauth_cache
        self.token_file = token_file
        self.oauth_verifier = oauth_verifier

        self.use_po_token = use_po_token
        self.po_token_verifier = po_token_verifier

        self._innertube_client = InnerTube(
            client='WEB',
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache,
            token_file=self.token_file,
            oauth_verifier=self.oauth_verifier,
            use_po_token=self.use_po_token,
            po_token_verifier=self.po_token_verifier
        )

        # The first search, without a continuation, is structured differently
        #  and contains completion suggestions, so we must store this separately
        self._initial_results = None

        self._results = {}
        self._completion_suggestions = None

        # Used for keeping track of query continuations so that new results
        #  are always returned when get_next_results() is called
        self._current_continuation = None

        if proxies:
            install_proxy(proxies)

        self.filter = None
        if filters:
            logger.debug("Filters found, starting combination")

            # TODO: 
            if isinstance(filters, dict):
                logging.warning("This filter implementation is obsolete and will be removed soon. "
                                "Please refer to the documentation for the new implementation. "
                                "https://pytubefix.readthedocs.io/en/latest/user/search.html")
                filter_protobuf = Filter()
                filter_protobuf.set_filters(filters)
                self.filter = filter_protobuf.get_filters_params()

            else:
                self.filter = encode_protobuf(filters.merge())
                logger.debug(f"Filter encoded in protobuf: {self.filter}")

    @property
    def completion_suggestions(self):
        """Return query autocompletion suggestions for the query.

        :rtype: list
        :returns:
            A list of autocomplete suggestions provided by YouTube for the query.
        """
        if self._completion_suggestions:
            return self._completion_suggestions
        if self.results:
            self._completion_suggestions = self._initial_results['refinements']
        return self._completion_suggestions

    def _get_results(self):
        """Search results and filter them

        """
        results, continuation = self.fetch_and_parse()
        self._current_continuation = continuation
        self._results['videos'] = results['videos']
        self._results['shorts'] = results['shorts']
        self._results['playlist'] = results['playlist']
        self._results['channel'] = results['channel']

    @property
    def videos(self) -> List[YouTube]:
        """Returns the search result videos.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list[YouTube]
        :returns:
            A list of YouTube objects.
        """
        if not self._results:
            self._get_results()

        return [items for items in self._results['videos']]

    @property
    def shorts(self) -> List[YouTube]:
        """Returns the search result shorts.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list[YouTube]
        :returns:
            A list of YouTube objects.
        """
        if not self._results:
            self._get_results()

        return [items for items in self._results['shorts']]

    @property
    def playlist(self) -> List[Playlist]:
        """Returns the search result playlist.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list[Playlist]
        :returns:
            A list of Playlist objects.
        """
        if not self._results:
            self._get_results()

        return [items for items in self._results['playlist']]

    @property
    def channel(self) -> List[Channel]:
        """Returns the search result channel.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list[Channel]
        :returns:
            A list of Channel objects.
        """
        if not self._results:
            self._get_results()

        return [items for items in self._results['channel']]

    @property
    def results(self) -> list:
        """returns a list with videos, shorts, playlist and channels.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list
        :returns:
            A list of YouTube, Playlist and Channel objects.
        """

        if not self._results:
            self._get_results()

        return [items for values in self._results.values() for items in values]

    @property
    def all(self) -> list:
        """
        Return all objects found in the search
        """
        if not self._results:
            self._get_results()

        return [items for values in self._results.values() for items in values]

    def get_next_results(self):
        """Use the stored continuation string to fetch the next set of results.

        This method does not return the results, but instead updates the results property.
        """
        if self._current_continuation:
            results, continuation = self.fetch_and_parse(self._current_continuation)
            self._current_continuation = continuation
            self._results['videos'].extend(results['videos'])
            self._results['shorts'].extend(results['shorts'])
            self._results['playlist'].extend(results['playlist'])
            self._results['channel'].extend(results['channel'])
        else:
            self._get_results()

    def fetch_and_parse(self, continuation=None):
        """Fetch from the innertube API and parse the results.

        :param str continuation:
            Continuation string for fetching results.
        :rtype: tuple
        :returns:
            A tuple of a list of YouTube objects and a continuation string.
        """
        # Begin by executing the query and identifying the relevant sections
        #  of the results
        raw_results = self.fetch_query(continuation,
                                       # The filter parameter must only be passed in the first API call
                                       # After the first call, the continuation token already contains the filter
                                       {'params': self.filter} if self.filter and not continuation else None
                                       )

        # Initial result is handled by try block, continuations by except block
        try:
            sections = raw_results['contents']['twoColumnSearchResultsRenderer'][
                'primaryContents']['sectionListRenderer']['contents']
        except KeyError:
            sections = raw_results['onResponseReceivedCommands'][0][
                'appendContinuationItemsAction']['continuationItems']
        item_renderer = None
        continuation_renderer = None
        for s in sections:
            if 'itemSectionRenderer' in s:
                item_renderer = s['itemSectionRenderer']
            if 'continuationItemRenderer' in s:
                continuation_renderer = s['continuationItemRenderer']

        # If the continuationItemRenderer doesn't exist, assume no further results
        if continuation_renderer:
            next_continuation = continuation_renderer['continuationEndpoint'][
                'continuationCommand']['token']
        else:
            next_continuation = None

        # If the itemSectionRenderer doesn't exist, assume no results.
        results = {}
        if item_renderer:
            videos = []
            shorts = []
            playlist = []
            channel = []
            raw_video_list = item_renderer['contents']
            for video_details in raw_video_list:
                # Skip over ads
                if video_details.get('searchPyvRenderer', {}).get('ads', None):
                    continue

                # Skip "recommended" type videos e.g. "people also watched" and "popular X"
                #  that break up the search results
                if 'shelfRenderer' in video_details:
                    continue

                # Skip auto-generated "mix" playlist results
                if 'radioRenderer' in video_details:
                    continue

                # Skip 'people also searched for' results
                if 'horizontalCardListRenderer' in video_details:
                    continue

                # Can't seem to reproduce, probably related to typo fix suggestions
                if 'didYouMeanRenderer' in video_details:
                    continue

                # Seems to be the renderer used for the image shown on a no results page
                if 'backgroundPromoRenderer' in video_details:
                    continue

                # Get playlist results
                if 'playlistRenderer' in video_details:
                    playlist.append(Playlist(f"https://www.youtube.com/playlist?list="
                                             f"{video_details['playlistRenderer']['playlistId']}",
                                             client=self.client,
                                             use_oauth=self.use_oauth,
                                             allow_oauth_cache=self.allow_oauth_cache,
                                             token_file=self.token_file,
                                             oauth_verifier=self.oauth_verifier,
                                             use_po_token=self.use_po_token,
                                             po_token_verifier=self.po_token_verifier
                                             ))

                # Get channel results
                if 'channelRenderer' in video_details:
                    channel.append(Channel(f"https://www.youtube.com/channel/"
                                           f"{video_details['channelRenderer']['channelId']}",
                                           client=self.client,
                                           use_oauth=self.use_oauth,
                                           allow_oauth_cache=self.allow_oauth_cache,
                                           token_file=self.token_file,
                                           oauth_verifier=self.oauth_verifier,
                                           use_po_token=self.use_po_token,
                                           po_token_verifier=self.po_token_verifier
                                           ))

                # Get shorts results
                if 'reelShelfRenderer' in video_details:
                    for items in video_details['reelShelfRenderer']['items']:
                        if 'reelItemRenderer' in items:
                            video_id = items['reelItemRenderer']['videoId']
                        else:
                            video_id = items['shortsLockupViewModel']['onTap']['innertubeCommand'][
                                'reelWatchEndpoint']['videoId']

                        shorts.append(YouTube(f"https://www.youtube.com/watch?v={video_id}",
                                              client=self.client,
                                              use_oauth=self.use_oauth,
                                              allow_oauth_cache=self.allow_oauth_cache,
                                              token_file=self.token_file,
                                              oauth_verifier=self.oauth_verifier,
                                              use_po_token=self.use_po_token,
                                              po_token_verifier=self.po_token_verifier
                                              ))

                # Get videos results
                if 'videoRenderer' in video_details:
                    videos.append(YouTube(f"https://www.youtube.com/watch?v="
                                          f"{video_details['videoRenderer']['videoId']}",
                                          client=self.client,
                                          use_oauth=self.use_oauth,
                                          allow_oauth_cache=self.allow_oauth_cache,
                                          token_file=self.token_file,
                                          oauth_verifier=self.oauth_verifier,
                                          use_po_token=self.use_po_token,
                                          po_token_verifier=self.po_token_verifier
                                          ))

            results['videos'] = videos
            results['shorts'] = shorts
            results['playlist'] = playlist
            results['channel'] = channel

        return results, next_continuation

    def fetch_query(self, continuation: str = None, filters: dict = None):
        """Fetch raw results from the innertube API.

        :param str continuation:
            Continuation string for fetching results.
        :param dict filters:
            Parameter encoded in protobuf that contains the search filters.
        :rtype: dict
        :returns:
            The raw json object returned by the innertube API.
        """
        query_results = self._innertube_client.search(self.query, continuation=continuation, data=filters)
        if not self._initial_results:
            self._initial_results = query_results
        return query_results  # noqa:R504
