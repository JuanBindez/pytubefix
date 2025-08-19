# Pytubefix Library Development Context

This document provides context for an AI assistant to help with the development of the `pytubefix` library.

## Project Overview

`pytubefix` is a Python library for downloading YouTube videos. It is a fork of the popular `pytube` library, with additional fixes and features.

## File Structure

The following is a list of files in the `pytubefix` directory, which contains the main source code for the library:

```
/pytubefix/pytubefix/version.py
/pytubefix/pytubefix/streams.py
/pytubefix/pytubefix/sabr/video_streaming/video_playback_abr_request.py
/pytubefix/pytubefix/sabr/video_streaming/time_range.py
/pytubefix/pytubefix/sabr/video_streaming/streamer_context.py
/pytubefix/pytubefix/sabr/video_streaming/stream_protection_status.py
/pytubefix/pytubefix/sabr/video_streaming/sabr_redirect.py
/pytubefix/pytubefix/sabr/video_streaming/sabr_error.py
/pytubefix/pytubefix/sabr/video_streaming/playback_cookie.py
/pytubefix/pytubefix/sabr/video_streaming/next_request_policy.py
/pytubefix/pytubefix/sabr/video_streaming/media_header.py
/pytubefix/pytubefix/sabr/video_streaming/format_initialization_metadata.py
/pytubefix/pytubefix/sabr/video_streaming/client_abr_state.py
/pytubefix/pytubefix/sabr/video_streaming/buffered_range.py
/pytubefix/pytubefix/sabr/video_streaming/__init__.py
/pytubefix/pytubefix/sabr/proto.py
/pytubefix/pytubefix/sabr/core/server_abr_stream.py
/pytubefix/pytubefix/sabr/core/chunked_data_buffer.py
/pytubefix/pytubefix/sabr/common.py
/pytubefix/pytubefix/sabr/core/UMP.py
/pytubefix/pytubefix/sabr/core/__init__.py
/pytubefix/pytubefix/request.py
/pytubefix/pytubefix/query.py
/pytubefix/pytubefix/protobuf.py
/pytubefix/pytubefix/parser.py
/pytubefix/pytubefix/monostate.py
/pytubefix/pytubefix/sabr/__init__.py
/pytubefix/pytubefix/metadata.py
/pytubefix/pytubefix/keymoments.py
/pytubefix/pytubefix/jsinterp.py
/pytubefix/pytubefix/itags.py
/pytubefix/pytubefix/innertube.py
/pytubefix/pytubefix/info.py
/pytubefix/pytubefix/helpers.py
/pytubefix/pytubefix/file_system.py
/pytubefix/pytubefix/extract.py
/pytubefix/pytubefix/exceptions.py
/pytubefix/pytubefix/contrib/search.py
/pytubefix/pytubefix/contrib/playlist.py
/pytubefix/pytubefix/contrib/channel.py
/pytubefix/pytubefix/cli.py
/pytubefix/pytubefix/cipher.py
/pytubefix/pytubefix/chapters.py
/pytubefix/pytubefix/contrib/__init__.py
/pytubefix/pytubefix/captions.py
/pytubefix/pytubefix/buffer.py
/pytubefix/pytubefix/botGuard/vm/botGuard.js
/pytubefix/pytubefix/botGuard/bot_guard.py
/pytubefix/pytubefix/async_youtube.py
/pytubefix/pytubefix/botGuard/__init__.py
/pytubefix/pytubefix/async_http_client.py
/pytubefix/pytubefix/__main__.py
/pytubefix/pytubefix/__init__.py
```

## Development Guidelines

When assisting with the development of `pytubefix`, please adhere to the following guidelines:

1.  **Understand the Codebase:** Before making any changes, it's important to understand the existing code. The file list above provides a starting point. Key files to understand are:
    *   `__main__.py`: The main entry point for the `YouTube` object.
    *   `streams.py`: Handles the different video and audio streams.
    *   `extract.py`: Contains functions for extracting data from YouTube's web pages.
    *   `cipher.py`: Handles the decryption of YouTube's signature cipher.
    *   `innertube.py`: Interacts with YouTube's internal API.
    *   `request.py`: Manages HTTP requests.

2.  **Maintain Code Style:** The project follows the PEP 8 style guide. Please ensure any new code adheres to this standard, and compatibility with python 3.7+

3.  **Write Clear and Concise Code:** The code should be easy to read and understand. Add comments where necessary to explain complex logic.

4.  **Add Tests:** For any new features or bug fixes, please add corresponding tests to ensure the changes are working correctly and do not introduce regressions.

5.  **Document Changes:** Update the documentation to reflect any changes made to the codebase. This includes docstrings, README files, and any other relevant documentation.

By following these guidelines, you can help ensure that `pytubefix` remains a high-quality and easy-to-maintain library.
