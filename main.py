from torrent.parser import TorrentParser

parser = TorrentParser(
    "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
)

parser.parse()