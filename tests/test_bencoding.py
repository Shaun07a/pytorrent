from torrent.bencoding import BencodeDecoder


def test_integer():
    decoder = BencodeDecoder(b"i42e")

    result = decoder.decode()

    assert result == 42

def test_string():
    decoder = BencodeDecoder(b"4:spam")

    result = decoder.decode()

    assert result == b"spam"


def test_list():
    decoder = BencodeDecoder(
        b"l4:spami42ee"
    )

    result = decoder.decode()

    assert result == [
        b"spam",
        42
    ]

def test_dictionary():
    decoder = BencodeDecoder(
        b"d3:cow3:moo4:spam4:eggse"
    )

    result = decoder.decode()

    assert result == {
        b"cow": b"moo",
        b"spam": b"eggs"
    }