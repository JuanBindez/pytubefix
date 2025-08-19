# Pytubefix Library Development Context

## Project Overview

`pytubefix` is a Python library for downloading YouTube videos. It is a fork of the popular `pytube` library that adds stability improvements and new features. The library supports Python 3.7+ and follows PEP 8 style guidelines.

## Core Features

- Download YouTube videos and audio streams
- Handle YouTube's signature cipher decryption
- Interact with YouTube's internal API (Innertube)
- Support for playlists, channels, and search
- Asynchronous operation support
- Bot protection handling
- Captions and chapters support

## Project Structure

### Core Modules
```
pytubefix/
├── __init__.py          # Package initialization
├── __main__.py          # Main entry point and YouTube class
├── streams.py           # Stream handling and processing
├── cipher.py            # Signature cipher decryption
├── innertube.py         # YouTube API interaction
├── extract.py           # Data extraction utilities
└── request.py           # HTTP request management
```

### Key Components

1. **Video Processing**
   - `streams.py`: Stream selection and download
   - `buffer.py`: Data buffering
   - `parser.py`: Response parsing
   - `protobuf.py`: Protocol buffer handling

2. **Security & Authentication**
   ```
   botGuard/
   ├── __init__.py
   ├── bot_guard.py
   ├── vm/
   └── botGuard.js
   ```

3. **Features & Extensions**
   ```
   contrib/
   ├── search.py
   ├── playlist.py
   └── channel.py
   ```

4. **Adaptive Streaming (SABR)**
   ```
   sabr/
   ├── video_streaming/
   ├── core/
   └── proto.py
   ```

## Development Guidelines

### 1. Code Quality Standards
- Follow PEP 8 style guidelines
- Maintain Python 3.7+ compatibility
- Use type hints where applicable
- Keep cyclomatic complexity low

### 2. Documentation Requirements
- Include docstrings for all public functions and classes
- Follow Google-style docstring format
- Update README.md for user-facing changes
- Document complex algorithms with inline comments

### 3. Testing Protocol
- Write unit tests for new features
- Include regression tests for bug fixes
- Maintain test coverage above 80%
- Test edge cases and error conditions

### 4. Error Handling
- Use custom exceptions from `exceptions.py`
- Provide meaningful error messages
- Handle network and API errors gracefully
- Log important operations and errors

### 5. Performance Considerations
- Minimize API calls
- Use async operations for I/O-bound tasks
- Implement proper caching strategies
- Consider memory usage for large downloads

## Key Files Reference

| File | Purpose |
|------|---------|
| `__main__.py` | Entry point and YouTube object implementation |
| `streams.py` | Video/audio stream handling |
| `cipher.py` | Signature decryption algorithms |
| `innertube.py` | YouTube API client |
| `extract.py` | Web page data extraction |
| `request.py` | HTTP request handling |

## Common Tasks

1. **Adding New Features**
   - Create feature branch
   - Update relevant modules
   - Add tests
   - Update documentation
   - Submit pull request

2. **Bug Fixes**
   - Reproduce issue
   - Add regression test
   - Implement fix
   - Document changes

3. **Performance Improvements**
   - Profile code
   - Identify bottlenecks
   - Implement optimizations
   - Benchmark changes

## Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Python Package Guidelines](https://packaging.python.org/tutorials/packaging-projects/)
- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
