import asyncio
import struct

from torrent.handshake import Handshake
from torrent.models import Peer, TorrentMeta
from torrent.messages import Interested, Message, MESSAGE_NAMES
from torrent.messages import Request
from torrent.bitfield import Bitfield
from torrent.piece_assembler import PieceAssembler
from torrent.verifier import PieceVerifier


PIPELINE_SIZE = 5


class PeerConnection:

    def __init__(
        self,
        peer: Peer,
        torrent: TorrentMeta,
        peer_id: bytes,
        piece_manager,
        block_manager,
        writer_file
    ):
        self.peer = peer
        self.torrent = torrent
        self.peer_id = peer_id

        self.reader = None
        self.writer = None
        self.bitfield = None
        self.assembler = PieceAssembler()
        self.piece_manager = piece_manager
        self.block_manager = block_manager
        self.writer_file = writer_file
                

        # Per-peer objects
        self.assembler = PieceAssembler()

        self.started_download = False

    async def connect(self):

        print(f"[{self.peer.ip}:{self.peer.port}] Connecting...")

        self.reader, self.writer = await asyncio.open_connection(
            self.peer.ip,
            self.peer.port
        )

        print(f"[{self.peer.ip}:{self.peer.port}] Connected.")

    async def send_handshake(self):

        handshake = Handshake(
            self.torrent.info_hash,
            self.peer_id
        )

        self.writer.write(handshake.encode())

        await self.writer.drain()

        print(f"[{self.peer.ip}:{self.peer.port}] Handshake sent")

    async def receive_handshake(self):

        response = await self.reader.readexactly(68)

        decoded = Handshake.decode(response)

        print("\nPeer Handshake")
        print("----------------------------")
        print("Protocol :", decoded["protocol"])
        print("Peer ID  :", decoded["peer_id"])
        print("Info Hash:", decoded["info_hash"].hex())

        if decoded["info_hash"] != self.torrent.info_hash:
            raise ValueError("Peer returned the wrong torrent!")

        return decoded

    async def handshake(self):

        await self.connect()

        await self.send_handshake()

        await self.receive_handshake()

        await self.send_interested()

        while True:

            try:
                message = await asyncio.wait_for(
                    self.receive_message(),
                    timeout=10
                )

            except asyncio.TimeoutError:
                print("Timed out waiting for peer.")
                break

            except asyncio.IncompleteReadError:
                print("Peer closed the connection.")
                break

            if message is None:
                continue

            await self.handle_message(message)

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def receive_message(self):

        # Read the 4-byte message length
        length_bytes = await self.reader.readexactly(4)

        length = struct.unpack(">I", length_bytes)[0]

        # KeepAlive message
        if length == 0:
            print("Received KeepAlive")
            return None

        # Read the remaining bytes
        message_bytes = await self.reader.readexactly(length)

        # Decode the complete message
        message = Message.decode(length_bytes + message_bytes)

        return message

    async def send_interested(self):

        message = Interested()

        self.writer.write(message.encode())

        await self.writer.drain()

        print(f"[{self.peer.ip}:{self.peer.port}] Interested message sent")

    async def send_request(self):

        request = self.block_manager.next_request()

        if request is None:
            
            return

        piece, begin, length = request

        packet = Request(
            index=piece,
            begin=begin,
            length=length
        )

        self.writer.write(packet.encode())

        await self.writer.drain()

        print(
            f"[{self.peer.ip}:{self.peer.port}] "
            f"Requested Piece {piece} "
            f"Offset {begin} "
            f"Length {length}"
        )

    async def fill_pipeline(self):

        for _ in range(PIPELINE_SIZE):

            request = self.block_manager.next_request()

            if request is None:
                print("Pipeline complete.")
                break

            piece, begin, length = request

            packet = Request(
                index=piece,
                begin=begin,
                length=length
            )

            self.writer.write(packet.encode())

            print(
                f"Queued Piece {piece} Offset {begin}"
            )

        await self.writer.drain()

    async def handle_message(self, message):

        message_name = MESSAGE_NAMES.get(
            message.message_id,
            "Unknown"
        )

        print(f"\n[{self.peer.ip}:{self.peer.port}] Peer Message")
        print("--------------------------------------------")
        print("Type    :", message_name)
        print("Payload :", len(message.payload), "bytes")

        if message_name == "Unchoke":
            print("Peer unchoked us.")
            await self.fill_pipeline()

        elif message_name == "Bitfield":

            self.bitfield = Bitfield(message.payload)

            print(
                f"Peer has {self.bitfield.count()} pieces."
            )

            print(
                "Has Piece #0:",
                self.bitfield.has_piece(0)
            )
        elif message_name == "Have":

            piece_index = struct.unpack(">I", message.payload)[0]

            print(f"Peer has piece {piece_index}")

        elif message_name == "Piece":

            print("Received piece")

            print("Piece Index :", message.index)
            print("Block Begin :", message.begin)
            print("Block Size  :", len(message.block))

            self.assembler.add_block(
                message.index,
                message.begin,
                message.block
            )

            self.block_manager.mark_completed(
                message.index,
                message.begin
            )

            print(f"Stored block at offset {message.begin}")

            current_size = self.assembler.piece_size(
                message.index
            )

            piece_length = min(
                self.torrent.piece_length,
                self.torrent.length -
                message.index * self.torrent.piece_length
            )

            print(
                f"Current Piece Size: "
                f"{current_size}/{piece_length}"
            )

            # Is the whole piece received?
            if current_size >= piece_length:

                print(f"\nPiece {message.index} complete!")

                piece = self.assembler.assemble_piece(
                    message.index
                )

                verified = PieceVerifier.verify(
                    piece,
                    self.torrent.pieces[message.index]
                )

                print("Verification:", verified)

                if verified:

                    self.writer_file.write_piece(
                        message.index,
                        piece
                    )

                    self.piece_manager.mark_downloaded(
                        message.index
                    )

                    downloaded, total = self.piece_manager.progress()

                    print(f"Progress: {downloaded}/{total}")

                    # Entire torrent finished?
                    if downloaded == total:

                        print("\nDownload Complete!")

                        self.writer.close()
                        await self.writer.wait_closed()

                        return

            # Request the next block only if download isn't complete
            await self.send_request()

        elif message_name == "Unchoke":

            if not self.started_download:

                self.started_download = True

                print("Peer unchoked us.")

                await self.fill_pipeline()