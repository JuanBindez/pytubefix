import socket
import os
import pytest
from unittest import mock
from urllib.error import URLError

from pytubefix import request
from pytubefix.exceptions import MaxRetriesExceeded


@mock.patch("pytubefix.request.urlopen")
def test_streaming(mock_urlopen):
    # Given
    fake_stream_binary = [
        os.urandom(8 * 1024),
        os.urandom(8 * 1024),
        os.urandom(8 * 1024),
        None,
    ]
    mock_response = mock.Mock()
    mock_response.read.side_effect = fake_stream_binary
    mock_response.info.return_value = {"Content-Range": "bytes 200-1000/24576"}
    mock_urlopen.return_value = mock_response
    # When
    response = request.stream("http://fakeassurl.gov/streaming_test")

    count = 0

    for blob in response:
        if blob: count += len(blob)
    assert count == 24576
    assert mock_response.read.call_count == 4 + 1
@mock.patch('pytubefix.request.urlopen')
def test_timeout(mock_urlopen):
    exc = URLError(reason=socket.timeout('timed_out'))
    mock_urlopen.side_effect = exc
    generator = request.stream('http://fakeassurl.gov/timeout_test', timeout=1)
    with pytest.raises(MaxRetriesExceeded):
        next(generator)


@mock.patch("pytubefix.request.urlopen")
def test_headers(mock_urlopen):
    response = mock.Mock()
    response.info.return_value = {"content-length": "16384"}
    mock_urlopen.return_value = response
    response = request.head("http://fakeassurl.gov")
    assert response == {"content-length": "16384"}


@mock.patch("pytubefix.request.urlopen")
def test_get(mock_urlopen):
    response = mock.Mock()
    response.read.return_value = "<html></html>".encode("utf-8")
    mock_urlopen.return_value = response
    response = request.get("http://fakeassurl.gov")
    assert response == "<html></html>"


def test_get_non_http():
    with pytest.raises(ValueError):  # noqa: PT011
        request.get("file://bad")
