# All credits to https://github.com/LuanRT/googlevideo

class ChunkedDataBuffer:
    def __init__(self, chunks=None):
        """
        Initializes a new ChunkedDataBuffer with the given chunks.
        """
        self.chunks = []
        self.current_chunk_index = 0
        self.current_chunk_offset = 0
        self.current_data_view = None
        self.total_length = 0

        chunks = chunks or []
        for chunk in chunks:
            self.append(chunk)

    def get_length(self):
        return self.total_length

    def append(self, chunk):
        """
        Adds a new chunk to the buffer, merging with the previous one if possible.
        """
        if self.can_merge_with_last_chunk(chunk):
            last_chunk = self.chunks[-1]
            merged = bytearray(last_chunk)
            merged.extend(chunk)
            self.chunks[-1] = bytes(merged)
            self.reset_focus()
        else:
            self.chunks.append(chunk)
        self.total_length += len(chunk)

    def split(self, position):
        """
        Split the buffer at the specified position into two: extracted and remainder.
        """
        extracted_buffer = ChunkedDataBuffer()
        remaining_buffer = ChunkedDataBuffer()
        remaining_pos = position

        for chunk in self.chunks:
            chunk_len = len(chunk)
            if remaining_pos >= chunk_len:
                extracted_buffer.append(chunk)
                remaining_pos -= chunk_len
            elif remaining_pos > 0:
                extracted_buffer.append(chunk[:remaining_pos])
                remaining_buffer.append(chunk[remaining_pos:])
                remaining_pos = 0
            else:
                remaining_buffer.append(chunk)

        return {
            "extracted_buffer": extracted_buffer,
            "remaining_buffer": remaining_buffer
        }

    def is_focused(self, position):
        """
        Checks if the position is within the currently focused chunk.
        """
        chunk = self.chunks[self.current_chunk_index]
        return self.current_chunk_offset <= position < self.current_chunk_offset + len(chunk)

    def focus(self, position):
        """
        Moves the internal focus to the chunk containing the specified position.
        """
        if not self.is_focused(position):
            if position < self.current_chunk_offset:
                self.reset_focus()
            while (self.current_chunk_offset + len(self.chunks[self.current_chunk_index]) <= position and
                   self.current_chunk_index < len(self.chunks) - 1):
                self.current_chunk_offset += len(self.chunks[self.current_chunk_index])
                self.current_chunk_index += 1
            self.current_data_view = None

    def can_read_bytes(self, position, length):
        """
        Checks whether `length` bytes can be read from `position`.
        """
        return position + length <= self.total_length

    def get_uint8(self, position):
        """
        Returns a single byte (as int) from the specified position.
        """
        self.focus(position)
        chunk = self.chunks[self.current_chunk_index]
        return chunk[position - self.current_chunk_offset]

    def can_merge_with_last_chunk(self, chunk):
        """
        Checks if the new chunk can be merged with the last one.
        """
        if not self.chunks:
            return False
        last_chunk = self.chunks[-1]
        return (
            last_chunk is not None and
            isinstance(last_chunk, (bytes, bytearray)) and
            isinstance(chunk, (bytes, bytearray))
        )

    def reset_focus(self):
        """
        Resets focus to the beginning of the buffer.
        """
        self.current_data_view = None
        self.current_chunk_index = 0
        self.current_chunk_offset = 0
