#!/usr/bin/env python

import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk

def run_app():
    class ImageAnnotationApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Image Annotation App")
            self.root.geometry("1200x900")

            # Initialize variables
            self.image_list = []
            self.image_index = 0
            self.current_image = None
            self.rect_start_x = None
            self.rect_start_y = None
            self.rect_id = None
            self.save_dir = "output"

            # Set up UI
            self.setup_ui()

        def setup_ui(self):
            # Top-left: Image display
            self.canvas = tk.Canvas(self.root, bg="gray")
            self.canvas.grid(row=0, column=0, sticky="nsew")
            self.canvas.bind("<Button-1>", self.start_draw)
            self.canvas.bind("<B1-Motion>", self.draw)
            self.canvas.bind("<ButtonRelease-1>", self.finalize_draw)
            self.root.bind("<Left>", self.previous_image)
            self.root.bind("<Right>", self.next_image)

            # Top-right: List widget (listA)
            self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
            self.listbox.grid(row=0, column=1, sticky="nsew")
            self.listbox.bind("<Double-1>", self.delete_text)

            # Bottom-left: Directory selection button
            self.dir_button = tk.Button(self.root, text="Select Directory", command=self.select_directory)
            self.dir_button.grid(row=1, column=0, sticky="nsew")

            # Bottom-right: buttonA for adding text to listA
            self.add_button = tk.Button(self.root, text="Add Text", command=self.add_text)
            self.add_button.grid(row=1, column=1, sticky="nsew")

            # Configure grid weights
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_rowconfigure(1, weight=0)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=1)

        def select_directory(self):
            directory = filedialog.askdirectory()
            if directory:
                self.image_list = [os.path.join(directory, f) for f in os.listdir(directory)
                                   if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif', '.tiff'))]
                self.image_index = 0
                self.show_image()

        def show_image(self):
            if self.image_list:
                img_path = self.image_list[self.image_index]
                self.current_image = Image.open(img_path)

                # Stretch image to fit canvas while maintaining aspect ratio
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                img_width, img_height = self.current_image.size
                scale = min(canvas_width / img_width, canvas_height / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                resized_image = self.current_image.resize((new_width, new_height), Image.ANTIALIAS)

                photo = ImageTk.PhotoImage(resized_image)
                self.canvas.image = photo  # Keep a reference to avoid garbage collection
                self.canvas.delete("all")
                self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=photo)

        def previous_image(self, event=None):
            if self.image_list and self.image_index > 0:
                self.image_index -= 1
                self.show_image()

        def next_image(self, event=None):
            if self.image_list and self.image_index < len(self.image_list) - 1:
                self.image_index += 1
                self.show_image()

        def start_draw(self, event):
            self.rect_start_x, self.rect_start_y = event.x, event.y

        def draw(self, event):
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(self.rect_start_x, self.rect_start_y, event.x, event.y, outline="red", width=2)

        def finalize_draw(self, event):
            if not self.current_image:
                return

            if not self.listbox.curselection():
                messagebox.showwarning("Warning", "Please select a category to save the rectangle.")
                return

            category = self.listbox.get(self.listbox.curselection())
            save_path = os.path.join(self.save_dir, category)
            os.makedirs(save_path, exist_ok=True)

            # Extract the rectangle area
            x1, y1, x2, y2 = self.rect_start_x, self.rect_start_y, event.x, event.y
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Get original image dimensions
            img_width, img_height = self.current_image.size

            # Calculate scale factors
            scale = min(canvas_width / img_width, canvas_height / img_height)
            scaled_img_width = int(img_width * scale)
            scaled_img_height = int(img_height * scale)

            # Offset for centering
            offset_x = (canvas_width - scaled_img_width) // 2
            offset_y = (canvas_height - scaled_img_height) // 2

            # Map canvas coordinates to original image coordinates
            orig_x1 = int((x1 - offset_x) / scale)
            orig_y1 = int((y1 - offset_y) / scale)
            orig_x2 = int((x2 - offset_x) / scale)
            orig_y2 = int((y2 - offset_y) / scale)

            # Ensure coordinates are within image bounds
            orig_x1 = max(0, min(orig_x1, img_width))
            orig_y1 = max(0, min(orig_y1, img_height))
            orig_x2 = max(0, min(orig_x2, img_width))
            orig_y2 = max(0, min(orig_y2, img_height))

            # Crop the image
            cropped = self.current_image.crop((orig_x1, orig_y1, orig_x2, orig_y2))

            # Save the cropped image with a unique name
            existing_files = os.listdir(save_path)
            image_number = len([f for f in existing_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]) + 1
            cropped_name = f"img_{image_number}.png"
            cropped.save(os.path.join(save_path, cropped_name))

        def add_text(self):
            text = simpledialog.askstring("Add Text", "Enter text to add:")
            if text:
                self.listbox.insert(tk.END, text)

        def delete_text(self, event):
            selected = self.listbox.curselection()
            if selected:
                self.listbox.delete(selected)

    # Create root window
    root = tk.Tk()
    app = ImageAnnotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()

