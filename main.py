#!/usr/bin/env python

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import ctypes
import shutil

def set_mouse_pos(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)

def mouse_pos(root_element):
    x = root_element.winfo_pointerx()
    y = root_element.winfo_pointery()
    return x,y

def goster(element):
    x = element.winfo_rootx()
    y = element.winfo_rooty()
    return x,y

def convert_png_to_jpg(img_dir):
    for file in os.listdir(img_dir):
        if file.lower().endswith(".png"):
            png_path = os.path.join(img_dir, file)
            jpg_path = os.path.join(img_dir, os.path.splitext(file)[0] + ".jpg")
            if not os.path.exists(jpg_path): 
                img = Image.open(png_path).convert("RGB")
                img.save(jpg_path, "JPEG")

class ClassInputWindow:
    def __init__(self, master):
        self.master = master
        master.title("Define Classes")
        master.configure(bg="#2b2b2b")

        tk.Label(master, text="Enter the classes separated by commas (e.g., person, car, dog):", bg="#2b2b2b", fg="white").pack(padx=10, pady=10)
        self.entry = tk.Entry(master, width=40, bg="#3c3f41", fg="white", insertbackground="white")
        self.entry.pack(padx=10, pady=5)
        self.entry.focus_set()
        self.entry.focus_force()
        self.entry.bind("<Return>", lambda event: self.start_labeling())

        self.start_button = tk.Button(master, text="Start", command=self.start_labeling, bg="#4a90e2", fg="white", activebackground="#357ABD")
        self.start_button.pack(pady=10)

    def start_labeling(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter at least one class!")
            return
        print(text)
        classes = [c.strip() for c in text.split(",") if c.strip()]
        if not classes:
            messagebox.showwarning("Warning", "No valid class found!")
            return

        self.master.destroy()
        root = tk.Tk()
        app = YoloLabelTool(root, classes)
        root.mainloop()


class YoloLabelTool:
    def __init__(self, master, class_list):
        self.master = master
        self.master.title("47's YOLO Dataset Labeling Tool")
        self.master.configure(bg="#2b2b2b")

        self.class_list = class_list
        self.selected_class = tk.StringVar(value=self.class_list[0])
        self.class_map = {name: idx for idx, name in enumerate(self.class_list)}

        self.img_dir = filedialog.askdirectory(title="Select the folder containing the images")
        if not self.img_dir:
            messagebox.showerror("Error", "No image folder selected, the program will close.")
            self.master.destroy()
            return
        print(f"Secilen Klasor: {self.img_dir} +=+=+")
        convert_png_to_jpg(self.img_dir)  

        self.image_files = [f for f in os.listdir(self.img_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
        self.image_files.sort()

        self.labels_dir = self.img_dir.rstrip("/\\") + "_labels"
        os.makedirs(self.labels_dir, exist_ok=True)

        self.index = 0
        self.shapes = []
        self.class_ids = []

        self.canvas = tk.Canvas(master, cursor="cross", bg="#1e1e1e")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.save_class_and_yaml_minimal()

        control_frame = tk.Frame(master, bg="#2b2b2b")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(control_frame, text="Class:", bg="#2b2b2b", fg="white").pack(side=tk.LEFT, padx=(10, 2))
        self.class_dropdown = ttk.Combobox(control_frame, textvariable=self.selected_class, values=self.class_list, state="readonly", width=15)
        self.class_dropdown.pack(side=tk.LEFT)

        self.clear_button = tk.Button(control_frame, text="Clear Selections (R)", command=self.clear_selections, bg="#4a90e2", fg="white", activebackground="#357ABD")
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_button = tk.Button(control_frame, text="Next Image (E)", command=self.save_and_next, bg="#4a90e2", fg="white", activebackground="#357ABD")
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.on_click)
        self.update_focus_debug()

        self.start_x = self.start_y = 0
        self.current_rect = None
        
        self.master.focus_set() 
        self.master.bind("<e>", lambda event: self.save_and_next())
        self.master.bind("<r>", lambda event: self.clear_selections())

        self.load_image()
        self.class_dropdown.focus_set()
        self.class_dropdown.focus_force()

    def save_class_and_yaml_minimal(self):
        base_dir = os.path.dirname(self.img_dir.rstrip("/\\"))
        classes_path = os.path.join(base_dir, "classes.txt")
        yaml_path = os.path.join(base_dir, "data.yaml")

        with open(classes_path, "w", encoding="utf-8") as f:
            for c in self.class_list:
                f.write(c + "\n")

        train_dir = os.path.join(base_dir, "train")
        val_dir = os.path.join(base_dir, "val")

        names_str = "[" + ", ".join(f"'{c}'" for c in self.class_list) + "]"

        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(f"train: {train_dir}\n")
            f.write(f"val: {val_dir}\n")
            f.write(f"nc: {len(self.class_list)}\n")
            f.write(f"names: {names_str}\n")

        print(f"Classes and YAML files have been saved to the {base_dir} directory")


    def update_focus_debug(self):
        focused_widget = self.master.focus_get()
        print("🔎 Odakta olan widget:", focused_widget)
        self.master.after(1000, self.update_focus_debug)
    
    def load_image(self):
        self.shapes.clear()
        self.class_ids.clear()
        self.canvas.delete("all")

        if self.index >= len(self.image_files):
            messagebox.showinfo("Bitti", "Tüm resimler işlendi.")
            self.master.quit()
            return

        self.current_filename = self.image_files[self.index]
        img_path = os.path.join(self.img_dir, self.current_filename)
        self.original_img = Image.open(img_path).convert("RGB")
        self.w, self.h = self.original_img.size

        max_w, max_h = 1280, 720
        self.scale_x = self.scale_y = 1.0
        if self.w > max_w or self.h > max_h:
            scale = min(max_w / self.w, max_h / self.h)
            new_size = (int(self.w * scale), int(self.h * scale))
            self.img_size_of_scaled = new_size
            self.display_img = self.original_img.resize(new_size, Image.Resampling.LANCZOS)
            self.scale_x = self.scale_y = scale
        else:
            self.display_img = self.original_img
            self.img_size_of_scaled = (int(self.w), int(self.h))

        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.canvas.config(width=self.tk_img.width(), height=self.tk_img.height())

        control_height = 50
        total_width = self.tk_img.width()
        total_height = self.tk_img.height() + control_height

        min_width = 600
        min_height = 400

        final_width = max(total_width, min_width)
        final_height = max(total_height, min_height)

        self.master.geometry(f"{final_width}x{final_height}")

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

        self.master.title(f"YOLO Etiketleyici - {self.current_filename}")

    def on_click(self, event):
        self.class_dropdown.focus_set()
        self.class_dropdown.focus_force()
        x, y = event.x, event.y
        if not self.current_rect:
            self.start_x, self.start_y = x, y
            self.current_rect = self.canvas.create_rectangle(x, y, x, y, outline='red')
            self.canvas.bind("<Motion>", self.on_motion)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_motion(self, event):
        min_pos_x, min_pos_y = goster(self.canvas)
        max_pos_x, max_pos_y = (min_pos_x + self.img_size_of_scaled[0]), (min_pos_y + self.img_size_of_scaled[1])
        
        mouse_pos_x, mouse_pos_y = mouse_pos(self.master)
        
        print(f"{min_pos_x}, {min_pos_y} - {mouse_pos_x}, {mouse_pos_y} - {max_pos_x}, {max_pos_y}")
        print(f"{self.w}, {self.h} - {mouse_pos_x}, {mouse_pos_y} - {max_pos_x}, {max_pos_y}")
        
        if (mouse_pos_x < min_pos_x):
            set_mouse_pos(min_pos_x, mouse_pos_y)
        elif (mouse_pos_x > max_pos_x):
            set_mouse_pos(max_pos_x, mouse_pos_y)
            
        if (mouse_pos_y < min_pos_y):
            set_mouse_pos(mouse_pos_x, min_pos_y)
        elif (mouse_pos_y > max_pos_y):
            set_mouse_pos(mouse_pos_x, max_pos_y)
            
        if self.current_rect:
            print(self.current_rect, self.start_x, self.start_y, event.x, event.y)
            self.canvas.coords(self.current_rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        if abs(end_x - self.start_x) > 5 and abs(end_y - self.start_y) > 5:
            self.shapes.append((self.start_x, self.start_y, end_x, end_y))
            self.class_ids.append(self.selected_class.get())
        else:
            self.canvas.delete(self.current_rect)

        self.current_rect = None

    def clear_selections(self):
        self.shapes.clear()
        self.class_ids.clear()
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)


    def save_and_next(self):
        base_name = os.path.splitext(self.current_filename)[0]
        label_path = os.path.join(self.labels_dir, base_name + ".txt")

        with open(label_path, "w", encoding="utf-8") as f:
            for (x1, y1, x2, y2), class_name in zip(self.shapes, self.class_ids):
                class_id = self.class_map[class_name]
                x_center = ((x1 + x2) / 2) / (self.tk_img.width() / self.scale_x)
                y_center = ((y1 + y2) / 2) / (self.tk_img.height() / self.scale_y)
                width = abs(x2 - x1) / (self.tk_img.width() / self.scale_x)
                height = abs(y2 - y1) / (self.tk_img.height() / self.scale_y)

                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        annotated_dir = os.path.join(os.path.dirname(self.img_dir.rstrip("/\\")), f"{os.path.basename(self.img_dir)}_cp")
        os.makedirs(annotated_dir, exist_ok=True)

        src_img_path = os.path.join(self.img_dir, self.current_filename)
        dst_img_path = os.path.join(annotated_dir, self.current_filename)
        shutil.move(src_img_path, dst_img_path)

        self.index += 1
        self.load_image()

if __name__ == "__main__":
    root = tk.Tk()
    ciw = ClassInputWindow(root)
    root.mainloop()