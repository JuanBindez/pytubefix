# MIT License
#
# Copyright (c) 2023 - 2025 Juan Bindez <juanbindez780@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
This module implements the core developer interface for pytubefix.

The problem domain of the :class:`YouTube <YouTube> class focuses almost
exclusively on the developer interface. Pytubefix offloads the heavy lifting to
smaller peripheral modules and functions.

"""

import logging
from subprocess import CalledProcessError
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytubefix
import pytubefix.exceptions as exceptions
from pytubefix import extract, request
from pytubefix import Stream, StreamQuery
from pytubefix.helpers import install_proxy
from pytubefix.innertube import InnerTube
from pytubefix.metadata import YouTubeMetadata
from pytubefix.monostate import Monostate
from pytubefix.botGuard import bot_guard

logger = logging.getLogger(__name__)


class YouTube:
    """Core developer interface for pytubefix."""

    def __init__(
            self,
            url: str,
            client: str = InnerTube().client_name,
            on_progress_callback: Optional[Callable[[Any, bytes, int], None]] = None,
            on_complete_callback: Optional[Callable[[Any, Optional[str]], None]] = None,
            proxies: Optional[Dict[str, str]] = None,
            use_oauth: bool = False,
            allow_oauth_cache: bool = True,
            token_file: Optional[str] = None,
            oauth_verifier: Optional[Callable[[str, str], None]] = None,
            use_po_token: Optional[bool] = False,
            po_token_verifier: Optional[Callable[[None], Tuple[str, str]]] = None,
    ):
        """Construct a :class:`YouTube <YouTube>`.

        :param str url:
            A valid YouTube watch URL.
        :param str client:
            (Optional) A YouTube client,
            Available:
                WEB, WEB_EMBED, WEB_MUSIC, WEB_CREATOR, WEB_SAFARI,
                ANDROID, ANDROID_MUSIC, ANDROID_CREATOR, ANDROID_VR, ANDROID_PRODUCER, ANDROID_TESTSUITE,
                IOS, IOS_MUSIC, IOS_CREATOR,
                MWEB, TV, TV_EMBED, MEDIA_CONNECT.
        :param func on_progress_callback:
            (Optional) User defined callback function for stream download
            progress events.
        :param func on_complete_callback:
            (Optional) User defined callback function for stream download
            complete events.
        :param dict proxies:
            (Optional) A dict mapping protocol to proxy address which will be used by pytube.
        :param bool use_oauth:
            (Optional) Prompt the user to authenticate to YouTube.
            If allow_oauth_cache is set to True, the user should only be prompted once.
        :param bool allow_oauth_cache:
            (Optional) Cache OAuth and Po tokens locally on the machine. Defaults to True.
            These tokens are only generated if use_oauth is set to True as well.
        :param str token_file:
            (Optional) Path to the file where the OAuth and Po tokens will be stored.
            Defaults to None, which means the tokens will be stored in the pytubefix/__cache__ directory.
        :param Callable oauth_verifier:
            (optional) Verifier to be used for getting oauth tokens. 
            Verification URL and User-Code will be passed to it respectively.
            (if passed, else default verifier will be used)
        """
        # js fetched by js_url
        self._js: Optional[str] = None

        # the url to the js, parsed from watch html
        self._js_url: Optional[str] = None

        # content fetched from innertube/player
        self._vid_info: Optional[Dict] = None
        self._vid_details: Optional[Dict] = None

        # the html of /watch?v=<video_id>
        self._watch_html: Optional[str] = None
        self._embed_html: Optional[str] = None

        # inline js in the html containing
        self._player_config_args: Optional[Dict] = None
        self._age_restricted: Optional[bool] = None

        self._fmt_streams: Optional[List[Stream]] = None

        self._initial_data = None
        self._metadata: Optional[YouTubeMetadata] = None

        # video_id part of /watch?v=<video_id>
        self.video_id = extract.video_id(url)

        self.watch_url = f"https://youtube.com/watch?v={self.video_id}"
        self.embed_url = f"https://www.youtube.com/embed/{self.video_id}"

        self.client = client

        # oauth can only be used by the TV and TV_EMBED client.
        self.client = 'TV' if use_oauth else self.client

        self.fallback_clients = ['TV', 'IOS']

        self._signature_timestamp: dict = {}
        self._visitor_data = None

        # Shared between all instances of `Stream` (Borg pattern).
        self.stream_monostate = Monostate(
            on_progress=on_progress_callback, on_complete=on_complete_callback, youtube=self
        )

        if proxies:
            install_proxy(proxies)

        self._author = None
        self._title = None
        self._original_title = None
        self._publish_date = None

        self.use_oauth = use_oauth
        self.allow_oauth_cache = allow_oauth_cache
        self.token_file = token_file
        self.oauth_verifier = oauth_verifier


        # TODO: This does not work, remove poToken manually in the next update
        # https://github.com/FreeTubeApp/FreeTube/pull/8137
        self.use_po_token = use_po_token
        self.po_token_verifier = po_token_verifier

        if self.use_po_token or self.po_token_verifier:
            logger.warning("`use_po_token` and `po_token_verifier` is deprecated and will be removed soon.")

        self.po_token = None
        self._pot = None

    def __repr__(self):
        return f'<pytubefix.__main__.YouTube object: videoId={self.video_id}>'

    def __eq__(self, o: object) -> bool:
        # Compare types and urls, if they're same return true, else return false.
        return type(o) == type(self) and o.watch_url == self.watch_url

    @property
    def watch_html(self):
        if self._watch_html:
            return self._watch_html
        self._watch_html = request.get(url=self.watch_url)
        return self._watch_html

    @property
    def embed_html(self):
        if self._embed_html:
            return self._embed_html
        self._embed_html = request.get(url=self.embed_url)
        return self._embed_html

    @property
    def age_restricted(self):
        if self._age_restricted:
            return self._age_restricted
        self._age_restricted = extract.is_age_restricted(self.watch_html)
        return self._age_restricted

    @property
    def js_url(self):
        if self._js_url:
            return self._js_url

        if self.age_restricted:
            self._js_url = extract.js_url(self.embed_html)
        else:
            self._js_url = extract.js_url(self.watch_html)

        return self._js_url

    @property
    def js(self):
        if self._js:
            return self._js

        # If the js_url doesn't match the cached url, fetch the new js and update
        #  the cache; otherwise, load the cache.
        if pytubefix.__js_url__ != self.js_url:
            self._js = request.get(self.js_url)
            pytubefix.__js__ = self._js
            pytubefix.__js_url__ = self.js_url
        else:
            self._js = pytubefix.__js__

        return self._js

    @property
    def visitor_data(self) -> str:
        """
        Retrieves the visitorData from the WEB client.
        """
        if self._visitor_data:
            return self._visitor_data

        if InnerTube(self.client).require_po_token:
            try:
                logger.debug("Looking for visitorData in initial_data")
                self._visitor_data = extract.visitor_data(str(self.initial_data['responseContext']))
                logger.debug('VisitorData obtained successfully')
                return self._visitor_data
            except (KeyError, pytubefix.exceptions.RegexMatchError):
                logger.debug("Unable to obtain visitorData from initial_data. Trying to request from the WEB client")

        logger.debug("Looking for visitorData in InnerTube API")
        innertube_response = InnerTube('WEB').player(self.video_id)
        try:
            self._visitor_data = innertube_response['responseContext']['visitorData']
        except KeyError:
            p_dicts = innertube_response['responseContext']['serviceTrackingParams'][0]['params']
            self._visitor_data = next(p for p in p_dicts if p['key'] == 'visitor_data')['value']
        logger.debug('VisitorData obtained successfully')

        return self._visitor_data

    @property
    def pot(self) -> str:
        """
        Retrieves the poToken generated by botGuard.

        This poToken only works for WEB-based clients.
        """
        if self._pot:
            return self._pot
        logger.debug('Running botGuard')
        try:
            self._pot = bot_guard.generate_po_token(video_id=self.video_id)
            logger.debug('PoToken generated successfully')
        except Exception as e:
            logger.warning('Unable to run botGuard. Skipping poToken generation, reason: ' + e.__str__())
        return self._pot

    @property
    def initial_data(self):
        if self._initial_data:
            return self._initial_data
        self._initial_data = extract.initial_data(self.watch_html)
        return self._initial_data

    @property
    def streaming_data(self):
        """Return streamingData from video info."""

        # List of YouTube error video IDs
        invalid_id_list = ['aQvGIIdgFDM']

        # If my previously valid video_info doesn't have the streamingData,
        #   or it is an invalid video,
        #   try to get a new video_info with a different client.
        if 'streamingData' not in self.vid_info or self.vid_info['videoDetails']['videoId'] in invalid_id_list:
            original_client = self.client

            # for each fallback client set, revert videodata, and run check_availability, which
            #   will try to get a new video_info with a different client.
            #   if it fails try the next fallback client, and so on.
            # If none of the clients have valid streamingData, raise an exception.
            for client in self.fallback_clients:
                self.client = client
                self.vid_info = None
                try:
                    self.check_availability()
                except Exception as e:
                    continue
                if 'streamingData' in self.vid_info:
                    break
            if 'streamingData' not in self.vid_info:
                raise exceptions.UnknownVideoError(video_id=self.video_id,
                                                   developer_message=f'Streaming data is missing, '
                                                                     f'original client: {original_client}, '
                                                                     f'fallback clients: {self.fallback_clients}')

        return self.vid_info['streamingData']

    @property
    def fmt_streams(self):
        """Returns a list of streams if they have been initialized.

        If the streams have not been initialized, finds all relevant
        streams and initializes them.
        """
        self.check_availability()
        if self._fmt_streams:
            return self._fmt_streams

        self._fmt_streams = []

        stream_manifest = extract.apply_descrambler(self.streaming_data)
        inner_tube = InnerTube(self.client)
        if self.po_token:
            extract.apply_po_token(stream_manifest, self.vid_info, self.po_token)

        if inner_tube.require_js_player:
            # If the cached js doesn't work, try fetching a new js file
            # https://github.com/pytube/pytube/issues/1054
            try:
                extract.apply_signature(stream_manifest, self.vid_info, self.js, self.js_url)
            except exceptions.ExtractError:
                # To force an update to the js file, we clear the cache and retry
                self._js = None
                self._js_url = None
                pytubefix.__js__ = None
                pytubefix.__js_url__ = None
                extract.apply_signature(stream_manifest, self.vid_info, self.js, self.js_url)

        # build instances of :class:`Stream <Stream>`
        # Initialize stream objects
        for stream in stream_manifest:
            video = Stream(
                stream=stream,
                monostate=self.stream_monostate,
                po_token=self.po_token,
                video_playback_ustreamer_config=self.video_playback_ustreamer_config
            )
            self._fmt_streams.append(video)

        self.stream_monostate.title = self.title
        self.stream_monostate.duration = self.length

        return self._fmt_streams

    def check_availability(self):
        """Check whether the video is available.

        Raises different exceptions based on why the video is unavailable,
        otherwise does nothing.
        """
        status, messages = extract.playability_status(self.vid_info)

        if InnerTube(self.client).require_po_token and not self.po_token:
            logger.warning(f"The {self.client} client requires PoToken to obtain functional streams, "
                           f"See more details at https://github.com/JuanBindez/pytubefix/pull/209")

        for reason in messages:
            if status == 'UNPLAYABLE':
                if reason == (
                        'Join this channel to get access to members-only content '
                        'like this video, and other exclusive perks.'
                ):
                    raise exceptions.MembersOnly(video_id=self.video_id)

                elif 'Join this channel to get access to members-only content and other exclusive perks.' in reason:
                    raise exceptions.MembersOnly(video_id=self.video_id)

                elif reason == 'This live stream recording is not available.':
                    raise exceptions.RecordingUnavailable(video_id=self.video_id)

                elif reason == (
                        'Sorry, something is wrong. This video may be inappropriate for some users. '
                        'Sign in to your primary account to confirm your age.'
                ):
                    raise exceptions.AgeCheckRequiredAccountError(video_id=self.video_id)
                elif reason == ('The uploader has not made this video available in your country'):
                    raise exceptions.VideoRegionBlocked(video_id=self.video_id)
                elif "blocked it in your country on copyright grounds" in reason:
                    raise exceptions.VideoBlockedByCopyright(video_id=self.video_id, reason=reason)
                else:
                    raise exceptions.VideoUnavailable(video_id=self.video_id)

            elif status == 'LOGIN_REQUIRED':
                if reason == (
                        'Sign in to confirm your age'
                ):
                    raise exceptions.AgeRestrictedError(video_id=self.video_id)
                elif reason == (
                        'Sign in to confirm you’re not a bot'
                ):
                    raise exceptions.BotDetection(video_id=self.video_id)
                else:
                    raise exceptions.LoginRequired(video_id=self.video_id, reason=reason)

            elif status == 'AGE_CHECK_REQUIRED':
                if self.use_oauth:
                    self.age_check()
                else:
                    raise exceptions.AgeCheckRequiredError(video_id=self.video_id)

            elif status == 'LIVE_STREAM_OFFLINE':
                raise exceptions.LiveStreamOffline(video_id=self.video_id, reason=reason)

            elif status == 'ERROR':
                if reason == 'Video unavailable':
                    raise exceptions.VideoUnavailable(video_id=self.video_id)
                elif reason == 'This video is private':
                    raise exceptions.VideoPrivate(video_id=self.video_id)
                elif reason == 'This video is unavailable':
                    raise exceptions.VideoUnavailable(video_id=self.video_id)
                elif reason == 'This video has been removed by the uploader':
                    raise exceptions.VideoRemovedByUploader(video_id=self.video_id, reason=reason)
                elif reason == 'This video is no longer available because the YouTube account associated with this video has been terminated.':
                    raise exceptions.AccountTerminated(video_id=self.video_id, reason=reason)
                elif reason == "This video has been removed for violating YouTube's Community Guidelines":
                    raise exceptions.VideoRemovedByYouTubeForViolatingTOS(video_id=self.video_id, reason=reason)
                else:
                    raise exceptions.UnknownVideoError(video_id=self.video_id, status=status, reason=reason, developer_message=f'Unknown reason type for Error status')
            elif status == 'LIVE_STREAM':
                raise exceptions.LiveStreamError(video_id=self.video_id)
            elif status == 'OK':
                if reason == 'This live event has ended.':
                    raise exceptions.LiveStreamEnded(video_id=self.video_id, reason=reason)
                else:
                    raise exceptions.UnknownVideoError(video_id=self.video_id, status=status, reason=reason, developer_message=f'Unknown video status')
            elif status is None:
                pass
            else:
                raise exceptions.UnknownVideoError(video_id=self.video_id, status=status, reason=reason, developer_message=f'Unknown video status')

    @property
    def signature_timestamp(self) -> dict:
        """WEB clients need to be signed with a signature timestamp.

        The signature is found inside the player's base.js.

        :rtype: Dict
        """
        if not self._signature_timestamp:
            self._signature_timestamp = {
                'playbackContext': {
                    'contentPlaybackContext': {
                        'signatureTimestamp': extract.signature_timestamp(self.js)
                    }
                }
            }
        return self._signature_timestamp

    @property
    def video_playback_ustreamer_config(self):
        return self.vid_info[
            'playerConfig'][
            'mediaCommonConfig'][
            'mediaUstreamerRequestConfig'][
            'videoPlaybackUstreamerConfig']

    @property
    def server_abr_streaming_url(self):
        """
        Extract the url for abr server and decrypt the `n` parameter
        """
        try:
            url = self.vid_info[
                'streamingData'][
                'serverAbrStreamingUrl']
            stream_manifest = [{"url": url}]
            extract.apply_signature(stream_manifest, vid_info=self.vid_info, js=self.js, url_js=self.js_url)
            return stream_manifest[0]["url"]
        except Exception:
            return None

    @property
    def vid_info(self):
        """Parse the raw vid info and return the parsed result.

        :rtype: Dict[Any, Any]
        """
        if self._vid_info:
            return self._vid_info

        self._vid_info = self.vid_info_client()

        return self._vid_info

    @vid_info.setter
    def vid_info(self, value):
        self._vid_info = value

    def vid_info_client(self, optional_client=None):

        if optional_client is None:
            if self._vid_info:
                return self._vid_info
            optional_client = self.client

        def call_innertube(optional_client):
            innertube = InnerTube(
                client=optional_client,
                use_oauth=self.use_oauth,
                allow_cache=self.allow_oauth_cache,
                token_file=self.token_file,
                oauth_verifier=self.oauth_verifier,
                use_po_token=self.use_po_token,
                po_token_verifier=self.po_token_verifier
            )
            if innertube.require_js_player:
                innertube.innertube_context.update(self.signature_timestamp)

            # Automatically generates a poToken
            if innertube.require_po_token and not self.use_po_token:
                logger.debug(f"The {optional_client} client requires poToken to obtain functional streams")
                logger.debug("Automatically generating poToken")
                innertube.insert_visitor_data(visitor_data=self.visitor_data)
            elif not self.use_po_token:
                # from 01/22/2025 all clients must send the visitorData in the API request
                innertube.insert_visitor_data(visitor_data=self.visitor_data)

            response = innertube.player(self.video_id)

            # Retrieves the sent poToken
            if self.use_po_token or innertube.require_po_token:
                self.po_token = innertube.access_po_token or self.pot
            return response

        innertube_response = call_innertube(optional_client)
        for client in self.fallback_clients:
            # Some clients are unable to access certain types of videos
            # If the video is unavailable for the current client, attempts will be made with fallback clients
            playability_status = innertube_response['playabilityStatus']
            if playability_status['status'] == 'UNPLAYABLE' and 'reason' in playability_status and playability_status['reason'] == 'This video is not available':
                logger.warning(f"{self.client} client returned: This video is not available")
                self.client = client
                logger.warning(f"Switching to client: {client}")
                innertube_response = call_innertube(client)
            else:
                break

        if not innertube_response:
            raise pytubefix.exceptions.InnerTubeResponseError(self.video_id, self.client)

        return innertube_response

    @property
    def vid_details(self):
        """Parse the raw vid details and return the parsed result.

        The official player sends a request to the `next` endpoint to obtain some details of the video.

        :rtype: Dict[Any, Any]
        """
        if self._vid_details:
            return self._vid_details

        innertube = InnerTube(
            client='TV' if self.use_oauth else 'WEB',
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache,
            token_file=self.token_file,
            oauth_verifier=self.oauth_verifier,
            use_po_token=self.use_po_token,
            po_token_verifier=self.po_token_verifier
        )
        innertube_response = innertube.next(self.video_id)
        self._vid_details = innertube_response
        return self._vid_details

    @vid_details.setter
    def vid_details(self, value):
        self._vid_details = value

    def age_check(self):
        """If the video has any age restrictions, you must confirm that you wish to continue.

        Originally the WEB client was used, but with the implementation of PoToken we switched to MWEB.
        """

        self.client = 'TV'
        innertube = InnerTube(
            client=self.client,
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache,
            token_file=self.token_file,
            oauth_verifier=self.oauth_verifier,
            use_po_token=self.use_po_token,
            po_token_verifier=self.po_token_verifier
        )

        if innertube.require_js_player:
            innertube.innertube_context.update(self.signature_timestamp)

        innertube.verify_age(self.video_id)

        innertube_response = innertube.player(self.video_id)

        playability_status = innertube_response['playabilityStatus'].get('status', None)

        # If we still can't access the video, raise an exception
        if playability_status != 'OK':
            if playability_status == 'UNPLAYABLE':
                raise exceptions.AgeCheckRequiredAccountError(self.video_id)
            else:
                raise exceptions.AgeCheckRequiredError(self.video_id)

        self._vid_info = innertube_response

    @property
    def caption_tracks(self) -> List[pytubefix.Caption]:
        """Get a list of :class:`Caption <Caption>`.

        :rtype: List[Caption]
        """

        innertube_response = InnerTube(
            client='WEB' if not self.use_oauth else self.client,
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache,
            token_file=self.token_file,
            oauth_verifier=self.oauth_verifier,
            use_po_token=self.use_po_token,
            po_token_verifier=self.po_token_verifier
        ).player(self.video_id)

        raw_tracks = (
            innertube_response.get("captions", {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        )
        return [pytubefix.Caption(track) for track in raw_tracks]

    @property
    def captions(self) -> pytubefix.CaptionQuery:
        """Interface to query caption tracks.

        :rtype: :class:`CaptionQuery <CaptionQuery>`.
        """
        return pytubefix.CaptionQuery(self.caption_tracks)

    @property
    def chapters(self) -> List[pytubefix.Chapter]:
        """Get a list of :class:`Chapter <Chapter>`.

        :rtype: List[Chapter]
        """
        try:
            chapters_data = []
            markers_map = self.initial_data['playerOverlays']['playerOverlayRenderer'][
                'decoratedPlayerBarRenderer']['decoratedPlayerBarRenderer']['playerBar'][
                'multiMarkersPlayerBarRenderer']['markersMap']
            for marker in markers_map:
                if marker['key'].upper() == 'DESCRIPTION_CHAPTERS' or marker['key'].upper() == 'AUTO_CHAPTERS':
                    chapters_data = marker['value']['chapters']
                    break
        except (KeyError, IndexError):
            return []

        result: List[pytubefix.Chapter] = []

        for i, chapter_data in enumerate(chapters_data):
            chapter_start = int(
                chapter_data['chapterRenderer']['timeRangeStartMillis'] / 1000
            )

            if i == len(chapters_data) - 1:
                chapter_end = self.length
            else:
                chapter_end = int(
                    chapters_data[i + 1]['chapterRenderer']['timeRangeStartMillis'] / 1000
                )

            result.append(pytubefix.Chapter(chapter_data, chapter_end - chapter_start))

        return result

    @property
    def key_moments(self) -> List[pytubefix.KeyMoment]:
        """Get a list of :class:`KeyMoment <KeyMoment>`.

        :rtype: List[KeyMoment]
        """
        try:
            mutations = self.initial_data['frameworkUpdates']['entityBatchUpdate']['mutations']
            found = False
            for mutation in mutations:
                if mutation.get('payload', {}).get('macroMarkersListEntity', {}).get('markersList', {}).get(
                        'markerType') == "MARKER_TYPE_TIMESTAMPS":
                    key_moments_data = mutation['payload']['macroMarkersListEntity']['markersList']['markers']
                    found = True
                    break

            if not found:
                return []
        except (KeyError, IndexError):
            return []

        result: List[pytubefix.KeyMoment] = []

        for i, key_moment_data in enumerate(key_moments_data):
            key_moment_start = int(key_moment_data['startMillis']) // 1000

            if i == len(key_moments_data) - 1:
                key_moment_end = self.length
            else:
                key_moment_end = int(key_moments_data[i + 1]['startMillis']) // 1000

            result.append(pytubefix.KeyMoment(key_moment_data, key_moment_end - key_moment_start))

        return result

    @property
    def replayed_heatmap(self) -> List[Dict[str, float]]:
        """Get a list of : `Dict<str, float>`.

        :rtype: List[Dict[str, float]]
        """
        try:
            mutations = self.initial_data['frameworkUpdates']['entityBatchUpdate']['mutations']
            found = False
            for mutation in mutations:
                if mutation.get('payload', {}).get('macroMarkersListEntity', {}).get('markersList', {}).get(
                        'markerType') == "MARKER_TYPE_HEATMAP":
                    heatmaps_data = mutation['payload']['macroMarkersListEntity']['markersList']['markers']
                    found = True
                    break

            if not found:
                return []
        except (KeyError, IndexError):
            return []

        result: List[Dict[str, float]] = []

        for heatmap_data in heatmaps_data:
            heatmap_start = int(heatmap_data['startMillis']) / 1000
            duration = int(heatmap_data['durationMillis']) / 1000

            norm_intensity = float(heatmap_data['intensityScoreNormalized'])

            result.append({
                "start_seconds": heatmap_start,
                "duration": duration,
                "norm_intensity": norm_intensity
            })

        return result

    @property
    def streams(self) -> StreamQuery:
        """Interface to query both adaptive (DASH) and progressive streams.

        :rtype: :class:`StreamQuery <StreamQuery>`.
        """
        self.check_availability()
        return StreamQuery(self.fmt_streams)

    @property
    def thumbnail_url(self) -> str:
        """Get the thumbnail url image.

        :rtype: str
        """
        thumbnail_details = (
            self.vid_info.get("videoDetails", {})
            .get("thumbnail", {})
            .get("thumbnails")
        )
        if thumbnail_details:
            thumbnail_details = thumbnail_details[-1]  # last item has max size
            return thumbnail_details["url"]

        return f"https://img.youtube.com/vi/{self.video_id}/maxresdefault.jpg"

    @property
    def publish_date(self):
        """Get the publish date.

        :rtype: datetime
        """
        if self._publish_date:
            return self._publish_date
        self._publish_date = extract.publish_date(self.watch_html)
        return self._publish_date

    @publish_date.setter
    def publish_date(self, value):
        """Sets the publish date."""
        self._publish_date = value

    def vid_engagement_items(self) -> list:
        for i in range(1,4):
            try:
                return self.vid_details['engagementPanels'][i]['engagementPanelSectionListRenderer']['content']['structuredDescriptionContentRenderer']['items']
            except KeyError as e:
                continue
        raise exceptions.PytubeFixError(
            (
                f'Exception while accessing engagementPanel of {self.watch_url} in {self.client} client.'
            )
        ) from e

    @property
    def title(self) -> str:
        """Get the video title.

        :rtype: str
        """
        self._author = self.vid_info.get("videoDetails", {}).get(
            "author", "unknown"
        )

        if self._title:
            return self._title

        if self.use_oauth == True:
            self._title = self.vid_engagement_items()[0]['videoDescriptionHeaderRenderer']['title']['runs'][0]['text']

        try:
            # Some clients may not return the title in the `player` endpoint,
            # so if it is not found we will look for it in the `next` endpoint
            if 'title' in self.vid_info['videoDetails']:
                self._title = self.vid_info['videoDetails']['title']
                logger.debug('Found title in vid_info')
            else:
                if 'singleColumnWatchNextResults' in self.vid_details['contents']:
                    contents = self.vid_details['contents'][
                        'singleColumnWatchNextResults'][
                        'results'][
                        'results'][
                        'contents'][0][
                        'itemSectionRenderer'][
                        'contents'][0]

                    if 'videoMetadataRenderer' in contents:
                        self._title = contents['videoMetadataRenderer']['title']['runs'][0]['text']
                    else:
                        # JSON tree for titles in videos available on YouTube music
                        self._title = contents['musicWatchMetadataRenderer']['title']['simpleText']

                # The type of video with this structure is not yet known.
                # First reported in: https://github.com/JuanBindez/pytubefix/issues/351
                elif 'twoColumnWatchNextResults' in self.vid_details['contents']:
                    contents = self.vid_details['contents'][
                        'twoColumnWatchNextResults'][
                        'results'][
                        'results'][
                        'contents']
                    for videoPrimaryInfoRenderer in contents:
                        if 'videoPrimaryInfoRenderer' in videoPrimaryInfoRenderer:
                            self._title = videoPrimaryInfoRenderer[
                                'videoPrimaryInfoRenderer'][
                                'title'][
                                'runs'][0][
                                'text']
                            break

        except KeyError as e:
            # Check_availability will raise the correct exception in most cases
            #  if it doesn't, ask for a report.
            self.check_availability()
            raise exceptions.PytubeFixError(
                (
                    f'Exception while accessing title of {self.watch_url} in {self.client} client.'
                )
            ) from e

        return self._title

    @title.setter
    def title(self, value):
        """Sets the title value."""
        self._title = value

    @property
    def original_title(self):

        if self._original_title:
            return self._original_title

        try:
            if self.client == 'WEB':
                self._original_title = self.vid_info['microformat']['playerMicroformatRenderer']['title']['simpleText']
            else:
                self._original_title = self.vid_info_client("WEB")['microformat']['playerMicroformatRenderer']['title']['simpleText']
        except KeyError as e:
            # Check_availability will raise the correct exception in most cases
            #  if it doesn't, ask for a report.
            self.check_availability()
            raise exceptions.PytubeFixError(
                (
                    f'Exception while accessing original title of {self.watch_url} in {self.client} client.'
                )
            ) from e

        return self._original_title

    def vid_details_content(self) -> list:
        try:
            contents = self.vid_details['contents']
            results = contents[list(contents.keys())[0]]['results']['results']['contents']
        except Exception as e:
            raise exceptions.PyTubeFixError(
                    (
                        f'Exception: accessing vid_details_content of {self.watch_url} in {self.client} and trying to use key in {contents.keys()}'
                    )
            ) from e
        return results


    @property
    def description(self) -> str:
        """Get the video description.

        :rtype: str
        """
        description = self.vid_info.get("videoDetails", {}).get("shortDescription")

        if self.use_oauth == True:
            description = self.vid_engagement_items()[2]['expandableVideoDescriptionBodyRenderer']['descriptionBodyText']['runs'][0]['text']

        if description is None:
            # TV client structure
            results = self.vid_details_content()
            for c in results:
                if 'videoSecondaryInfoRenderer' in c:
                    description = c['videoSecondaryInfoRenderer']['attributedDescription']['content']
                    break
        return description

    @property
    def rating(self) -> float:
        """Get the video average rating.

        :rtype: float

        """
        return self.vid_info.get("videoDetails", {}).get("averageRating")

    @property
    def length(self) -> int:
        """Get the video length in seconds.

        :rtype: int
        """
        self.check_availability()
        return int(self.vid_info.get('videoDetails', {}).get('lengthSeconds'))

    @property
    def views(self) -> int:
        """Get the number of the times the video has been viewed.

        :rtype: int
        """
        view = int(self.vid_info.get("videoDetails", {}).get("viewCount", "0"))

        if self.use_oauth == True:
            simple_text = self.vid_engagement_items()[0]['videoDescriptionHeaderRenderer']['views']['simpleText']
            view = int(''.join([char for char in simple_text if char.isdigit()]))

        if not view:
            results = self.vid_details_content()
            for c in results:
                if 'videoPrimaryInfoRenderer' in c:
                    simple_text = c['videoPrimaryInfoRenderer'][
                        'viewCount'][
                        'videoViewCountRenderer'][
                        'viewCount'][
                        'simpleText']
                    view = int(''.join([char for char in simple_text if char.isdigit()]))
                    break
        return view

    @property
    def author(self) -> str:
        """Get the video author.
        :rtype: str
        """

        # TODO: Implement correctly for the TV client
        _author = self.vid_info.get("videoDetails", {}).get("author", "unknown")

        if self.use_oauth == True:
            _author = self.vid_engagement_items()[0]['videoDescriptionHeaderRenderer']['channel']['simpleText']


        self._author = _author
        return self._author

    @author.setter
    def author(self, value):
        """Set the video author."""
        self._author = value

    @property
    def keywords(self) -> List[str]:
        """Get the video keywords.

        :rtype: List[str]
        """
        return self.vid_info.get('videoDetails', {}).get('keywords', [])

    @property
    def channel_id(self) -> str:
        """Get the video poster's channel id.

        :rtype: str
        """
        return self.vid_info.get('videoDetails', {}).get('channelId', None)

    @property
    def channel_url(self) -> str:
        """Construct the channel url for the video's poster from the channel id.

        :rtype: str
        """
        return f'https://www.youtube.com/channel/{self.channel_id}'

    @property
    def likes(self):
        """Get the video likes

        :rtype: str
        """
        
        if self.use_oauth == True:
            return self.vid_engagement_items()[0]['videoDescriptionHeaderRenderer']['factoid'][0]['factoidRenderer']['value']['simpleText']

        try:
            likes = '0'
            contents = self.vid_details_content()
            for c in contents:
                if 'videoPrimaryInfoRenderer' in c:
                    likes = c['videoPrimaryInfoRenderer'][
                    'videoActions'][
                    'menuRenderer'][
                    'topLevelButtons'][
                    0][
                    'segmentedLikeDislikeButtonViewModel'][
                    'likeButtonViewModel'][
                    'likeButtonViewModel'][
                    'toggleButtonViewModel'][
                    'toggleButtonViewModel'][
                    'defaultButtonViewModel'][
                    'buttonViewModel'][
                    'accessibilityText']
                    break

            return ''.join([char for char in likes if char.isdigit()])
        except (KeyError, IndexError) as e:
            raise exceptions.PyTubeFixError(
                    (
                        f'Exception: accessing likes of {self.watch_url} in {self.client}'
                    )
            ) from e
        return None

    @property
    def metadata(self) -> Optional[YouTubeMetadata]:
        """Get the metadata for the video.

        :rtype: YouTubeMetadata
        """
        if not self._metadata:
            self._metadata = extract.metadata(
                self.initial_data)  # Creating the metadata
        return self._metadata

    def register_on_progress_callback(self, func: Callable[[Any, bytes, int], None]):
        """Register a download progress callback function post initialization.

        :param callable func:
            A callback function that takes ``stream``, ``chunk``,
             and ``bytes_remaining`` as parameters.

        :rtype: None

        """
        self.stream_monostate.on_progress = func

    def register_on_complete_callback(self, func: Callable[[Any, Optional[str]], None]):
        """Register a download complete callback function post initialization.

        :param callable func:
            A callback function that takes ``stream`` and  ``file_path``.

        :rtype: None

        """
        self.stream_monostate.on_complete = func

    @staticmethod
    def from_id(video_id: str) -> "YouTube":
        """Construct a :class:`YouTube <YouTube>` object from a video id.

        :param str video_id:
            The video id of the YouTube video.

        :rtype: :class:`YouTube <YouTube>`
        """
        return YouTube(f"https://www.youtube.com/watch?v={video_id}")
