"""Implements a simple wrapper around urlopen."""

import http.client
import json
import logging
import re
import socket
from functools import lru_cache
from urllib import parse
from urllib.error import URLError
from urllib.request import Request, urlopen
import requests

from pytubefix.exceptions import RegexMatchError, MaxRetriesExceeded
from pytubefix.helpers import regex_search

logger = logging.getLogger(__name__)
default_range_size = 9437184  # 9MB


def _execute_request_requests(
    url, method=None, headers=None, data=None, proxies=None, timeout=20
):
    base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}

    if headers:
        base_headers.update(headers)

    if data and method != "GET":
        # If data is already a JSON string, we should pass it as 'data' not 'json'
        if isinstance(data, (dict, list)):
            json_data = data
            data = None
        else:
            json_data = None
    else:
        json_data = None  # Ensure no JSON data is sent with GET requests
        data = None  # Ensure no data is sent with GET requests

    response = requests.request(
        method,
        url,
        headers=base_headers,
        data=data,
        json=json_data,
        timeout=timeout,
        proxies=proxies,  # Uncomment if proxies are needed
        verify=False,
    )

    return response


def _execute_request_urllib(
    url, method=None, headers=None, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT
):
    base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}
    if headers:
        base_headers.update(headers)
    if data and not isinstance(data, bytes):  # encode data for request
        data = bytes(json.dumps(data), encoding="utf-8")
    if url.lower().startswith("http"):
        request = Request(url, headers=base_headers, method=method, data=data)
    else:
        raise ValueError("Invalid URL")
    return urlopen(request, timeout=timeout)  # nosec


def get(url, extra_headers=None, proxies=None, timeout=20):
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :param dict extra_headers:
        Extra headers to add to the request
    :rtype: str
    :returns:
        UTF-8 encoded string of response
    """
    if extra_headers is None:
        extra_headers = {}

    response_requests_one = _execute_request_requests(
        url, method="GET", headers=extra_headers, proxies=proxies, timeout=timeout
    )
    return response_requests_one.text


def post(url, extra_headers=None, data=None, proxies=None, timeout=20):
    """Send an http POST request.

    :param str url:
        The URL to perform the POST request for.
    :param dict extra_headers:
        Extra headers to add to the request
    :param dict data:
        The data to send on the POST request
    :rtype: str
    :returns:
        UTF-8 encoded string of response
    """
    # could technically be implemented in get,
    # but to avoid confusion implemented like this
    if extra_headers is None:
        extra_headers = {}
    if data is None:
        data = {}
    # required because the youtube servers are strict on content type
    # raises HTTPError [400]: Bad Request otherwise
    extra_headers.update({"Content-Type": "application/json"})
    # response = _execute_request_urllib(
    #     url, headers=extra_headers, data=data, timeout=timeout
    # )
    response = _execute_request_requests(
        url, "POST", headers=extra_headers, data=data, proxies=proxies
    )
    response_text_manual = response.content.decode("utf-8")
    response_requests_loaded = json.loads(response_text_manual)
    return response_requests_loaded


def seq_stream(url, timeout=20, max_retries=0, proxies=None):
    """Read the response in sequence.
    :param str url: The URL to perform the GET request for.
    :rtype: Iterable[bytes]
    """
    # YouTube expects a request sequence number as part of the parameters.
    split_url = parse.urlsplit(url)
    base_url = f"{split_url.scheme}://{split_url.netloc}/{split_url.path}?"

    querys = dict(parse.parse_qsl(split_url.query))

    # The 0th sequential request provides the file headers, which tell us
    #  information about how the file is segmented.
    querys["sq"] = 0
    url = base_url + parse.urlencode(querys)

    segment_data = b""
    for chunk in stream(url, timeout=timeout, max_retries=max_retries, proxies=proxies):
        yield chunk
        segment_data += chunk

    # We can then parse the header to find the number of segments
    stream_info = segment_data.split(b"\r\n")
    segment_count_pattern = re.compile(b"Segment-Count: (\\d+)")
    for line in stream_info:
        match = segment_count_pattern.search(line)
        if match:
            segment_count = int(match.group(1).decode("utf-8"))

    # We request these segments sequentially to build the file.
    seq_num = 1
    while seq_num <= segment_count:
        # Create sequential request URL
        querys["sq"] = seq_num
        url = base_url + parse.urlencode(querys)

        yield from stream(
            url, timeout=timeout, max_retries=max_retries, proxies=proxies
        )
        seq_num += 1
    return  # pylint: disable=R1711


# TODO: Refactor this code


def stream(url, timeout=20, max_retries=0, proxies=None):
    """Read the response in chunks.
    :param str url: The URL to perform the GET request for.
    :param int timeout: The timeout for the request in seconds.
    :param int max_retries: The maximum number of retries for the request.
    :param dict proxies: Proxies to use for the request.
    :rtype: Iterable[bytes]
    """
    chunk_size: int = 1024  # fake filesize to start
    base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}
    head_req = requests.head(
        url + f"&range={0}-{99999999999}",
        headers=base_headers,
        proxies=proxies,
        verify=False,
    )
    full_file_size = int(head_req.headers["Content-Length"])
    downloaded = 0

    def get_range(start, end):

        retries = 0
        while retries <= max_retries:
            try:
                response = requests.get(
                    url + f"&range={start}-{end}",
                    headers=base_headers,
                    # stream=True, # Not working.
                    proxies=proxies,
                    verify=False,
                    timeout=timeout,
                )
                if response.status_code in [200, 206]:  # 206 Partial Content
                    return response
            except requests.RequestException:
                retries += 1
                if retries > max_retries:
                    raise
                time.sleep(2)
        return None

    while downloaded < full_file_size:
        end_range = min(downloaded + default_range_size - 1, full_file_size - 1)
        response = get_range(downloaded, end_range)
        if response:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filter out keep-alive new chunks
                    yield chunk
                    downloaded += len(chunk)


@lru_cache()
def filesize(url, proxies=None):
    """Fetch size in bytes of file at given URL

    :param str url: The URL to get the size of
    :returns: int: size in bytes of remote file
    """
    return int(head(url, proxies)["content-length"])


@lru_cache()
def seq_filesize(url, proxies=None):
    """Fetch size in bytes of file at given URL from sequential requests

    :param str url: The URL to get the size of
    :returns: int: size in bytes of remote file
    """
    total_filesize = 0
    # YouTube expects a request sequence number as part of the parameters.
    split_url = parse.urlsplit(url)
    base_url = "%s://%s/%s?" % (split_url.scheme, split_url.netloc, split_url.path)
    querys = dict(parse.parse_qsl(split_url.query))

    # The 0th sequential request provides the file headers, which tell us
    #  information about how the file is segmented.
    querys["sq"] = 0
    url = base_url + parse.urlencode(querys)
    response = _execute_request_requests(url, method="GET", proxies=proxies)

    response_value = response.text
    # The file header must be added to the total filesize
    total_filesize += len(response_value)

    # We can then parse the header to find the number of segments
    segment_count = 0
    stream_info = response_value.split(b"\r\n")
    segment_regex = b"Segment-Count: (\\d+)"
    for line in stream_info:
        # One of the lines should contain the segment count, but we don't know
        #  which, so we need to iterate through the lines to find it
        try:
            segment_count = int(regex_search(segment_regex, line, 1))
        except RegexMatchError:
            pass

    if segment_count == 0:
        raise RegexMatchError("seq_filesize", segment_regex)

    # We make HEAD requests to the segments sequentially to find the total filesize.
    seq_num = 1
    while seq_num <= segment_count:
        # Create sequential request URL
        querys["sq"] = seq_num
        url = base_url + parse.urlencode(querys)

        total_filesize += int(head(url, proxies)["content-length"])
        seq_num += 1
    return total_filesize


def head(url, proxies=None):
    """Fetch headers returned http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: dict
    :returns:
        dictionary of lowercase headers
    """
    response_headers = _execute_request_requests(
        url, method="HEAD", proxies=proxies
    ).headers
    return {k.lower(): v for k, v in response_headers.items()}
