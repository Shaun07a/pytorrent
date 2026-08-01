import socket
import struct

from torrent.models import Peer


class PeerParser:

    @staticmethod
    def parse(peers: bytes):
        result = []

        for i in range(0, len(peers), 6):

            chunk = peers[i:i + 6]

            ip = socket.inet_ntoa(chunk[:4])

            port = struct.unpack(">H", chunk[4:])[0]

            result.append(Peer(ip, port))

        return result