# 47's YOLO Dataset Labeling Tool

A simple and user-friendly Python/Tkinter GUI tool to quickly label datasets in YOLO format.

## Features
- Enter classes separated by commas (e.g., person,car,dog)  
- Draw bounding boxes on images for object labeling  
- Automatically save labels in `.txt` files and class info in `.yaml` file  
- Clean and easy-to-use interface  

## Installation
1. Make sure Python 3.x is installed  
2. Install required libraries:  
   ```bash
   pip install tkinter opencv-python
   ```  
3. Clone or download this repository  

## Usage
1. Run the program:  
   ```bash
   python main.py
   ```  
2. Click "Select Image Folder" and choose your image directory  
3. Enter the classes in the input box separated by commas (e.g., person,car,dog)  
4. Draw bounding boxes around objects in the images  
5. Labels will be saved automatically, and the images will be moved to another directory (e.g., from train to train_cp).

## File Structure
- Image folder  
- YOLO format `.txt` files for each image  
- `classes.txt` and `data.yaml` files for class definitions  
