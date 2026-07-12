from torrent.bencoding import BencodeDecoder


def test_integer():
    decoder = BencodeDecoder(b"i42e")

    result = decoder.decode()

    assert result == 42

def test_string():
    decoder = BencodeDecoder(b"4:spam")

    result = decoder.decode()

    assert result == b"spam"