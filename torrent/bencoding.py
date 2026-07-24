from typing import Any


class BencodeDecoder:
    """
    Decodes bencoded bytes into Python objects.
    """

    def __init__(self, data: bytes):
        self.data = data
        self.index = 0

    def decode(self) -> Any:
        """
        Decode the next bencoded object.
        """
        current = self.data[self.index:self.index + 1]

        if current == b"i":
            return self._decode_integer()
        
        elif current.isdigit():
            return self._decode_string()


        raise ValueError("Unsupported bencode type")
    
    def _decode_integer(self) -> int:
        # Skip the 'i'
        self.index += 1

        end = self.data.index(b"e", self.index)

        number = int(self.data[self.index:end])

        self.index = end + 1

        return number
    
    def _decode_string(self) -> bytes:
        # Find where the length ends
        colon = self.data.index(b":", self.index)

        # Read the length
        length = int(self.data[self.index:colon])

        # First byte of the actual string
        start = colon + 1

        # Last byte (exclusive)
        end = start + length

        # Extract the bytes
        value = self.data[start:end]

        # Move the pointer
        self.index = end

        return value

    def _decode_list(self):
        # Skip the 'l'
        self.index += 1

        items = []

        while self.data[self.index:self.index + 1] != b"e":
            items.append(self.decode())

        # Skip the ending 'e'
        self.index += 1

        return items

    def decode(self):
        current = self.data[self.index:self.index + 1]

        if current == b"i":
            return self._decode_integer()

        elif current == b"l":
            return self._decode_list()

        elif current.isdigit():
            return self._decode_string()

        raise ValueError("Unsupported bencode type")