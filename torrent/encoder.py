class BencodeEncoder:

    def encode(self, value):

        if isinstance(value, int):
            return self._encode_int(value)

        elif isinstance(value, bytes):
            return self._encode_bytes(value)

        elif isinstance(value, str):
            return self._encode_bytes(value.encode())

        elif isinstance(value, list):
            return self._encode_list(value)

        elif isinstance(value, dict):
            return self._encode_dict(value)

        else:
            raise TypeError(f"Unsupported type: {type(value)}")

    def _encode_int(self, value):
        return f"i{value}e".encode()

    def _encode_bytes(self, value):
        return str(len(value)).encode() + b":" + value

    def _encode_list(self, value):
        encoded = b"l"

        for item in value:
            encoded += self.encode(item)

        encoded += b"e"

        return encoded
    