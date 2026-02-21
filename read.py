import struct
import zlib
import sys
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SVMViewer:
    def __init__(self, root, file_arg=None):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("1100x750")
        self.root.configure(bg="#0e1117")

        self.root.call("tk", "scaling", 1.5)

        self.drag_x = 0
        self.drag_y = 0

        self.topbar = tk.Frame(root, bg="#151a22", height=42)
        self.topbar.pack(fill="x")

        self.title = tk.Label(self.topbar, text="SVM Viewer", bg="#151a22", fg="#e6edf3", font=("Segoe UI", 11, "bold"))
        self.title.pack(side="left", padx=15)

        self.btn_close = tk.Label(self.topbar, text="✕", bg="#151a22", fg="#ff5c5c", font=("Segoe UI", 12))
        self.btn_close.pack(side="right", padx=15)
        self.btn_close.bind("<Button-1>", lambda e: self.root.destroy())

        self.btn_min = tk.Label(self.topbar, text="—", bg="#151a22", fg="#aaa", font=("Segoe UI", 12))
        self.btn_min.pack(side="right")
        self.btn_min.bind("<Button-1>", lambda e: self.root.iconify())

        self.topbar.bind("<ButtonPress-1>", self.start_move)
        self.topbar.bind("<B1-Motion>", self.move_window)

        self.toolbar = tk.Frame(root, bg="#10141b", height=45)
        self.toolbar.pack(fill="x")

        self.open_btn = self.make_button("Open", self.open_file)
        self.play_btn = self.make_button("Pause", self.toggle_play)
        self.loc_btn = self.make_button("Open Location", self.open_location)

        self.canvas = tk.Canvas(root, bg="#0e1117", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.frames = []
        self.current = 0
        self.playing = True
        self.delay = 100
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.file_path = None

        self.canvas.bind("<MouseWheel>", self.zoom_image)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)

        if file_arg:
            self.load_svm(file_arg)
            self.animate()

    def make_button(self, text, cmd):
        b = tk.Label(self.toolbar, text=text, bg="#1a1f29", fg="#e6edf3",
                     font=("Segoe UI", 10), padx=15, pady=6)
        b.pack(side="left", padx=10, pady=6)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(bg="#242b36"))
        b.bind("<Leave>", lambda e: b.config(bg="#1a1f29"))
        return b

    def start_move(self, e):
        self.drag_x = e.x
        self.drag_y = e.y

    def move_window(self, e):
        x = e.x_root - self.drag_x
        y = e.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("SVM Files", "*.svm")])
        if path:
            self.load_svm(path)
            self.animate()

    def open_location(self):
        if self.file_path:
            os.startfile(os.path.dirname(self.file_path))

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.config(text="Pause" if self.playing else "Play")

    def zoom_image(self, event):
        self.zoom *= 1.1 if event.delta > 0 else 0.9
        self.render_frame()

    def start_pan(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def pan(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.offset_x += dx
        self.offset_y += dy
        self.last_x = event.x
        self.last_y = event.y
        self.render_frame()

    def load_svm(self, path):
        self.file_path = path
        with open(path, "rb") as f:
            f.read(3)
            f.read(1)
            width = struct.unpack("<H", f.read(2))[0]
            height = struct.unpack("<H", f.read(2))[0]
            frame_count = struct.unpack("B", f.read(1))[0]
            self.delay = struct.unpack("<H", f.read(2))[0]
            palette = list(f.read(768))
            compressed = f.read()

        data = zlib.decompress(compressed)

        ptr = 0
        raw_frames = []

        first = bytearray()
        while len(first) < width*height:
            run, color = struct.unpack("<HB", data[ptr:ptr+3])
            first += bytes([color]) * run
            ptr += 3

        raw_frames.append(first)

        for _ in range(1, frame_count):
            patch_count = struct.unpack("<H", data[ptr:ptr+2])[0]
            ptr += 2
            frame = bytearray(raw_frames[-1])
            for _ in range(patch_count):
                start, run, color = struct.unpack("<IHB", data[ptr:ptr+7])
                ptr += 7
                for i in range(run):
                    frame[start+i] = color
            raw_frames.append(frame)

        self.frames = []
        for raw in raw_frames:
            img = Image.frombytes("P", (width, height), bytes(raw))
            img.putpalette(palette)
            self.frames.append(img.convert("RGBA"))

        self.current = 0
        self.render_frame()

    def render_frame(self):
        if not self.frames:
            return
        img = self.frames[self.current]
        w, h = img.size
        resized = img.resize((int(w*self.zoom), int(h*self.zoom)), Image.NEAREST)
        self.tk_img = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.tk_img)

    def animate(self):
        if self.frames:
            if self.playing:
                self.render_frame()
                self.current = (self.current + 1) % len(self.frames)
        self.root.after(self.delay, self.animate)

if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    
    icon_img = Image.open(resource_path("icon.png"))
    icon_photo = ImageTk.PhotoImage(icon_img)
    root.iconphoto(True, icon_photo)
    root._icon_ref = icon_photo

    app = SVMViewer(root, file_arg)
    root.mainloop()
