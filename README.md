# SVM (Stored Visual Media)

SVM is a compact binary format for storing static images or animated
image sequences. It is designed to be lightweight, efficient, and simple
to decode.

The format uses palette quantization, run-length encoding (RLE), delta
frame patching, and zlib compression to achieve high compactness while
remaining easy to implement.

------------------------------------------------------------------------

## Overview

SVM supports:

-   Single images
-   Animated image sequences
-   256-color palette indexing
-   Run-length encoding for the first frame
-   Delta patch compression for subsequent frames
-   zlib compression for the final payload

Suitable for sprite storage, lightweight animations, custom engines, and
experimental media containers.

------------------------------------------------------------------------

## File Structure

Each `.svm` file contains:

Header: - Magic bytes: `SVM` - Version (1 byte) - Width (2 bytes, little
endian) - Height (2 bytes, little endian) - Frame count (1 byte) - Frame
delay in milliseconds (2 bytes) - 768-byte palette (256 × RGB)

Payload: - RLE-compressed first frame - Delta patch data for subsequent
frames - Entire payload compressed with zlib

All frames must have identical dimensions.

------------------------------------------------------------------------

## Converting Images

Example (single image):

    python convert.py image.png image.svm

Example (animation):

    python convert.py frame1.png frame2.png frame3.png animation.svm

The last argument is the output file. All preceding arguments are input
frames in playback order.

------------------------------------------------------------------------

## Viewer Features

-   Opens `.svm` files
-   Plays animations
-   Zoom via mouse wheel
-   Click-and-drag panning
-   Open file location
-   Borderless modern window
-   Custom icon support

------------------------------------------------------------------------

## Compiling the Viewer (Windows)

Install PyInstaller:

    pip install pyinstaller

Build:

    pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.png;." read.py

The executable will appear in:

    dist/read.exe

You may rename it (e.g., SVMViewer.exe).

------------------------------------------------------------------------

## Setting SVM as Default Application (Windows)

1.  Right-click a `.svm` file.
2.  Select "Open with".
3.  Click "Choose another app".
4.  Click "More apps".
5.  Select "Look for another app on this PC".
6.  Browse to your compiled executable.
7.  Check "Always use this app to open .svm files".
8.  Click OK.

Double-clicking `.svm` files will now open in your viewer.

------------------------------------------------------------------------

## Requirements

-   Python 3.10+
-   Pillow
-   tkinter (standard library)
-   zlib (standard library)
-   struct (standard library)

------------------------------------------------------------------------

## Limitations

-   Maximum 256 colors
-   All frames must share identical dimensions
-   Global frame delay only
-   No native alpha channel storage

------------------------------------------------------------------------

SVM is intended as a compact experimental media container prioritizing
simplicity and size efficiency.
