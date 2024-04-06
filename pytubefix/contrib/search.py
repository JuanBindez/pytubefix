"""Module for interacting with YouTube search."""
# Native python imports
import logging
from typing import List

# Local imports
from pytubefix import YouTube, Channel, Playlist
from pytubefix.helpers import deprecated
from pytubefix.innertube import InnerTube

logger = logging.getLogger(__name__)


class Search:
    def __init__(self, query):
        """Initialize Search object.

        :param str query:
            Search query provided by the user.
        """
        self.query = query
        self._innertube_client = InnerTube(client='WEB')

        # The first search, without a continuation, is structured differently
        #  and contains completion suggestions, so we must store this separately
        self._initial_results = None

        self._results = {}
        self._completion_suggestions = None

        # Used for keeping track of query continuations so that new results
        #  are always returned when get_next_results() is called
        self._current_continuation = None

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
            results, continuation = self.fetch_and_parse()
            self._current_continuation = continuation
            self._results['videos'] = results['videos']
            self._results['shorts'] = results['shorts']
            self._results['playlist'] = results['playlist']
            self._results['channel'] = results['channel']

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
            results, continuation = self.fetch_and_parse()
            self._current_continuation = continuation
            self._results['videos'] = results['videos']
            self._results['shorts'] = results['shorts']
            self._results['playlist'] = results['playlist']
            self._results['channel'] = results['channel']

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
            results, continuation = self.fetch_and_parse()
            self._current_continuation = continuation
            self._results['videos'] = results['videos']
            self._results['shorts'] = results['shorts']
            self._results['playlist'] = results['playlist']
            self._results['channel'] = results['channel']

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
            results, continuation = self.fetch_and_parse()
            self._current_continuation = continuation
            self._results['videos'] = results['videos']
            self._results['shorts'] = results['shorts']
            self._results['playlist'] = results['playlist']
            self._results['channel'] = results['channel']

        return [items for items in self._results['channel']]

    @property
    @deprecated("Get video results using: .videos")
    def results(self) -> list:
        """returns a list with videos, shorts, playlist and channels.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list
        :returns:
            A list of YouTube, Playlist and Channel objects.
        """
        # Remove these comments to get the list of videos, shorts, playlist and channel

        # if not self._results:
        #     results, continuation = self.fetch_and_parse()
        #     self._current_continuation = continuation
        #     self._results['videos'] = results['videos']
        #     self._results['shorts'] = results['shorts']
        #     self._results['playlist'] = results['playlist']
        #     self._results['channel'] = results['channel']

        #  return [items for values in self._results.values() for items in values]
        return self.videos

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
            raise IndexError

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
        raw_results = self.fetch_query(continuation)

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
                                             f"{video_details['playlistRenderer']['playlistId']}"))

                # Get channel results
                if 'channelRenderer' in video_details:
                    channel.append(Channel(f"https://www.youtube.com/channel/"
                                           f"{video_details['channelRenderer']['channelId']}"))

                # Get shorts results
                if 'reelShelfRenderer' in video_details:
                    for items in video_details['reelShelfRenderer']['items']:
                        shorts.append(YouTube(f"https://www.youtube.com/watch?v="
                                              f"{items['reelItemRenderer']['videoId']}"))

                # Get videos results
                if 'videoRenderer' in video_details:
                    videos.append(YouTube(f"https://www.youtube.com/watch?v="
                                          f"{video_details['videoRenderer']['videoId']}"))

            results['videos'] = videos
            results['shorts'] = shorts
            results['playlist'] = playlist
            results['channel'] = channel

        return results, next_continuation

    def fetch_query(self, continuation=None):
        """Fetch raw results from the innertube API.

        :param str continuation:
            Continuation string for fetching results.
        :rtype: dict
        :returns:
            The raw json object returned by the innertube API.
        """
        query_results = self._innertube_client.search(self.query, continuation)
        if not self._initial_results:
            self._initial_results = query_results
        return query_results  # noqa:R504
