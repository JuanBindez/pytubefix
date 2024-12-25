# MIT License
#
# Copyright (c) 2023 - 2024 Juan Bindez <juanbindez780@gmail.com>
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
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytubefix
import pytubefix.exceptions as exceptions
from pytubefix import extract, request
from pytubefix import Stream, StreamQuery
from pytubefix.helpers import install_proxy
from pytubefix.innertube import InnerTube
from pytubefix.metadata import YouTubeMetadata
from pytubefix.monostate import Monostate

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
        :param bool use_po_token:
            (Optional) Prompt the user to use the proof of origin token on YouTube.
            It must be sent with the API along with the linked visitorData and
            then passed as a `po_token` query parameter to affected clients.
            If allow_oauth_cache is set to True, the user should only be prompted once.
            (Do not use together with `use_oauth=True`)
        :param Callable po_token_verifier:
            (Optional) Verified used to obtain the visitorData and po_token.
            The verifier will return the visitorData and po_token respectively.
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

        self.client = 'WEB' if use_po_token else client

        # oauth can only be used by the TV and TV_EMBED client.
        self.client = 'TV' if use_oauth else self.client

        self.fallback_clients = ['MWEB', 'IOS', 'TV', 'WEB']

        self._signature_timestamp: dict = {}

        # Shared between all instances of `Stream` (Borg pattern).
        self.stream_monostate = Monostate(
            on_progress=on_progress_callback, on_complete=on_complete_callback
        )

        if proxies:
            install_proxy(proxies)

        self._author = None
        self._title = None
        self._publish_date = None

        self.use_oauth = use_oauth
        self.allow_oauth_cache = allow_oauth_cache
        self.token_file = token_file
        self.oauth_verifier = oauth_verifier

        self.use_po_token = use_po_token
        self.po_token_verifier = po_token_verifier

        self.po_token = None

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

        if self.use_po_token:
            extract.apply_po_token(stream_manifest, self.vid_info, self.po_token)

        if InnerTube(self.client).require_js_player:
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

                elif reason == 'This live stream recording is not available.':
                    raise exceptions.RecordingUnavailable(video_id=self.video_id)

                elif reason == (
                        'Sorry, something is wrong. This video may be inappropriate for some users. '
                        'Sign in to your primary account to confirm your age.'
                ):
                    raise exceptions.AgeCheckRequiredAccountError(video_id=self.video_id)
                elif reason == (
                        'The uploader has not made this video available in your country'
                ):
                    raise exceptions.VideoRegionBlocked(video_id=self.video_id)
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
                    raise exceptions.VideoUnavailable(video_id=self.video_id)
                elif reason == 'This video is no longer available because the YouTube account associated with this video has been terminated.':
                    raise exceptions.VideoUnavailable(video_id=self.video_id)
                else:
                    raise exceptions.UnknownVideoError(video_id=self.video_id, status=status, reason=reason, developer_message=f'Unknown reason type for Error status')
            elif status == 'LIVE_STREAM':
                raise exceptions.LiveStreamError(video_id=self.video_id)
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
    def vid_info(self):
        """Parse the raw vid info and return the parsed result.

        :rtype: Dict[Any, Any]
        """
        if self._vid_info:
            return self._vid_info

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

        innertube_response = innertube.player(self.video_id)
        if self.use_po_token:
            self.po_token = innertube.access_po_token
        self._vid_info = innertube_response
        return self._vid_info

    @vid_info.setter
    def vid_info(self, value):
        self._vid_info = value

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

        self.client = 'MWEB'
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

        innertube_response = InnerTube(client='WEB').player(self.video_id)

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
                if marker['key'].upper() == 'DESCRIPTION_CHAPTERS':
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
                    self._title = self.vid_details['contents'][
                        'twoColumnWatchNextResults'][
                        'results'][
                        'results'][
                        'contents'][0][
                        'videoPrimaryInfoRenderer'][
                        'title'][
                        'runs'][0][
                        'text']

                logger.debug('Found title in vid_details')
        except KeyError as e:
            # Check_availability will raise the correct exception in most cases
            #  if it doesn't, ask for a report.
            self.check_availability()
            raise exceptions.PytubeFixError(
                (
                    f'Exception while accessing title of {self.watch_url}. '
                    'Please file a bug report at https://github.com/JuanBindez/pytubefix'
                )
            ) from e

        return self._title

    @title.setter
    def title(self, value):
        """Sets the title value."""
        self._title = value

    @property
    def description(self) -> str:
        """Get the video description.

        :rtype: str
        """
        return self.vid_info.get("videoDetails", {}).get("shortDescription")

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
        return int(self.vid_info.get('videoDetails', {}).get('lengthSeconds'))

    @property
    def views(self) -> int:
        """Get the number of the times the video has been viewed.

        :rtype: int
        """
        return int(self.vid_info.get("videoDetails", {}).get("viewCount"))

    @property
    def author(self) -> str:
        """Get the video author.
        :rtype: str
        """
        if self._author:
            return self._author
        self._author = self.vid_info.get("videoDetails", {}).get(
            "author", "unknown"
        )
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
        try:
            return self.vid_details[
                'contents'][
                'twoColumnWatchNextResults'][
                'results'][
                'results'][
                'contents'][
                0][
                'videoPrimaryInfoRenderer'][
                'videoActions'][
                'menuRenderer'][
                'topLevelButtons'][
                0][
                'segmentedLikeDislikeButtonViewModel'][
                'likeCountEntity'][
                'likeCountIfLikedNumber']
        except (KeyError, IndexError):
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
