import struct
import zlib
from PIL import Image
import sys

def rle_encode(data):
    out = bytearray()
    i = 0
    while i < len(data):
        run = 1
        while i+run < len(data) and data[i] == data[i+run] and run < 65535:
            run += 1
        out += struct.pack("<HB", run, data[i])
        i += run
    return out

def diff_frames(prev, curr):
    patches = []
    i = 0
    while i < len(curr):
        if curr[i] != prev[i]:
            start = i
            color = curr[i]
            run = 1
            while i+run < len(curr) and curr[i+run] == color and prev[i+run] != color:
                run += 1
            patches.append((start, run, color))
            i += run
        else:
            i += 1
    return patches

def convert(images, output, delay=100):
    frames = []
    for path in images:
        img = Image.open(path).convert("RGBA")
        img = img.quantize(colors=256, method=Image.FASTOCTREE)
        frames.append(img)

    width, height = frames[0].size
    palette = frames[0].getpalette()[:768]
    raw_frames = [f.tobytes() for f in frames]

    payload = bytearray()

    payload += rle_encode(raw_frames[0])

    for i in range(1, len(raw_frames)):
        patches = diff_frames(raw_frames[i-1], raw_frames[i])
        payload += struct.pack("<H", len(patches))
        for start, run, color in patches:
            payload += struct.pack("<IHB", start, run, color)

    compressed = zlib.compress(payload, 9)

    with open(output, "wb") as f:
        f.write(b"SVM")
        f.write(struct.pack("B", 1))
        f.write(struct.pack("<H", width))
        f.write(struct.pack("<H", height))
        f.write(struct.pack("B", len(frames)))
        f.write(struct.pack("<H", delay))
        f.write(bytes(palette))
        f.write(compressed)

if __name__ == "__main__":
    convert(sys.argv[1:-1], sys.argv[-1])
