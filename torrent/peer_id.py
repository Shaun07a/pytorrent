import random
import string


class PeerID:

    PREFIX = "-PC0001-"

    @classmethod
    def generate(cls) -> bytes:
        suffix = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(12)
        )

        return (cls.PREFIX + suffix).encode()