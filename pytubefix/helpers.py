"""Various helper functions implemented by pytube."""
import functools
import gzip
import json
import logging
import os
import re
import warnings
from typing import Any, Callable, Dict, List, Optional, TypeVar
from urllib import request

from pytubefix.exceptions import RegexMatchError

logger = logging.getLogger(__name__)


class DeferredGeneratorList:
    """A wrapper class for deferring list generation.

    Pytubefix has some continuation generators that create web calls, which means
    that any time a full list is requested, all of those web calls must be
    made at once, which could lead to slowdowns. This will allow individual
    elements to be queried, so that slowdowns only happen as necessary. For
    example, you can iterate over elements in the list without accessing them
    all simultaneously. This should allow for speed improvements for playlist
    and channel interactions.
    """

    def __init__(self, generator):
        """Construct a :class:`DeferredGeneratorList <DeferredGeneratorList>`.

        :param generator generator:
            The deferrable generator to create a wrapper for.
        :param func func:
            (Optional) A function to call on the generator items to produce the list.
        """
        self.gen = generator
        self._elements = []

    def __eq__(self, other):
        """We want to mimic list behavior for comparison."""
        return list(self) == other

    def __getitem__(self, key) -> Any:
        """Only generate items as they're asked for."""
        # We only allow querying with indexes.
        if not isinstance(key, (int, slice)):
            raise TypeError('Key must be either a slice or int.')

        # Convert int keys to slice
        key_slice = key
        if isinstance(key, int):
            key_slice = slice(key, key + 1, 1)

        # Generate all elements up to the final item
        while len(self._elements) < key_slice.stop:
            try:
                next_item = next(self.gen)
            except StopIteration as exc:
                # If we can't find enough elements for the slice, raise an IndexError
                raise IndexError from exc

            self._elements.append(next_item)

        return self._elements[key]

    def __iter__(self):
        """Custom iterator for dynamically generated list."""
        iter_index = 0
        while True:
            try:
                curr_item = self[iter_index]
            except IndexError:
                return

            yield curr_item
            iter_index += 1

    def __next__(self) -> Any:
        """Fetch next element in iterator."""
        try:
            curr_element = self[self.iter_index]
        except IndexError:
            raise StopIteration
        self.iter_index += 1
        return curr_element  # noqa:R504

    def __len__(self) -> int:
        """Return length of list of all items."""
        self.generate_all()
        return len(self._elements)

    def __repr__(self) -> str:
        """String representation of all items."""
        self.generate_all()
        return str(self._elements)

    def __reversed__(self):
        self.generate_all()
        return self._elements[::-1]

    def generate_all(self):
        """Generate all items."""
        while True:
            try:
                next_item = next(self.gen)
            except StopIteration:
                break
            else:
                self._elements.append(next_item)


def regex_search(pattern: str, string: str, group: int) -> str:
    """Shortcut method to search a string for a given pattern.

    :param str pattern:
        A regular expression pattern.
    :param str string:
        A target string to search.
    :param int group:
        Index of group to return.
    :rtype:
        str or tuple
    :returns:
        Substring pattern matches.
    """
    regex = re.compile(pattern)
    results = regex.search(string)
    if not results:
        raise RegexMatchError(caller="regex_search", pattern=pattern)

    logger.debug("matched regex search: %s", pattern)

    return results.group(group)


def safe_filename(s: str, max_length: int = 255) -> str:
    """Sanitize a string making it safe to use as a filename.

    This function was based off the limitations outlined here:
    https://en.wikipedia.org/wiki/Filename.

    :param str s:
        A string to make safe for use as a file name.
    :param int max_length:
        The maximum filename character length.
    :rtype: str
    :returns:
        A sanitized string.
    """
    # Characters in range 0-31 (0x00-0x1F) are not allowed in ntfs filenames.
    ntfs_characters = [chr(i) for i in range(31)]
    characters = [
        r'"',
        r"\#",
        r"\$",
        r"\%",
        r"'",
        r"\*",
        r"\,",
        r"\.",
        r"\/",
        r"\:",
        r'"',
        r"\;",
        r"\<",
        r"\>",
        r"\?",
        r"\\",
        r"\^",
        r"\|",
        r"\~",
        r"\\\\",
    ]
    pattern = "|".join(ntfs_characters + characters)
    regex = re.compile(pattern, re.UNICODE)
    filename = regex.sub("", s)
    return filename[:max_length].rsplit(" ", 0)[0]


def setup_logger(level: int = logging.ERROR, log_filename: Optional[str] = None) -> None:
    """Create a configured instance of logger.

    :param int level:
        Describe the severity level of the logs to handle.
    """
    fmt = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    date_fmt = "%H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    # https://github.com/pytube/pytube/issues/163
    logger = logging.getLogger("pytubefix")
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_filename is not None:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


GenericType = TypeVar("GenericType")


def cache(func: Callable[..., GenericType]) -> GenericType:
    """ mypy compatible annotation wrapper for lru_cache"""
    return functools.lru_cache()(func)  # type: ignore


def deprecated(reason: str) -> Callable:
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    def decorator(func1):
        message = "Call to deprecated function {name} ({reason})."

        @functools.wraps(func1)
        def new_func1(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                message.format(name=func1.__name__, reason=reason),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func1(*args, **kwargs)

        return new_func1

    return decorator


def target_directory(output_path: Optional[str] = None) -> str:
    """
    Function for determining target directory of a download.
    Returns an absolute path (if relative one given) or the current
    path (if none given). Makes directory if it does not exist.

    :type output_path: str
        :rtype: str
    :returns:
        An absolute directory path as a string.
    """
    if output_path:
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
    else:
        output_path = os.getcwd()
    os.makedirs(output_path, exist_ok=True)
    return output_path


def install_proxy(proxy_handler: Dict[str, str]) -> None:
    proxy_support = request.ProxyHandler(proxy_handler)
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)


def uniqueify(duped_list: List) -> List:
    """Remove duplicate items from a list, while maintaining list order.

    :param List duped_list
        List to remove duplicates from

    :return List result
        De-duplicated list
    """
    result = []
    for item in duped_list:
        if item in result:
            continue
        result.append(item)
    return result


def generate_all_html_json_mocks():
    """Regenerate the video mock json files for all current test videos.

    This should automatically output to the test/mocks directory.
    """
    test_vid_ids = [
        '2lAe1cqCOXo',
        '5YceQ8YqYMc',
        'irauhITDrsE',
        'm8uHb5jIGN8',
        'QRS8MkLhQmM',
        'WXxV9g7lsFE'
    ]
    for vid_id in test_vid_ids:
        create_mock_html_json(vid_id)


def create_mock_html_json(vid_id) -> Dict[str, Any]:
    """Generate a json.gz file with sample html responses.

    :param str vid_id
        YouTube video id

    :return dict data
        Dict used to generate the json.gz file
    """
    from pytubefix import YouTube
    gzip_filename = f'yt-video-{vid_id}-html.json.gz'

    # Get the pytube directory in order to navigate to /tests/mocks
    pytube_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir
        )
    )
    pytube_mocks_path = os.path.join(pytube_dir_path, 'tests', 'mocks')
    gzip_filepath = os.path.join(pytube_mocks_path, gzip_filename)

    yt = YouTube(f'https://www.youtube.com/watch?v={vid_id}')
    html_data = {
        'url': yt.watch_url,
        'js': yt.js,
        'embed_html': yt.embed_html,
        'watch_html': yt.watch_html,
        'vid_info': yt.vid_info
    }

    logger.info('Outputing json.gz file to %s', gzip_filepath)
    with gzip.open(gzip_filepath, 'wb') as f:
        f.write(json.dumps(html_data).encode('utf-8'))

    return html_data


def strip_color_codes(input_str):
    """Remove ANSI color codes from a string"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', input_str)
