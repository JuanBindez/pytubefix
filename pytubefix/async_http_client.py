import aiohttp
import asyncio
import json
import logging
import re
from urllib import parse

from pytubefix.exceptions import RegexMatchError, MaxRetriesExceeded
from pytubefix.helpers import regex_search

logger = logging.getLogger(__name__)
default_range_size = 9 * 1024 * 1024  # 9MB

class AsyncHTTPClient:
    """Singleton Async HTTP Client with persistent session and handy methods."""

    _instance = None
    _session = None

    def __new__(cls, *args, **kwargs):
        # Singleton pattern: one instance per process
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _get_session(self):
        """Ensure session is alive (recreate if closed)."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the internal session (call at end of program or via async with)."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def _execute_request(
        self, url, method="GET", headers=None, data=None, timeout=None
    ):
        base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}
        if headers:
            base_headers.update(headers)
        send_data = None
        if data is not None:
            send_data = (
                json.dumps(data).encode('utf-8') if not isinstance(data, (bytes, str)) else data
            )
            base_headers.setdefault("Content-Type", "application/json")
        if not url.lower().startswith("http"):
            raise ValueError("Invalid URL")
        session = await self._get_session()
        try:
            resp = await session.request(
                method=method,
                url=url,
                headers=base_headers,
                data=send_data,
                timeout=timeout,
            )
            return resp
        except Exception as e:
            logger.error(f"HTTP error: {e}")
            raise

    async def get(self, url, headers=None, timeout=None):
        """GET request, returns response text."""
        resp = await self._execute_request(url, method="GET", headers=headers, timeout=timeout)
        async with resp:
            return await resp.text()

    async def post(self, url, headers=None, data=None, timeout=None):
        """POST request, returns response text."""
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        resp = await self._execute_request(
            url, method="POST", headers=headers, data=data, timeout=timeout
        )
        async with resp:
            return await resp.text()

    async def head(self, url, headers=None, timeout=None):
        """HEAD request, returns headers as dict."""
        resp = await self._execute_request(url, method="HEAD", headers=headers, timeout=timeout)
        async with resp:
            return {k.lower(): v for k, v in resp.headers.items()}

    async def stream(self, url, timeout=None, max_retries=0):
        """Async generator: stream file in chunks with retries and range support."""
        file_size = default_range_size
        downloaded = 0

        while downloaded < file_size:
            stop_pos = min(downloaded + default_range_size, file_size) - 1
            tries = 0
            response = None
            # retry loop
            while True:
                if tries >= 1 + max_retries:
                    raise MaxRetriesExceeded()
                try:
                    response = await self._execute_request(
                        f"{url}&range={downloaded}-{stop_pos}", timeout=timeout
                    )
                    break
                except aiohttp.ClientError as e:
                    logger.error(e)
                    tries += 1
            # get real filesize if first chunk
            if file_size == default_range_size:
                try:
                    resp = await self._execute_request(
                        f"{url}&range=0-99999999999", timeout=timeout
                    )
                    async with resp:
                        content_length = resp.headers.get("Content-Length")
                        if content_length:
                            file_size = int(content_length)
                except Exception as e:
                    logger.error(e)
            async with response:
                while True:
                    chunk = await response.content.readany()
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    yield chunk

    async def seq_stream(self, url, timeout=None, max_retries=0):
        """Async generator: read sequential video segments in order."""
        split_url = parse.urlsplit(url)
        base_url = f"{split_url.scheme}://{split_url.netloc}/{split_url.path}?"
        qs = dict(parse.parse_qsl(split_url.query))
        qs["sq"] = 0
        url_0 = base_url + parse.urlencode(qs)
        buffer = bytearray()
        async for chunk in self.stream(url_0, timeout, max_retries):
            yield chunk
            buffer.extend(chunk)
        # Find segment count
        segment_regex = re.compile(b"Segment-Count: (\\d+)")
        m = segment_regex.search(buffer)
        if not m:
            raise RegexMatchError("seq_stream", segment_regex.pattern)
        segment_count = 0
        for line in buffer.split(b"\r\n"):
            m = re.search(b"Segment-Count: (\\d+)", line)
            if m:
                segment_count = int(m.group(1))
        # Download all segments
        for sq in range(1, segment_count + 1):
            qs["sq"] = sq
            seg_url = base_url + parse.urlencode(qs)
            async for chunk in self.stream(seg_url, timeout, max_retries):
                yield chunk

    async def filesize(self, url):
        """Get file size via HEAD (Content-Length)."""
        head_info = await self.head(url)
        return int(head_info["content-length"])

    async def seq_filesize(self, url):
        """Get total file size for sequential segments."""
        total = 0
        split_url = parse.urlsplit(url)
        base_url = f"{split_url.scheme}://{split_url.netloc}/{split_url.path}?"
        qs = dict(parse.parse_qsl(split_url.query))
        qs["sq"] = 0
        url_0 = base_url + parse.urlencode(qs)
        resp = await self._execute_request(url_0, method="GET")
        async with resp:
            data = await resp.read()
        total += len(data)
        # Find segment count
        segment_count = 0
        for line in data.split(b"\r\n"):
            try:
                segment_count = int(regex_search(b"Segment-Count: (\\d+)", line, 1))
            except RegexMatchError:
                pass
        if segment_count == 0:
            raise RegexMatchError("seq_filesize", b"Segment-Count: (\\d+)")
        for sq in range(1, segment_count + 1):
            qs["sq"] = sq
            seg_url = base_url + parse.urlencode(qs)
            head_info = await self.head(seg_url)
            total += int(head_info["content-length"])
        return total
