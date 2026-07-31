from torrent.parser import TorrentParser

parser = TorrentParser(
    "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
)

torrent = parser.parse()

print(f"Name          : {torrent.name}")
print(f"Announce URL  : {torrent.announce}")
print(f"File Size     : {torrent.length}")
print(f"Piece Length  : {torrent.piece_length}")
print(f"Pieces        : {len(torrent.piece_hashes)}")