# BitTorrent Client

A BitTorrent client built from scratch in **Python 3.13** to understand and implement the core mechanisms of the BitTorrent peer-to-peer protocol.

The project implements torrent metadata parsing, HTTP tracker communication, peer discovery, TCP peer handshakes, block-based piece downloading, SHA-1 integrity verification, resumable downloads, corrupted-piece detection, and tracker lifecycle events.

The client uses Python's `asyncio` for asynchronous peer communication and `aiohttp` for HTTP tracker requests. Local testing is performed using qBittorrent as a seeder.

---

## Features

- Parse `.torrent` files using a custom Bencode decoder
- Extract torrent metadata and piece information
- Generate the torrent's SHA-1 info hash
- Communicate with HTTP BitTorrent trackers
- Discover peers through tracker announces
- Generate BitTorrent peer IDs
- Perform BitTorrent peer handshakes
- Handle bitfield, interested, and unchoke messages
- Download pieces using 16 KiB blocks
- Assemble blocks into complete pieces
- Verify downloaded pieces using SHA-1
- Write verified pieces to disk
- Track download progress and remaining bytes
- Resume interrupted downloads
- Verify existing pieces when resuming
- Detect corrupted pieces and download them again
- Send `started` and `completed` tracker events
- Read and use the tracker-provided announce interval
- Support asynchronous peer communication
- Local testing with qBittorrent

---

## Architecture

```text
                         .torrent File
                              |
                              v
                    +---------------------+
                    |   Torrent Parser    |
                    |      Bencode        |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |    Tracker Client   |
                    |    HTTP Announce    |
                    +----------+----------+
                               |
                         Peer Discovery
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        +-----------+    +-----------+    +-----------+
        |   Peer 1  |    |   Peer 2  |    |   Peer N  |
        +-----+-----+    +-----+-----+    +-----+-----+
              |                |                |
              +----------------+----------------+
                               |
                               v
                    +---------------------+
                    |    Peer Manager     |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |    Block Manager    |
                    |       16 KiB        |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |   Piece Assembler   |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |    SHA-1 Verifier   |
                    +----------+----------+
                               |
                         Verification
                               |
                               v
                    +---------------------+
                    |     File Writer     |
                    +----------+----------+
                               |
                               v
                       Downloaded File
How It Works

The download process follows the basic BitTorrent workflow:

1. Read the .torrent file
          |
          v
2. Decode torrent metadata
          |
          v
3. Calculate the info hash
          |
          v
4. Check for an existing download
          |
          v
5. Verify already downloaded pieces
          |
          v
6. Announce to the tracker
          |
          v
7. Receive peer information
          |
          v
8. Connect to peers
          |
          v
9. Perform the BitTorrent handshake
          |
          v
10. Exchange bitfield / interested / unchoke messages
          |
          v
11. Request 16 KiB blocks
          |
          v
12. Assemble received blocks into pieces
          |
          v
13. Verify each piece using SHA-1
          |
          v
14. Write verified pieces to disk
          |
          v
15. Continue until all pieces are complete
          |
          v
16. Send completed event to tracker
Project Structure
Torrent Client/
│
├── main.py
├── requirements.txt
├── README.md
│
├── sample_torrents/
│   └── large_sample.torrent
│
├── downloads/
│   └── large_sample.txt
│
└── torrent/
    ├── __init__.py
    ├── bencoding.py
    ├── parser.py
    ├── tracker.py
    ├── peer.py
    ├── peer_id.py
    ├── peer_parser.py
    ├── peer_manager.py
    ├── block_manager.py
    ├── piece_manager.py
    ├── piece_assembler.py
    ├── verifier.py
    └── file_writer.py
Core Components
Bencode Decoder

Implements decoding of the Bencode format used by .torrent files.

Supported data types include:

Integers
Byte strings
Lists
Dictionaries

This allows the client to read torrent metadata without depending on a BitTorrent-specific library.

Torrent Parser

Extracts important torrent metadata such as:

Tracker announce URL
File name
File size
Piece length
SHA-1 piece hashes
Torrent info hash

The info hash is used to identify the torrent during tracker communication and peer handshakes.

Tracker Client

Communicates with HTTP trackers using the BitTorrent announce protocol.

The client sends information including:

info_hash
peer_id
port
uploaded
downloaded
left
compact
numwant
event

The client supports tracker lifecycle events such as:

started
completed

It also reads the tracker-provided announce interval for periodic communication.

Peer Discovery

The tracker returns peers in compact peer format. The client parses the response into peer IP addresses and ports and passes them to the peer manager.

Peer Connection

The peer connection implements the basic BitTorrent handshake and message flow:

Handshake
    ↓
Bitfield
    ↓
Interested
    ↓
Unchoke
    ↓
Request
    ↓
Piece

Peer communication is handled asynchronously using asyncio.

Block Manager

Pieces are divided into 16 KiB blocks for network transfer.

For example, a 256 KiB piece is divided into:

256 KiB / 16 KiB = 16 blocks

The block manager keeps track of requested and completed blocks and determines when an entire piece has been received.

Piece Assembler

Received blocks are stored using their piece index and byte offset.

Once all blocks for a piece have been received, they are ordered by offset and assembled into the complete piece.

SHA-1 Verification

Every completed piece is verified against the SHA-1 hash stored in the torrent metadata.

Downloaded Piece
       |
       v
    SHA-1
       |
       v
Compare with Torrent Hash
       |
   +---+---+
   |       |
 Valid   Invalid
   |       |
   v       v
 Write   Re-download

This ensures corrupted data is not accepted as a valid piece.

Resume Support

The client can resume partially completed downloads.

When starting, the existing file is scanned and each piece is checked for:

Correct length
Valid SHA-1 hash

Valid pieces are marked as already downloaded, while missing or corrupted pieces are requested again.

Example:

Checking existing download...

Existing file size: 1048576 bytes
Expected file size: 1048576 bytes

Piece 0 already complete and verified.
Piece 1 already complete and verified.
Piece 2 verification FAILED.
Piece 3 already complete and verified.

Resume scan: 3/4 pieces complete.

Only the missing or corrupted piece needs to be downloaded again.

Local Testing

The project includes a local testing mode for development.

qBittorrent can be used as a local seeder while the Python client acts as the downloader.

+---------------------+          +---------------------+
|   Python Client     |   TCP    |     qBittorrent     |
|                     | <------> |       Seeder        |
|   BitTorrent Peer   |          |                     |
+---------------------+          +---------------------+

For local testing, discovered peer addresses can be redirected to:

127.0.0.1

This makes it possible to test the BitTorrent peer protocol locally without depending entirely on remote peers.

Test Torrent

The included test torrent uses a small file divided into four pieces:

File Size    : 1 MiB
Pieces       : 4
Piece Size   : 256 KiB
Block Size   : 16 KiB

Each piece is therefore transferred through multiple 16 KiB block requests.

Example Output
Announce URL : http://tracker.opentrackr.org:1337/announce
Info Hash    : 3b211a0300e7b23c85bf2d35eb63a1377b066f71

Total Pieces: 4

Checking existing download...

Existing file size: 0 bytes
Expected file size: 1048576 bytes

Resume scan: 0/4 pieces complete.

Connecting to tracker (Attempt 1/3)...

HTTP Status: 200
Tracker interval: 1800 seconds

Found 2 peers

Connecting to peer 127.0.0.1:65026

Handshake successful.

Peer unchoked us.

Piece 0 complete!
Verification: True
Wrote Piece 0

Piece 1 complete!
Verification: True
Wrote Piece 1

Piece 2 complete!
Verification: True
Wrote Piece 2

Piece 3 complete!
Verification: True
Wrote Piece 3

Progress: 4/4

Download Complete!
Sending completed event to tracker...

HTTP Status: 200
Resume and Corruption Detection

The client was tested by modifying an already downloaded piece.

Instead of downloading the entire file again, the client detects the invalid SHA-1 hash and downloads only the affected piece.

Resume scan: 3/4 pieces complete.

Piece 2 complete!
Verification: True
Wrote Piece 2

Progress: 4/4

Download Complete!

This demonstrates both resumable downloading and piece-level integrity verification.

Technologies Used
Technology	Purpose
Python 3.13	Core implementation
asyncio	Asynchronous networking
aiohttp	HTTP tracker communication
TCP	Peer-to-peer communication
Bencode	Torrent metadata decoding
SHA-1	Piece integrity verification
qBittorrent	Local seeding and testing
Git/GitHub	Version control
Concepts Demonstrated

This project provides practical experience with:

Computer networking
Peer-to-peer architecture
TCP communication
Network protocol implementation
Distributed systems
Asynchronous programming
Concurrency
Binary data parsing
File I/O
Hashing and data integrity
State management
Fault detection
Resumable data transfer
Installation
Requirements
Python 3.13+
qBittorrent for local testing
Internet connection for HTTP tracker communication
Clone the Repository
git clone <your-repository-url>
cd "Torrent Client"
Create a Virtual Environment

Windows PowerShell:

python -m venv .venv
.venv\Scripts\Activate.ps1
Install Dependencies
pip install -r requirements.txt
Run the Client
python main.py

Downloaded files are stored in:

downloads/
Configuration

Local testing can be enabled in main.py:

LOCAL_TESTING = True

Set it to:

LOCAL_TESTING = False

when local peer address replacement is not required.

Current Limitations

This project focuses on the core BitTorrent download workflow and is not intended to be a complete production BitTorrent client.

Currently, it does not implement:

DHT
Magnet links
UDP trackers
Peer Exchange (PEX)
Protocol encryption
Upload/seeding functionality
Rarest-piece-first selection
Advanced peer scoring
Production-grade peer reconnection
Complete request timeout/retry handling
Full choking/unchoking strategy
Future Improvements
 Robust multi-peer piece scheduling
 Piece availability tracking using HAVE messages
 Rarest-piece-first selection
 Request timeout and retry handling
 Automatic peer reconnection
 Improved choking/unchoking strategy
 Download speed and ETA tracking
 Upload/seeding support
 UDP tracker support
 DHT implementation
 Magnet link support
 Peer Exchange (PEX)
 Command-line interface
 Improved logging and statistics
Learning Objective

The main goal of this project is to understand how a peer-to-peer protocol works internally by implementing the major components rather than relying on an existing BitTorrent client library.

The project brings together:

Torrent Metadata
       ↓
Tracker Communication
       ↓
Peer Discovery
       ↓
TCP Connection
       ↓
BitTorrent Handshake
       ↓
Block Requests
       ↓
Piece Assembly
       ↓
SHA-1 Verification
       ↓
File Persistence

into a working peer-to-peer download system.

Disclaimer

This project is intended for educational and networking research purposes.

Only download or distribute files that you have the legal right to access or share.

Author

Shaun Joseph