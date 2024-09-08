import pandas as pd
import numpy as np
from PIL import Image
import os
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

def import_task(progress_label, progress_bar, filename, file_index, total_files):
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(filename)
    else:
        raise ValueError("Unsupported file format")

    required_columns = ['X', 'Y', 'Grayscale']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(
            "The file must contain 'X', 'Y', and 'Grayscale' columns")

    min_x, max_x = df['X'].min().astype(int), df['X'].max().astype(int)
    min_y, max_y = df['Y'].min().astype(int), df['Y'].max().astype(int)

    img = np.zeros((max(max_y - min_y + 1, 1),
                   max(max_x - min_x + 1, 1)), dtype=np.uint8)

    total_rows = len(df)
    for index, row in df.iterrows():
        x, y, gray = row['X'].astype(int), row['Y'].astype(
            int), row['Grayscale'].astype(int)
        img[max_y - y, x - min_x] = gray

        # Update progress
        progress = (index + 1) / total_rows
        progress_bar['value'] = progress * 100
        progress_label.config(
            text=f"Processing file {file_index}/{total_files}, point {index + 1}/{total_rows}")
        progress_label.update()

    return img, total_rows  # Return the image and the number of points

def import_and_draw_images(root):
    filenames = filedialog.askopenfilenames(
        title="Select data files",
        filetypes=(("Excel files", "*.xlsx *.xls"),
                   ("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not filenames:
        return

    try:
        images = []
        total_files = len(filenames)
                
        # Create a progress dialog
        progress_window = tk.Toplevel(root)
        progress_window.title("")
        progress_window.geometry("400x150")

        progress_window.resizable(False, False)
        progress_window.attributes("-toolwindow", 1)
        progress_window.overrideredirect(True)
        # Disable the progress window from being interacted with
        progress_window.grab_set()

        # Center the progress window relative to the root window
        root.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - (400 // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (150 // 2)
        progress_window.geometry(f"400x150+{x}+{y}")

        # Create a frame to hold the progress bar and label
        frame = tk.Frame(progress_window, bg='#f0f0f0')
        frame.place(relx=0.5, rely=0.5, anchor='center')

        progress_label = tk.Label(frame, text="Processing files...", bg='#f0f0f0', font=("Arial", 10))
        progress_label.pack(pady=5)

        progress_bar = ttk.Progressbar(frame, length=300, mode='determinate')
        progress_bar.pack(pady=5)

        for i, filename in enumerate(filenames, 1):
            if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
                messagebox.showerror(
                    "Invalid File Format", f"The file '{os.path.basename(filename)}' is not a supported format. Please select CSV or Excel files only.")
                progress_window.destroy()
                return
            
            progress_label.config(text=f"Analysising file {i}/{total_files}")
            progress_bar['value'] = (i / total_files) * 100
            progress_window.update()

            imported_img, num_points = import_task(progress_label, progress_bar, filename, i, total_files)
            base_filename = os.path.splitext(os.path.basename(filename))[0]
            new_filename = f"{base_filename} ({num_points} points)"
            images.append((imported_img, new_filename))

        progress_window.destroy()
        from utils.gui import show_images  # Import here to avoid circular import
        show_images(root, images)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import data: {str(e)}")

def save_image(img, filename):
    # Remove file extension from the original filename
    base_filename = os.path.splitext(filename)[0]

    # Ask user for save location
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        initialfile=f"{base_filename}_processed.png"
    )

    if save_path:
        # Save the image
        Image.fromarray(img).save(save_path)
        messagebox.showinfo("Save Successful", f"Image saved as {save_path}")
