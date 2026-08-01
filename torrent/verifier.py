from hashlib import sha1


class PieceVerifier:

    @staticmethod
    def verify(
        piece: bytes,
        expected_hash: bytes
    ) -> bool:

        return sha1(piece).digest() == expected_hash