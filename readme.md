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
```

---

## How It Works

The client follows the core BitTorrent download workflow:

```text
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
Bitfield / Interested / Unchoke
       ↓
Block Requests
       ↓
Piece Assembly
       ↓
SHA-1 Verification
       ↓
File Persistence
       ↓
Completed Event
```

### 1. Torrent Parsing

The client reads a `.torrent` file and decodes its Bencode structure to extract:

- Tracker announce URL
- File name
- File size
- Piece length
- SHA-1 piece hashes
- Torrent info hash

The **info hash** identifies the torrent and is used during tracker communication and peer handshakes.

### 2. Tracker Communication

The tracker client communicates with HTTP BitTorrent trackers using the announce protocol.

The request includes information such as:

```text
info_hash
peer_id
port
uploaded
downloaded
left
compact
numwant
event
```

The client supports tracker events including:

```text
started
completed
```

It also reads the tracker-provided announce interval.

### 3. Peer Discovery

The tracker returns a list of peers containing their IP addresses and ports.

The client parses the compact peer response and creates peer objects that can be used for connection attempts.

### 4. Peer Handshake

The client establishes a TCP connection with a peer and performs the BitTorrent handshake.

The basic communication sequence is:

```text
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
```

### 5. Block Downloading

Each torrent piece is divided into smaller blocks.

The current block size is:

```text
16 KiB
```

For example, a 256 KiB piece consists of:

```text
256 KiB / 16 KiB = 16 blocks
```

The `BlockManager` tracks requested and completed blocks.

### 6. Piece Assembly

Received blocks are stored using their piece index and byte offset.

Once all blocks belonging to a piece have been received, they are ordered by offset and combined into the complete piece.

### 7. SHA-1 Verification

Every completed piece is verified against the SHA-1 hash stored in the torrent metadata.

```text
Downloaded Piece
       |
       v
    SHA-1 Hash
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
```

This prevents corrupted data from being accepted as a valid piece.

### 8. Resume Support

The client supports resumable downloads.

When the application starts, it checks whether a partially downloaded file already exists.

Each existing piece is:

1. Checked for the expected length
2. Read from disk
3. SHA-1 verified
4. Marked as complete if valid

For example:

```text
Checking existing download...

Existing file size: 1048576 bytes
Expected file size: 1048576 bytes

Piece 0 already complete and verified.
Piece 1 already complete and verified.
Piece 2 verification FAILED.
Piece 3 already complete and verified.

Resume scan: 3/4 pieces complete.
```

Only the missing or corrupted piece needs to be downloaded again.

---

## Local Testing

The client can be tested locally using **qBittorrent as a seeder**.

```text
+---------------------+          +---------------------+
|   Python Client     |   TCP    |     qBittorrent     |
|                     | <------> |       Seeder        |
|   BitTorrent Peer   |          |                     |
+---------------------+          +---------------------+
```

A local testing mode is available that redirects the configured local test peer to:

```text
127.0.0.1
```

This makes it possible to test the peer protocol locally without relying entirely on remote peers.

---

## Test Torrent

The included test torrent contains a small file divided into four pieces:

```text
File Size     : 1 MiB
Number Pieces : 4
Piece Size    : 256 KiB
Block Size    : 16 KiB
```

Each 256 KiB piece is transferred using multiple 16 KiB block requests.

---

## Example Output

```text
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
```

---

## Resume and Corruption Detection

The resume mechanism was tested by modifying an already downloaded piece.

Instead of downloading the entire file again, the client detects the invalid SHA-1 hash and downloads only the affected piece.

```text
Resume scan: 3/4 pieces complete.

Piece 2 complete!
Verification: True
Wrote Piece 2

Progress: 4/4

Download Complete!
```

This demonstrates both **resumable downloading** and **piece-level integrity verification**.

---

## Project Structure

```text
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
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.13 | Core implementation |
| asyncio | Asynchronous networking |
| aiohttp | HTTP tracker communication |
| TCP | Peer-to-peer communication |
| Bencode | Torrent metadata decoding |
| SHA-1 | Piece integrity verification |
| qBittorrent | Local seeding and testing |
| Git/GitHub | Version control |

---

## Concepts Demonstrated

This project demonstrates practical implementation of:

- Computer Networking
- Peer-to-Peer Architecture
- TCP Communication
- Network Protocols
- Distributed Systems
- Asynchronous Programming
- Concurrency
- Binary Data Parsing
- File I/O
- Hashing and Data Integrity
- State Management
- Fault Detection
- Resumable Data Transfer

---

## Installation

### Requirements

- Python 3.13+
- qBittorrent for local testing
- Internet connection for HTTP tracker communication

### Clone the Repository

```bash
git clone <your-repository-url>
cd "Torrent Client"
```

### Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Client

```bash
python main.py
```

Downloaded files are stored in:

```text
downloads/
```

---

## Configuration

Local testing can be enabled in `main.py`:

```python
LOCAL_TESTING = True
```

Set it to:

```python
LOCAL_TESTING = False
```

when local peer address replacement is not required.

---

## Current Limitations

This project focuses on the core BitTorrent download workflow and is not intended to be a complete production BitTorrent client.

Currently, it does not implement:

- DHT
- Magnet links
- UDP trackers
- Peer Exchange (PEX)
- Protocol encryption
- Upload/seeding functionality
- Rarest-piece-first selection
- Advanced peer scoring
- Production-grade peer reconnection
- Complete request timeout/retry handling
- Full choking/unchoking strategy

---

## Future Improvements

- [ ] Robust multi-peer piece scheduling
- [ ] Piece availability tracking using `HAVE` messages
- [ ] Rarest-piece-first selection
- [ ] Request timeout and retry handling
- [ ] Automatic peer reconnection
- [ ] Improved choking/unchoking strategy
- [ ] Download speed and ETA tracking
- [ ] Upload/seeding support
- [ ] UDP tracker support
- [ ] DHT implementation
- [ ] Magnet link support
- [ ] Peer Exchange (PEX)
- [ ] Command-line interface
- [ ] Improved logging and statistics

---

## Learning Objective

The main goal of this project is to understand how a peer-to-peer file transfer protocol works internally by implementing its core components instead of relying on an existing BitTorrent client library.

The project brings together:

```text
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
```

into a working peer-to-peer download system.

---

## Disclaimer

This project is intended for educational and networking research purposes.

Only download or distribute files that you have the legal right to access or share.

---

## Author

**Shaun Joseph**
