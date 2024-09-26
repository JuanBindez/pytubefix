# -*- coding: utf-8 -*-
"""Module for interacting with a user's youtube channel."""
import json
import logging
from typing import Dict, List, Optional, Tuple, Iterable, Any, Callable

from pytubefix import extract, YouTube, Playlist, request
from pytubefix.helpers import cache, uniqueify, DeferredGeneratorList
from pytubefix.innertube import InnerTube

logger = logging.getLogger(__name__)


class Channel(Playlist):
    def __init__(
            self,
            url: str,
            client: str = InnerTube().client_name,
            proxies: Optional[Dict[str, str]] = None,
            use_oauth: bool = False,
            allow_oauth_cache: bool = True,
            token_file: Optional[str] = None,
            oauth_verifier: Optional[Callable[[str, str], None]] = None,
            use_po_token: Optional[bool] = False,
            po_token_verifier: Optional[Callable[[None], Tuple[str, str]]] = None,
    ):
        """Construct a :class:`Channel <Channel>`.
        :param str url:
            A valid YouTube channel URL.
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
        """
        super().__init__(url, proxies)

        self.channel_uri = extract.channel_name(url)

        self.client = client
        self.use_oauth = use_oauth
        self.allow_oauth_cache = allow_oauth_cache
        self.token_file = token_file
        self.oauth_verifier = oauth_verifier

        self.use_po_token = use_po_token
        self.po_token_verifier = po_token_verifier

        self.channel_url = (
            f"https://www.youtube.com{self.channel_uri}"
        )

        self.featured_url = self.channel_url + '/featured'
        self.videos_url = self.channel_url + '/videos'
        self.shorts_url = self.channel_url + '/shorts'
        self.live_url = self.channel_url + '/streams'
        self.releases_url = self.channel_url + '/releases'
        self.playlists_url = self.channel_url + '/playlists'
        self.community_url = self.channel_url + '/community'
        self.featured_channels_url = self.channel_url + '/channels'
        self.about_url = self.channel_url + '/about'

        self._html_url = self.videos_url  # Videos will be preferred over short videos and live

        # Possible future additions
        self._playlists_html = None
        self._community_html = None
        self._featured_channels_html = None
        self._about_html = None

    def __repr__(self) -> str:
        return f'<pytubefix.contrib.Channel object: channelUri={self.channel_uri}>'

    @property
    def channel_name(self):
        """Get the name of the YouTube channel.

        :rtype: str
        """
        return self.initial_data['metadata']['channelMetadataRenderer']['title']

    @property
    def channel_id(self):
        """Get the ID of the YouTube channel.

        This will return the underlying ID, not the vanity URL.

        :rtype: str
        """
        return self.initial_data['metadata']['channelMetadataRenderer']['externalId']

    @property
    def vanity_url(self):
        """Get the vanity URL of the YouTube channel.

        Returns None if it doesn't exist.

        :rtype: str
        """
        return self.initial_data['metadata']['channelMetadataRenderer'].get('vanityChannelUrl', None)  # noqa:E501

    @property
    def html_url(self):
        """Get the html url.

        :rtype: str
        """
        return self._html_url

    @html_url.setter
    def html_url(self, value):
        """Set the html url and clear the cache."""
        if self._html_url != value:
            self._html = None
            self._initial_data = None
            self.__class__.video_urls.fget.cache_clear()
            self._html_url = value

    @property
    def html(self):
        """Get the html for the /videos, /shorts or /streams page.

        :rtype: str
        """
        if self._html:
            return self._html
        self._html = request.get(self.html_url)
        return self._html

    @property
    def playlists_html(self):
        """Get the html for the /playlists page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._playlists_html:
            return self._playlists_html
        else:
            self._playlists_html = request.get(self.playlists_url)
            return self._playlists_html

    @property
    def community_html(self):
        """Get the html for the /community page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._community_html:
            return self._community_html
        else:
            self._community_html = request.get(self.community_url)
            return self._community_html

    @property
    def featured_channels_html(self):
        """Get the html for the /channels page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._featured_channels_html:
            return self._featured_channels_html
        else:
            self._featured_channels_html = request.get(self.featured_channels_url)
            return self._featured_channels_html

    @property
    def about_html(self):
        """Get the html for the /about page.

        Currently unused for any functionality.

        :rtype: str
        """
        if self._about_html:
            return self._about_html
        else:
            self._about_html = request.get(self.about_url)
            return self._about_html

    def url_generator(self):
        """Generator that yields video URLs.

        :Yields: Video URLs
        """
        for page in self._paginate(self.html):
            for obj in page:
                yield obj

    def videos_generator(self):
        for url in self.video_urls:
            yield url

    def _get_active_tab(self, initial_data) -> dict:
        """ Receive the raw json and return the active page.

        :returns: Active page json object.
        """
        active_tab = {}
        # Possible tabs: Home, Videos, Shorts, Live, Releases, Playlists, Community, Channels, About
        # We check each page for the URL that is active.
        for tab in initial_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]:
            if 'tabRenderer' in tab:
                tab_url = tab["tabRenderer"]["endpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
                if tab_url.rsplit('/', maxsplit=1)[-1] == self.html_url.rsplit('/', maxsplit=1)[-1]:
                    active_tab = tab
                    break
        return active_tab

    def _extract_obj_from_home(self) -> list:
        """ Extract items from the channel home page.

        :returns: list of home page objects.
        """
        items = []
        try:
            contents = self._get_active_tab(self.initial_data)['tabRenderer']['content'][
                'sectionListRenderer']['contents']

            for obj in contents:
                item_section_renderer = obj['itemSectionRenderer']['contents'][0]

                # Skip the presentation videos for non-subscribers
                if 'channelVideoPlayerRenderer' in item_section_renderer:
                    continue

                # Skip presentation videos for subscribers
                if 'channelFeaturedContentRenderer' in item_section_renderer:
                    continue

                # skip the list with channel members
                if 'recognitionShelfRenderer' in item_section_renderer:
                    continue

                # Get the horizontal shorts
                if 'reelShelfRenderer' in item_section_renderer:
                    for x in item_section_renderer['reelShelfRenderer']['items']:
                        items.append(x)

                # Get videos, playlist and horizontal channels
                if 'shelfRenderer' in item_section_renderer:
                    # We only take items that are horizontal
                    if 'horizontalListRenderer' in item_section_renderer['shelfRenderer']['content']:
                        # We iterate over each item in the array, which could be videos, playlist or channel
                        for x in item_section_renderer['shelfRenderer']['content']['horizontalListRenderer']['items']:
                            items.append(x)

        except (KeyError, IndexError, TypeError):
            return []

        # Extract object from each corresponding url
        items_obj = self._extract_ids(items)

        # remove duplicates
        return uniqueify(items_obj)

    def _extract_videos(self, raw_json: str, context: Optional[Any] = None) -> Tuple[List[str], Optional[str]]:
        """Extracts videos from a raw json page

        :param str raw_json: Input json extracted from the page or the last
            server response
        :rtype: Tuple[List[str], Optional[str]]
        :returns: Tuple containing a list of up to 100 video watch ids and
            a continuation token, if more videos are available
        """

        if isinstance(raw_json, dict):
            initial_data = raw_json
        else:
            initial_data = json.loads(raw_json)
        # this is the json tree structure, if the json was extracted from
        # html
        try:
            active_tab = self._get_active_tab(initial_data)
            try:
                # This is the json tree structure for videos, shorts and streams
                items = active_tab['tabRenderer']['content']['richGridRenderer']['contents']
            except (KeyError, IndexError, TypeError):
                # This is the json tree structure for playlists
                items = active_tab['tabRenderer']['content']['sectionListRenderer']['contents'][0][
                    'itemSectionRenderer']['contents'][0]['gridRenderer']['items']

            # This is the json tree structure of visitor data
            # It is necessary to send the visitorData together with the continuation token
            self._visitor_data = initial_data["responseContext"]["webResponseContextExtensionData"][
                "ytConfigData"]["visitorData"]

        except (KeyError, IndexError, TypeError):
            try:
                # this is the json tree structure, if the json was directly sent
                # by the server in a continuation response
                important_content = initial_data[1]['response']['onResponseReceivedActions'][
                    0
                ]['appendContinuationItemsAction']['continuationItems']
                items = important_content
            except (KeyError, IndexError, TypeError):
                try:
                    # this is the json tree structure, if the json was directly sent
                    # by the server in a continuation response
                    # no longer a list and no longer has the "response" key
                    important_content = initial_data['onResponseReceivedActions'][0][
                        'appendContinuationItemsAction']['continuationItems']
                    items = important_content
                except (KeyError, IndexError, TypeError) as p:
                    logger.info(p)
                    return [], None

        try:
            continuation = items[-1]['continuationItemRenderer'][
                'continuationEndpoint'
            ]['continuationCommand']['token']
            items = items[:-1]
        except (KeyError, IndexError):
            # if there is an error, no continuation is available
            continuation = None

        # Extract object from each corresponding url
        items_obj = self._extract_ids(items)

        # remove duplicates
        return uniqueify(items_obj), continuation

    def _extract_video_id(self, x: dict):
        """ Try extracting video ids, if it fails, try extracting shorts ids.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            return YouTube(f"/watch?v="
                           f"{x['richItemRenderer']['content']['videoRenderer']['videoId']}",
                           client=self.client,
                           use_oauth=self.use_oauth,
                           allow_oauth_cache=self.allow_oauth_cache,
                           token_file=self.token_file,
                           oauth_verifier=self.oauth_verifier,
                           use_po_token=self.use_po_token,
                           po_token_verifier=self.po_token_verifier
                           )
        except (KeyError, IndexError, TypeError):
            return self._extract_shorts_id(x)

    def _extract_shorts_id(self, x: dict):
        """ Try extracting shorts ids, if it fails, try extracting release ids.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            content = x['richItemRenderer']['content']

            # New json tree added on 09/12/2024
            if 'shortsLockupViewModel' in content:
                video_id = content['shortsLockupViewModel']['onTap']['innertubeCommand']['reelWatchEndpoint']['videoId']
            else:
                video_id = content['reelItemRenderer']['videoId']

            return YouTube(f"/watch?v={video_id}",
                           client=self.client,
                           use_oauth=self.use_oauth,
                           allow_oauth_cache=self.allow_oauth_cache,
                           token_file=self.token_file,
                           oauth_verifier=self.oauth_verifier,
                           use_po_token=self.use_po_token,
                           po_token_verifier=self.po_token_verifier
                           )
        except (KeyError, IndexError, TypeError):
            return self._extract_release_id(x)

    def _extract_release_id(self, x: dict):
        """ Try extracting release ids, if it fails, try extracting video IDs from the home page.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            return Playlist(f"/playlist?list="
                            f"{x['richItemRenderer']['content']['playlistRenderer']['playlistId']}",
                            client=self.client,
                            use_oauth=self.use_oauth,
                            allow_oauth_cache=self.allow_oauth_cache,
                            token_file=self.token_file,
                            oauth_verifier=self.oauth_verifier,
                            use_po_token=self.use_po_token,
                            po_token_verifier=self.po_token_verifier
                            )
        except (KeyError, IndexError, TypeError):
            return self._extract_video_id_from_home(x)

    def _extract_video_id_from_home(self, x: dict):
        """ Try extracting the video IDs from the home page,
        if that fails, try extracting the shorts IDs from the home page.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            return YouTube(f"/watch?v="
                           f"{x['gridVideoRenderer']['videoId']}",
                           client=self.client,
                           use_oauth=self.use_oauth,
                           allow_oauth_cache=self.allow_oauth_cache,
                           token_file=self.token_file,
                           oauth_verifier=self.oauth_verifier,
                           use_po_token=self.use_po_token,
                           po_token_verifier=self.po_token_verifier
                           )
        except (KeyError, IndexError, TypeError):
            return self._extract_shorts_id_from_home(x)

    def _extract_shorts_id_from_home(self, x: dict):
        """ Try extracting the shorts IDs from the home page, if that fails, try extracting the playlist IDs.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            return YouTube(f"/watch?v="
                           f"{x['reelItemRenderer']['videoId']}",
                           client=self.client,
                           use_oauth=self.use_oauth,
                           allow_oauth_cache=self.allow_oauth_cache,
                           token_file=self.token_file,
                           oauth_verifier=self.oauth_verifier,
                           use_po_token=self.use_po_token,
                           po_token_verifier=self.po_token_verifier
                           )
        except (KeyError, IndexError, TypeError):
            return self._extract_playlist_id(x)

    def _extract_playlist_id(self, x: dict):
        """ Try extracting the playlist IDs, if that fails, try extracting the channel IDs.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            return Playlist(f"/playlist?list="
                            f"{x['gridPlaylistRenderer']['playlistId']}",
                            client=self.client,
                            use_oauth=self.use_oauth,
                            allow_oauth_cache=self.allow_oauth_cache,
                            token_file=self.token_file,
                            oauth_verifier=self.oauth_verifier,
                            use_po_token=self.use_po_token,
                            po_token_verifier=self.po_token_verifier
                            )
        except (KeyError, IndexError, TypeError):
            return self._extract_channel_id_from_home(x)

    def _extract_channel_id_from_home(self, x: dict):
        """ Try extracting the channel IDs from the home page, if that fails, return nothing.

        :returns: List of YouTube, Playlist or Channel objects.
        """
        try:
            return Channel(f"/channel/"
                           f"{x['gridChannelRenderer']['channelId']}",
                           client=self.client,
                           use_oauth=self.use_oauth,
                           allow_oauth_cache=self.allow_oauth_cache,
                           token_file=self.token_file,
                           oauth_verifier=self.oauth_verifier,
                           use_po_token=self.use_po_token,
                           po_token_verifier=self.po_token_verifier
                           )
        except (KeyError, IndexError, TypeError):
            return []

    @property
    def views(self) -> int:
        """Extract view count for channel.

        :return: Channel view count
        :rtype: int
        """
        self.html_url = self.about_url

        try:
            views_text = self.initial_data['onResponseReceivedEndpoints'][0]['showEngagementPanelEndpoint'][
                'engagementPanel']['engagementPanelSectionListRenderer']['content']['sectionListRenderer'][
                'contents'][0]['itemSectionRenderer']['contents'][0]['aboutChannelRenderer']['metadata'][
                'aboutChannelViewModel']['viewCountText']

            # "1,234,567 view"
            count_text = views_text.split(' ')[0]
            # "1234567"
            count_text = count_text.replace(',', '')
            return int(count_text)
        except KeyError:
            return 0

    @property
    def description(self) -> str:
        """Extract the channel description.

        :return: Channel description
        :rtype: str
        """
        self.html_url = self.channel_url
        return self.initial_data['metadata']['channelMetadataRenderer']['description']

    def find_videos_info(self, data):
        """Recursively search for 'videos' in the text content of the JSON."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'content' and isinstance(value, str) and 'videos' in value:
                    return value
                if isinstance(value, (dict, list)):
                    result = self.find_videos_info(value)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_videos_info(item)
                if result:
                    return result
        return None

    @property
    def length(self):
        """Extracts the approximate amount of videos from the channel."""
        try:
            result = self.find_videos_info(self.initial_data)
            return result if result else 'Unknown'
        except Exception as e:
            print(f"Exception: {e}")
            return 'Unknown'

    @property
    def last_updated(self) -> str:
        """Extract the date of the last uploaded video.

        :return: Last video uploaded
        :rtype: str
        """
        self.html_url = self.videos_url
        try:
            last_updated_text = self.initial_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1][
                'tabRenderer']['content']['richGridRenderer']['contents'][0]['richItemRenderer']['content'][
                'videoRenderer']['publishedTimeText']['simpleText']
            return last_updated_text
        except KeyError:
            return None

    @property
    def thumbnail_url(self) -> str:
        """extract the profile image from the json of the channel home page

        :rtype: str
        :return: a string with the url of the channel's profile image
        """
        self.html_url = self.channel_url  # get the url of the channel home page
        return self.initial_data['metadata']['channelMetadataRenderer']['avatar']['thumbnails'][0]['url']

    @property
    def home(self) -> list:
        """ Yields YouTube, Playlist and Channel objects from the channel home page.

        :returns: List of YouTube, Playlist and Channel objects.
        """
        self.html_url = self.featured_url  # Set home tab
        return self._extract_obj_from_home()

    @property
    def videos(self) -> Iterable[YouTube]:
        """Yields YouTube objects of videos in this channel

        :rtype: List[YouTube]
        :returns: List of YouTube
        """
        self.html_url = self.videos_url  # Set video tab
        return DeferredGeneratorList(self.videos_generator())

    @property
    def shorts(self) -> Iterable[YouTube]:
        """Yields YouTube objects of short videos in this channel

       :rtype: List[YouTube]
       :returns: List of YouTube
       """
        self.html_url = self.shorts_url  # Set shorts tab
        return DeferredGeneratorList(self.videos_generator())

    @property
    def live(self) -> Iterable[YouTube]:
        """Yields YouTube objects of live in this channel

       :rtype: List[YouTube]
       :returns: List of YouTube
       """
        self.html_url = self.live_url  # Set streams tab
        return DeferredGeneratorList(self.videos_generator())

    @property
    def releases(self) -> Iterable[Playlist]:
        """Yields Playlist objects in this channel

       :rtype: List[Playlist]
       :returns: List of YouTube
       """
        self.html_url = self.releases_url  # Set releases tab
        return DeferredGeneratorList(self.videos_generator())

    @property
    def playlists(self) -> Iterable[Playlist]:
        """Yields Playlist objects in this channel

       :rtype: List[Playlist]
       :returns: List of Playlist
       """
        self.html_url = self.playlists_url  # Set playlists tab
        return DeferredGeneratorList(self.videos_generator())
