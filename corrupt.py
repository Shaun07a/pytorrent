path = "downloads/large_sample.txt"

with open(path, "r+b") as f:
    f.seek(524288)
    original = f.read(1)

    f.seek(524288)

    if original == b"A":
        f.write(b"B")
    else:
        f.write(b"A")

print("Piece 2 corrupted.")