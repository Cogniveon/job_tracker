import os
import tkinter as tk
from tkinter import Label, filedialog, messagebox

import cv2
from PIL import Image, ImageTk


class FrameExtractor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Frame Extractor")
        self.geometry("1280x720")

        # Video path entry
        self.video_path_entry = tk.Entry(self, width=40)
        self.video_path_entry.pack()

        # Browse button
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        # Extract button
        self.extract_button = tk.Button(
            self, text="Start", command=self.start_extraction
        )
        self.extract_button.pack()

        # Frame Label
        self.frame_label = Label(self)
        self.frame_label.pack()

        # Frame Counter
        self.frame_counter = tk.Label(self, text="Frame: 0")
        self.frame_counter.pack()

        # Save Frame Button
        self.save_frame_button = tk.Button(
            self, text="Save Frame", command=self.save_frame
        )
        self.save_frame_button.pack()

        # Skip Frame Button
        self.skip_frame_button = tk.Button(
            self, text="Skip Frame", command=self.next_frame
        )
        self.skip_frame_button.pack()

        self.cap = None
        self.current_frame = None
        self.frame_number = 46

        # Keyboard Bindings
        self.bind("<space>", lambda event: self.next_frame())
        self.bind("<Return>", lambda event: self.save_frame())

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            # filetypes=[("Video files", "*.mp4;*.avi;*.mov")]
        )
        self.video_path_entry.delete(0, tk.END)
        self.video_path_entry.insert(0, file_path)

    def start_extraction(self):
        video_path = self.video_path_entry.get()
        if not video_path:
            return

        self.cap = cv2.VideoCapture(video_path)
        self.next_frame()

    def next_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            messagebox.showinfo("End of Video", "No more frames in the video.")
            return

        self.current_frame = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = frame.resize((480, 640), Image.Resampling.LANCZOS)
        frame = ImageTk.PhotoImage(frame)

        self.frame_label.configure(image=frame)
        self.frame_label.image = frame

        self.frame_counter.configure(text=f"Frame: {self.frame_number}")

    def save_frame(self):
        if self.current_frame is not None:
            folder_path = "extracted_frames"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            self.frame_number += 1
            cv2.imwrite(
                os.path.join(folder_path, f"frame_{self.frame_number}.jpg"),
                self.current_frame,
            )
            self.next_frame()


app = FrameExtractor()
app.mainloop()
