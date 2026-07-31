# from torrent.parser import TorrentParser

# parser = TorrentParser(
#     "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
# )

# torrent = parser.parse()

# print(f"Name          : {torrent.name}")
# print(f"Announce URL  : {torrent.announce}")
# print(f"File Size     : {torrent.length}")
# print(f"Piece Length  : {torrent.piece_length}")
# print(f"Pieces        : {len(torrent.piece_hashes)}")

# from torrent.encoder import BencodeEncoder

# encoder = BencodeEncoder()

# print(encoder.encode(42))
# print(encoder.encode("spam"))
# print(encoder.encode(b"hello"))

# from torrent.encoder import BencodeEncoder

# encoder = BencodeEncoder()

# print(encoder.encode(["spam", "eggs"]))
# print(encoder.encode([1, 2, 3]))
# print(encoder.encode(["hello", 25, b"abc"]))

# from torrent.encoder import BencodeEncoder

# encoder = BencodeEncoder()

# d = {
#     b"age": 20,
#     b"name": b"Shaun"
# }

# print(encoder.encode(d))

# d = {
#     b"banana": 1,
#     b"apple": 2
# }

# print(encoder.encode(d))

from torrent.parser import TorrentParser

parser = TorrentParser(
    "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
)


torrent = parser.parse()
print("Info Hash :", torrent.info_hash.hex())