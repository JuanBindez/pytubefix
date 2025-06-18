# All credits to https://github.com/LuanRT/googlevideo

class UMP:
    def __init__(self, chunked_data_buffer):
        """
       Creates a new UMP parser.
        :param chunked_data_buffer: Instance of a buffer containing data in UMP format.
        """
        self.chunked_data_buffer = chunked_data_buffer

    def parse(self, handle_part):
        """
       Parses parts of the buffer and calls the handler for each complete part.
        :param handle_part: Function called with each part complete.
        :return: Partial if parsing is incomplete, otherwise None.
        """
        while True:
            offset = 0
            part_type, new_offset = self.read_varint(offset)
            offset = new_offset
            part_size, final_offset = self.read_varint(offset)
            offset = final_offset

            if part_type < 0 or part_size < 0:
                break

            if not self.chunked_data_buffer.can_read_bytes(offset, part_size):
                if not self.chunked_data_buffer.can_read_bytes(offset, 1):
                    break
                return {
                    "type": part_type,
                    "size": part_size,
                    "data": self.chunked_data_buffer
                }

            split_result = self.chunked_data_buffer.split(offset)['remaining_buffer'].split(part_size)
            offset = 0
            handle_part({
                "type": part_type,
                "size": part_size,
                "data": split_result['extracted_buffer']
            })
            self.chunked_data_buffer = split_result['remaining_buffer']

    def read_varint(self, offset):
        """
        Reads a variable length integer from the buffer.
        :param offset: Initial reading position.
        :return: Tuple (value, new offset), or (-1, offset) if incomplete.
        """
        if self.chunked_data_buffer.can_read_bytes(offset, 1):
            first_byte = self.chunked_data_buffer.get_uint8(offset)
            if first_byte < 128:
                byte_length = 1
            elif first_byte < 192:
                byte_length = 2
            elif first_byte < 224:
                byte_length = 3
            elif first_byte < 240:
                byte_length = 4
            else:
                byte_length = 5
        else:
            byte_length = 0

        if byte_length < 1 or not self.chunked_data_buffer.can_read_bytes(offset, byte_length):
            return -1, offset

        if byte_length == 1:
            value = self.chunked_data_buffer.get_uint8(offset)
            offset += 1
        elif byte_length == 2:
            byte1 = self.chunked_data_buffer.get_uint8(offset)
            byte2 = self.chunked_data_buffer.get_uint8(offset + 1)
            value = (byte1 & 0x3F) + 64 * byte2
            offset += 2
        elif byte_length == 3:
            byte1 = self.chunked_data_buffer.get_uint8(offset)
            byte2 = self.chunked_data_buffer.get_uint8(offset + 1)
            byte3 = self.chunked_data_buffer.get_uint8(offset + 2)
            value = (byte1 & 0x1F) + 32 * (byte2 + 256 * byte3)
            offset += 3
        elif byte_length == 4:
            byte1 = self.chunked_data_buffer.get_uint8(offset)
            byte2 = self.chunked_data_buffer.get_uint8(offset + 1)
            byte3 = self.chunked_data_buffer.get_uint8(offset + 2)
            byte4 = self.chunked_data_buffer.get_uint8(offset + 3)
            value = (byte1 & 0x0F) + 16 * (byte2 + 256 * (byte3 + 256 * byte4))
            offset += 4
        else:
            temp_offset = offset + 1
            self.chunked_data_buffer.focus(temp_offset)

            if self.can_read_from_current_chunk(temp_offset, 4):
                view = self.get_current_data_view()
                offset_in_chunk = temp_offset - self.chunked_data_buffer.current_chunk_offset
                value = int.from_bytes(
                    view[offset_in_chunk:offset_in_chunk + 4],
                    byteorder='little'
                )
            else:
                byte3 = (
                    self.chunked_data_buffer.get_uint8(temp_offset + 2) +
                    256 * self.chunked_data_buffer.get_uint8(temp_offset + 3)
                )
                value = (
                    self.chunked_data_buffer.get_uint8(temp_offset) +
                    256 * (
                        self.chunked_data_buffer.get_uint8(temp_offset + 1) +
                        256 * byte3
                    )
                )
            offset += 5

        return value, offset

    def can_read_from_current_chunk(self, offset, length):
        """
        Checks whether the specified number of bytes can be read from the current chunk.
        """
        index = self.chunked_data_buffer.current_chunk_index
        current_chunk = self.chunked_data_buffer.chunks[index]
        return (
            offset - self.chunked_data_buffer.current_chunk_offset + length
            <= len(current_chunk)
        )

    def get_current_data_view(self):
        """
        Gets a binary view (DataView) of the current chunk.
        """
        if self.chunked_data_buffer.current_data_view is None:
            chunk = self.chunked_data_buffer.chunks[self.chunked_data_buffer.current_chunk_index]
            self.chunked_data_buffer.current_data_view = memoryview(chunk)
        return self.chunked_data_buffer.current_data_view
