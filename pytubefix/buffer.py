"""This module implements a `Buffer` class for handling in-memory data storage, downloading streams, 
and redirecting content to standard output (stdout)."""

import sys
import io


class Buffer:
    def __init__(self):
        """
        Initializes the in-memory buffer to store data.
        """
        self.buffer = io.BytesIO()

    def download_in_buffer(self, source):
        """
        Downloads data directly into the buffer. Accepts objects with the `stream_to_buffer`
        method or strings.

        Args:
            source: Object or data to be written to the buffer.
        """
        if hasattr(source, 'stream_to_buffer') and callable(source.stream_to_buffer):
            source.stream_to_buffer(self.buffer)
        elif isinstance(source, str):
            self.buffer.write(source.encode('utf-8'))
        else:
            raise TypeError("The provided object is not compatible for downloading into the buffer.")

    def redirect_to_stdout(self):
        """
        Redirects the buffer's content to stdout.
        """
        self.buffer.seek(0)  # Go back to the start of the buffer
        sys.stdout.buffer.write(self.buffer.read())

    def read(self):
        """
        Reads the buffer's content.
        """
        self.buffer.seek(0)
        return self.buffer.read()

    def clear(self):
        """
        Clears the buffer for reuse.
        """
        self.buffer = io.BytesIO()