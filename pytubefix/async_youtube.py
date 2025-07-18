import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytubefix
import pytubefix.exceptions as exceptions
from pytubefix import extract
from pytubefix import Stream, StreamQuery
from pytubefix.helpers import install_proxy
from pytubefix.innertube import InnerTube
from pytubefix.metadata import YouTubeMetadata
from pytubefix.monostate import Monostate
from pytubefix.botGuard import bot_guard

from pytubefix.async_http_client import AsyncHTTPClient

logger = logging.getLogger(__name__)

class AsyncYouTube:
    """Asynchronous YouTube interface using AsyncHTTPClient (production ready)."""

    def __init__(
        self,
        url: str,
        client: str = InnerTube().client_name,
        http_client: Optional[AsyncHTTPClient] = None,
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
        self._js: Optional[str] = None
        self._js_url: Optional[str] = None
        self._vid_info: Optional[Dict] = None
        self._vid_details: Optional[Dict] = None
        self._watch_html: Optional[str] = None
        self._embed_html: Optional[str] = None
        self._player_config_args: Optional[Dict] = None
        self._age_restricted: Optional[bool] = None
        self._fmt_streams: Optional[List[Stream]] = None
        self._initial_data = None
        self._metadata: Optional[YouTubeMetadata] = None

        self.video_id = extract.video_id(url)
        self.watch_url = f"https://youtube.com/watch?v={self.video_id}"
        self.embed_url = f"https://www.youtube.com/embed/{self.video_id}"

        self.client = 'WEB' if use_po_token else client
        self.client = 'TV' if use_oauth else self.client
        self.fallback_clients = ['TV', 'IOS']
        self._signature_timestamp: dict = {}
        self._visitor_data = None
        self.stream_monostate = Monostate(
            on_progress=on_progress_callback, on_complete=on_complete_callback, youtube=self
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
        self._pot = None

        # AsyncHTTPClient instance
        self.http_client = http_client or AsyncHTTPClient()

    def __repr__(self):
        return f'<pytubefix.async_main.AsyncYouTube object: videoId={self.video_id}>'

    def __eq__(self, o: object) -> bool:
        return type(o) == type(self) and o.watch_url == self.watch_url

    # ----------- ASYNC NETWORK METHODS --------------#
    async def get_watch_html(self):
        if self._watch_html:
            return self._watch_html
        self._watch_html = await self.http_client.get(self.watch_url)
        return self._watch_html

    async def get_embed_html(self):
        if self._embed_html:
            return self._embed_html
        self._embed_html = await self.http_client.get(self.embed_url)
        return self._embed_html
    
    async def get_age_restricted(self):
        if self._age_restricted is not None:
            return self._age_restricted
        self._age_restricted = extract.is_age_restricted(await self.get_watch_html())
        return self._age_restricted

    async def get_js_url(self):
        if self._js_url:
            return self._js_url
        if await self.get_age_restricted():
            self._js_url = extract.js_url(await self.get_embed_html())
        else:
            self._js_url = extract.js_url(await self.get_watch_html())
        return self._js_url

    async def get_js(self):
        if self._js:
            return self._js
        js_url = await self.get_js_url()
        if pytubefix.__js_url__ != js_url:
            self._js = await self.http_client.get(js_url)
            pytubefix.__js__ = self._js
            pytubefix.__js_url__ = js_url
        else:
            self._js = pytubefix.__js__
        return self._js
    
    async def get_initial_data(self):
        if self._initial_data:
            return self._initial_data
        self._initial_data = extract.initial_data(await self.get_watch_html())
        return self._initial_data

    async def get_visitor_data(self):
        if self._visitor_data:
            return self._visitor_data

        try:
            self._visitor_data = extract.visitor_data(str((await self.get_initial_data())['responseContext']))
            return self._visitor_data
        except (KeyError, pytubefix.exceptions.RegexMatchError):
            pass
        innertube_response = InnerTube('WEB').player(self.video_id)
        try:
            self._visitor_data = innertube_response['responseContext']['visitorData']
        except KeyError:
            self._visitor_data = innertube_response['responseContext']['serviceTrackingParams'][0]['params'][6]['value']
        return self._visitor_data
    
    async def get_vid_info(self):
        if self._vid_info:
            return self._vid_info

        async def call_innertube():
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
                innertube.innertube_context.update(await self.get_signature_timestamp())

            if innertube.require_po_token and not self.use_po_token:
                innertube.insert_po_token(visitor_data=await self.get_visitor_data(), po_token=await self.get_pot())
            elif not self.use_po_token:
                innertube.insert_visitor_data(visitor_data=await self.get_visitor_data())
            response = innertube.player(self.video_id)
            if self.use_po_token or innertube.require_po_token:
                self.po_token = innertube.access_po_token or await self.get_pot()
            return response

        innertube_response = await call_innertube()
        for client in self.fallback_clients:
            playability_status = innertube_response['playabilityStatus']
            if playability_status['status'] == 'UNPLAYABLE' and 'reason' in playability_status and playability_status['reason'] == 'This video is not available':
                self.client = client
                innertube_response = await call_innertube()
            else:
                break

        self._vid_info = innertube_response
        if not self._vid_info:
            raise pytubefix.exceptions.InnerTubeResponseError(self.video_id, self.client)
        return self._vid_info
    
    async def get_vid_details(self):
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

    async def get_signature_timestamp(self):
        if not self._signature_timestamp:
            self._signature_timestamp = {
                'playbackContext': {
                    'contentPlaybackContext': {
                        'signatureTimestamp': extract.signature_timestamp(await self.get_js())
                    }
                }
            }
        return self._signature_timestamp
    
    async def get_streaming_data(self):
        if not self._vid_info:
            await self.get_vid_info()
        invalid_id_list = ['aQvGIIdgFDM']
        if 'streamingData' not in self._vid_info or self._vid_info['videoDetails']['videoId'] in invalid_id_list:
            original_client = self.client
            for client in self.fallback_clients:
                self.client = client
                self._vid_info = None
                try:
                    await self.check_availability()
                except Exception:
                    continue
                if 'streamingData' in self._vid_info:
                    break
            if 'streamingData' not in self._vid_info:
                raise exceptions.UnknownVideoError(video_id=self.video_id, developer_message=f'Streaming data is missing, original client: {original_client}, fallback clients: {self.fallback_clients}')
        return self._vid_info['streamingData']
    
    async def check_availability(self):
        status, messages = extract.playability_status(await self.get_vid_info())
        if InnerTube(self.client).require_po_token and not self.po_token:
            logger.warning(f"The {self.client} client requires PoToken to obtain functional streams")
        for reason in messages:
            if status == 'UNPLAYABLE':
                if reason == ('Join this channel to get access to members-only content like this video, and other exclusive perks.'):
                    raise exceptions.MembersOnly(video_id=self.video_id)
                elif 'Join this channel to get access to members-only content and other exclusive perks.' in reason:
                    raise exceptions.MembersOnly(video_id=self.video_id)
                elif reason == 'This live stream recording is not available.':
                    raise exceptions.RecordingUnavailable(video_id=self.video_id)
                elif reason == ('Sorry, something is wrong. This video may be inappropriate for some users. Sign in to your primary account to confirm your age.'):
                    raise exceptions.AgeCheckRequiredAccountError(video_id=self.video_id)
                elif reason == ('The uploader has not made this video available in your country'):
                    raise exceptions.VideoRegionBlocked(video_id=self.video_id)
                else:
                    raise exceptions.VideoUnavailable(video_id=self.video_id)
            elif status == 'LOGIN_REQUIRED':
                if reason == ('Sign in to confirm your age'):
                    raise exceptions.AgeRestrictedError(video_id=self.video_id)
                elif reason == ('Sign in to confirm you’re not a bot'):
                    raise exceptions.BotDetection(video_id=self.video_id)
                else:
                    raise exceptions.LoginRequired(video_id=self.video_id, reason=reason)
            elif status == 'AGE_CHECK_REQUIRED':
                if self.use_oauth:
                    await self.age_check()
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

    #--------------Methods-----------#
    async def get_fmt_streams(self):
        await self.check_availability()  # دالة async
        if self._fmt_streams:
            return self._fmt_streams
    
        self._fmt_streams = []
    
        # Async replacements
        streaming_data = await self.get_streaming_data()
        stream_manifest = extract.apply_descrambler(streaming_data)
        inner_tube = InnerTube(self.client)
    
        if self.po_token:
            vid_info = await self.get_vid_info()
            extract.apply_po_token(stream_manifest, vid_info, self.po_token)
    
        if inner_tube.require_js_player:
    
            try:
                vid_info = await self.get_vid_info()
                js = await self.get_js()
                js_url = await self.get_js_url()
                extract.apply_signature(stream_manifest, vid_info, js, js_url)
            except exceptions.ExtractError:
                # clear js cache and retry
                self._js = None
                self._js_url = None
                pytubefix.__js__ = None
                pytubefix.__js_url__ = None
                vid_info = await self.get_vid_info()
                js = await self.get_js()
                js_url = await self.get_js_url()
                extract.apply_signature(stream_manifest, vid_info, js, js_url)
    
    
        vid_info = await self.get_vid_info()
        for stream in stream_manifest:
            video = Stream(
                stream=stream,
                monostate=self.stream_monostate,
                po_token=self.po_token,
                video_playback_ustreamer_config=vid_info.get('playerConfig', {}).get('mediaCommonConfig', {}).get('mediaUstreamerRequestConfig', {}).get('videoPlaybackUstreamerConfig')
            )
            self._fmt_streams.append(video)
    
    
        title = getattr(self, "title", None)
        length = getattr(self, "length", None)
        self.stream_monostate.title = title
        self.stream_monostate.duration = length
    
        return self._fmt_streams

    async def streams(self) -> StreamQuery:
        await self.check_availability()
        fmt_streams = await self.get_fmt_streams()
        return StreamQuery(fmt_streams)
    
    
    async def get_stream_by_itag(self, itag: int):
        """
        Async: Return only the Stream object for a specific itag (faster, less CPU).
        """
        await self.check_availability()
    
        streaming_data = await self.get_streaming_data()
        stream_manifest = extract.apply_descrambler(streaming_data)
        inner_tube = InnerTube(self.client)
    
    #Filter streams by itag
        stream_data = next((s for s in stream_manifest if int(s.get("itag", -1)) == int(itag)), None)
        if not stream_data:
            raise Exception(f"itag {itag} not found in this video.")
    
    #decipher only itag
        if inner_tube.require_js_player:
            try:
                vid_info = await self.get_vid_info()
                js = await self.get_js()
                js_url = await self.get_js_url()
                extract.apply_signature([stream_data], vid_info, js, js_url)
            except exceptions.ExtractError:
    #retry, recache
                self._js = None
                self._js_url = None
                pytubefix.__js__ = None
                pytubefix.__js_url__ = None
                vid_info = await self.get_vid_info()
                js = await self.get_js()
                js_url = await self.get_js_url()
                extract.apply_signature([stream_data], vid_info, js, js_url)
    
    #Build stream object
        vid_info = await self.get_vid_info()
        stream_obj = Stream(
            stream=stream_data,
            monostate=self.stream_monostate,
            po_token=self.po_token,
            video_playback_ustreamer_config=vid_info.get('playerConfig', {}).get('mediaCommonConfig', {}).get('mediaUstreamerRequestConfig', {}).get('videoPlaybackUstreamerConfig')
        )
        return stream_obj
    
    async def age_check(self):
        """Async: If the video has age restrictions, confirm age via TV client."""
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
            innertube.innertube_context.update(await self.get_signature_timestamp())
    
        innertube.verify_age(self.video_id) 
        innertube_response = innertube.player(self.video_id)
        playability_status = innertube_response['playabilityStatus'].get('status', None)
    
        # If still not accessible, raise the correct exception
        if playability_status != 'OK':
            if playability_status == 'UNPLAYABLE':
                raise exceptions.AgeCheckRequiredAccountError(self.video_id)
            else:
                raise exceptions.AgeCheckRequiredError(self.video_id)
    
        self._vid_info = innertube_response
    
    
    async def caption_tracks(self) -> List[pytubefix.Caption]:
        """Async: Get a list of Caption tracks."""
        innertube = InnerTube(
            client='WEB' if not self.use_oauth else self.client,
            use_oauth=self.use_oauth,
            allow_cache=self.allow_oauth_cache,
            token_file=self.token_file,
            oauth_verifier=self.oauth_verifier,
            use_po_token=self.use_po_token,
            po_token_verifier=self.po_token_verifier
        )
        innertube_response = innertube.player(self.video_id)
        raw_tracks = (
            innertube_response.get("captions", {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        )
        return [pytubefix.Caption(track) for track in raw_tracks]
    
    
    async def captions(self) -> pytubefix.CaptionQuery:
        """Interface to query caption tracks.

        :rtype: :class:`CaptionQuery <CaptionQuery>`.
        """
        caption_tracks = await self.caption_tracks()
        return pytubefix.CaptionQuery(caption_tracks)
    

    async def chapters(self) -> List[pytubefix.Chapter]:
        """Async: Get a list of Chapter objects."""
        try:
            chapters_data = []
            initial_data = await self.get_initial_data()
            markers_map = initial_data['playerOverlays']['playerOverlayRenderer'][
                'decoratedPlayerBarRenderer']['decoratedPlayerBarRenderer']['playerBar'][
                'multiMarkersPlayerBarRenderer']['markersMap']
            for marker in markers_map:
                if marker['key'].upper() in ('DESCRIPTION_CHAPTERS', 'AUTO_CHAPTERS'):
                    chapters_data = marker['value']['chapters']
                    break
        except (KeyError, IndexError, TypeError):
            return []
    
        result: List[pytubefix.Chapter] = []
        for i, chapter_data in enumerate(chapters_data):
            chapter_start = int(
                chapter_data['chapterRenderer']['timeRangeStartMillis'] / 1000
            )
            if i == len(chapters_data) - 1:
                chapter_end = getattr(self, "length", None) or 0
            else:
                chapter_end = int(
                    chapters_data[i + 1]['chapterRenderer']['timeRangeStartMillis'] / 1000
                )
    
            result.append(pytubefix.Chapter(chapter_data, chapter_end - chapter_start))
    
        return result
    
    
    async def key_moments(self) -> List[pytubefix.KeyMoment]:
        """Async: Get a list of KeyMoment objects."""
        try:
            initial_data = await self.get_initial_data()
            mutations = initial_data['frameworkUpdates']['entityBatchUpdate']['mutations']
            key_moments_data = []
            for mutation in mutations:
                marker = (
                    mutation.get('payload', {})
                    .get('macroMarkersListEntity', {})
                    .get('markersList', {})
                )
                if marker.get('markerType') == "MARKER_TYPE_TIMESTAMPS":
                    key_moments_data = marker.get('markers', [])
                    break
    
            if not key_moments_data:
                return []
        except (KeyError, IndexError, TypeError):
            return []
    
        result: List[pytubefix.KeyMoment] = []
        for i, key_moment_data in enumerate(key_moments_data):
            key_moment_start = int(key_moment_data['startMillis']) // 1000
    
            if i == len(key_moments_data) - 1:
                key_moment_end = getattr(self, "length", None) or 0
            else:
                key_moment_end = int(key_moments_data[i + 1]['startMillis']) // 1000
    
            result.append(pytubefix.KeyMoment(key_moment_data, key_moment_end - key_moment_start))
    
        return result
    
    
    async def replayed_heatmap(self) -> List[Dict[str, float]]:
        """Async: Get a list of heatmap data as Dict<str, float>."""
        try:
            initial_data = await self.get_initial_data()
            mutations = initial_data['frameworkUpdates']['entityBatchUpdate']['mutations']
            heatmaps_data = []
            for mutation in mutations:
                marker = (
                    mutation.get('payload', {})
                    .get('macroMarkersListEntity', {})
                    .get('markersList', {})
                )
                if marker.get('markerType') == "MARKER_TYPE_HEATMAP":
                    heatmaps_data = marker.get('markers', [])
                    break
    
            if not heatmaps_data:
                return []
        except (KeyError, IndexError, TypeError):
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
    
    async def thumbnail_url(self) -> str:
        """Async: Get the thumbnail url image."""
        vid_info = await self.get_vid_info()
        thumbnail_details = (
            vid_info.get("videoDetails", {})
            .get("thumbnail", {})
            .get("thumbnails")
        )
        if thumbnail_details:
            thumbnail_details = thumbnail_details[-1]  # last item has max size
            return thumbnail_details["url"]
    
        return f"https://img.youtube.com/vi/{self.video_id}/maxresdefault.jpg"
    
    
    async def publish_date(self):
        """Async: Get the publish date."""
        if self._publish_date:
            return self._publish_date
        html = await self.get_watch_html()
        self._publish_date = extract.publish_date(html)
        return self._publish_date
    
    def set_publish_date(self, value):
        """Sets the publish date."""
        self._publish_date = value
    
    
    async def title(self) -> str:
        """Async: Get the video title."""
        vid_info = await self.get_vid_info()
        self._author = vid_info.get("videoDetails", {}).get("author", "unknown")
    
        if self._title:
            return self._title
    
        try:
            if 'title' in vid_info.get('videoDetails', {}):
                self._title = vid_info['videoDetails']['title']
                logger.debug('Found title in vid_info')
            else:
                vid_details = await self.get_vid_details()
                contents = vid_details.get('contents', {})
  
                if 'singleColumnWatchNextResults' in contents:
                    s = contents['singleColumnWatchNextResults']['results']['results']['contents'][0]['itemSectionRenderer']['contents'][0]
                    if 'videoMetadataRenderer' in s:
                        self._title = s['videoMetadataRenderer']['title']['runs'][0]['text']
                    else:
                        self._title = s['musicWatchMetadataRenderer']['title']['simpleText']
    
                elif 'twoColumnWatchNextResults' in contents:
                    self._title = contents['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['title']['runs'][0]['text']
    
                logger.debug('Found title in vid_details')
        except KeyError as e:
            await self.check_availability()
            raise exceptions.PytubeFixError(
                (
                    f'Exception while accessing title of {self.watch_url}. '
                    'Please file a bug report at https://github.com/JuanBindez/pytubefix'
                )
            ) from e
    
        return self._title
    
    def set_title(self, value):
        """Sets the title value."""
        self._title = value
    
    async def description(self) -> str:
        """Async: Get the video description."""
        vid_info = await self.get_vid_info()
        return vid_info.get("videoDetails", {}).get("shortDescription")
    
    async def rating(self) -> float:
        """Async: Get the video average rating."""
        vid_info = await self.get_vid_info()
        return float(vid_info.get("videoDetails", {}).get("averageRating", 0.0))
    
    async def length(self) -> int:
        """Async: Get the video length in seconds."""
        vid_info = await self.get_vid_info()
        return int(vid_info.get('videoDetails', {}).get('lengthSeconds', 0))
    
    async def views(self) -> int:
        """Async: Get the number of the times the video has been viewed."""
        vid_info = await self.get_vid_info()
        return int(vid_info.get("videoDetails", {}).get("viewCount", "0"))
    
    async def author(self) -> str:
        """Async: Get the video author."""
        if self._author:
            return self._author
        vid_info = await self.get_vid_info()
        self._author = vid_info.get("videoDetails", {}).get("author", "unknown")
        return self._author
    
    def set_author(self, value):
        """Set the video author."""
        self._author = value
    
    
    async def keywords(self) -> List[str]:
        """Async: Get the video keywords."""
        vid_info = await self.get_vid_info()
        return vid_info.get('videoDetails', {}).get('keywords', [])
    
    async def channel_id(self) -> str:
        """Async: Get the video poster's channel id."""
        vid_info = await self.get_vid_info()
        return vid_info.get('videoDetails', {}).get('channelId', None)
    
    async def channel_url(self) -> str:
        """Async: Construct the channel url for the video's poster from the channel id."""
        channel_id = await self.channel_id()
        return f'https://www.youtube.com/channel/{channel_id}' if channel_id else None
    
    async def likes(self):
        """Async: Get the video likes count."""
        try:
            vid_details = await self.get_vid_details()
            return (
                vid_details['contents']
                ['twoColumnWatchNextResults']
                ['results']
                ['results']
                ['contents'][0]
                ['videoPrimaryInfoRenderer']
                ['videoActions']
                ['menuRenderer']
                ['topLevelButtons'][0]
                ['segmentedLikeDislikeButtonViewModel']
                ['likeCountEntity']
                ['likeCountIfLikedNumber']
            )
        except (KeyError, IndexError, TypeError):
            return None
    
    
    async def metadata(self) -> Optional[YouTubeMetadata]:
        """Async: Get the metadata for the video."""
        if not self._metadata:
            initial_data = await self.get_initial_data()
            self._metadata = extract.metadata(initial_data)
        return self._metadata
    
    
    def register_on_progress_callback(self, func: Callable[[Any, bytes, int], None]):
        """Register a download progress callback function post initialization."""
        self.stream_monostate.on_progress = func
    
    def register_on_complete_callback(self, func: Callable[[Any, Optional[str]], None]):
        """Register a download complete callback function post initialization."""
        self.stream_monostate.on_complete = func
    
    
    @staticmethod
    def from_id(video_id: str, http_client: Optional[AsyncHTTPClient] = None) -> "AsyncYouTube":
        """Construct an AsyncYouTube object from a video id."""
        return AsyncYouTube(f"https://www.youtube.com/watch?v={video_id}", http_client=http_client)

    