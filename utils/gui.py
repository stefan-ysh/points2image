import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from utils.file_operations import import_and_draw_images, save_image
from utils.plotting import show_3d_plot
import time

def create_gui(root):
    import_button = tk.Button(root, text="Import Data", command=lambda: import_and_draw_images(root))
    import_button.pack(pady=20)

    image_frame = tk.Frame(root)
    image_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Display initial message
    initial_message = tk.Label(image_frame, text="Please upload data to display images", font=("Arial", 16))
    initial_message.pack(expand=True)

    # Add a small delay before binding the <Configure> event
    root.after(100, lambda: root.bind("<Configure>", lambda event: schedule_update(root)))

    return import_button, image_frame

def show_images(root, images):
    image_frame = root.nametowidget('.!frame')
    for widget in image_frame.winfo_children():
        widget.destroy()

    if not images:
        message_label = tk.Label(image_frame, text="Please upload data to display images", font=("Arial", 16))
        message_label.pack(expand=True)
        return

    num_images = len(images)
    
    if num_images == 1:
        # For a single image, use pack to center it
        frame = tk.Frame(image_frame, borderwidth=1, relief="solid")
        frame.pack(expand=True, padx=10, pady=10)
        
        container = tk.Frame(frame)
        container.pack(expand=True, fill=tk.BOTH)
        
        # Create a header frame for filename and buttons
        header_frame = tk.Frame(container)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.grid_columnconfigure(0, weight=1)  # Make filename column expandable
        
        img, filename = images[0]
        
        # Add filename to the left
        filename_label = tk.Label(header_frame, text=filename, bg='white', fg='black', anchor='w')
        filename_label.grid(row=0, column=0, sticky='ew')
        
        # Add buttons to the right
        show_3d_button = tk.Button(header_frame, text="3D Model", command=lambda img=img, filename=filename: show_3d_plot(img, filename), width=10)
        show_3d_button.grid(row=0, column=1, padx=(0, 5))
        
        save_button = tk.Button(header_frame, text="Save Image",
                                command=lambda img=img, filename=filename: save_image(img, filename), width=10)
        save_button.grid(row=0, column=2, padx=(0, 5))
        
        # Image label
        image_label = tk.Label(container)
        image_label.pack(expand=True, fill=tk.BOTH)
        image_label.original_image = Image.fromarray(img)
        image_label.filename = filename
    else:
        # For multiple images, use grid layout
        num_cols = min(3, num_images)
        num_rows = (num_images + num_cols - 1) // num_cols

        for i, (img, filename) in enumerate(images):
            frame = tk.Frame(image_frame, borderwidth=1, relief="solid")
            frame.grid(row=i//num_cols, column=i % num_cols, padx=10, pady=10, sticky="nsew")

            container = tk.Frame(frame)
            container.pack(expand=True, fill=tk.BOTH)

            # Create a header frame for filename and buttons
            header_frame = tk.Frame(container)
            header_frame.pack(side=tk.TOP, fill=tk.X)
            header_frame.grid_columnconfigure(0, weight=1)  # Make filename column expandable
            
            # Add filename to the left
            filename_label = tk.Label(header_frame, text=filename, bg='white', fg='black', anchor='w')
            filename_label.grid(row=0, column=0, sticky='ew')
            
            # Add buttons to the right
            show_3d_button = tk.Button(header_frame, text="3D Model", command=lambda img=img, filename=filename: show_3d_plot(img, filename), width=10)
            show_3d_button.grid(row=0, column=1, padx=(0, 5))
            
            save_button = tk.Button(header_frame, text="Save Image",
                                    command=lambda img=img, filename=filename: save_image(img, filename), width=10)
            save_button.grid(row=0, column=2, padx=(0, 5))

            # Image label
            image_label = tk.Label(container)
            image_label.pack(expand=True, fill=tk.BOTH)
            image_label.original_image = Image.fromarray(img)
            image_label.filename = filename

        # Configure grid to expand with window
        for i in range(num_cols):
            image_frame.grid_columnconfigure(i, weight=1)
        for i in range(num_rows):
            image_frame.grid_rowconfigure(i, weight=1)

    # Initial update of images
    update_root_images(root)

def update_root_images(root):
    image_frame = root.nametowidget('.!frame')
    frame_width = image_frame.winfo_width()
    frame_height = image_frame.winfo_height()

    children = image_frame.winfo_children()
    num_images = len(children)
    
    if num_images == 0:
        return
    elif num_images == 1:
        frame = children[0]
        if not frame.winfo_children():
            return  # Skip if the frame has no children
        container = frame.winfo_children()[0]
        if len(container.winfo_children()) < 2:
            return  # Skip if the container doesn't have enough children
        image_label = container.winfo_children()[-1]  # The last child is now the image label
        
        if hasattr(image_label, 'original_image'):
            pil_img = image_label.original_image.copy()
            
            # Calculate the scaling factor to fit within the available space while maintaining aspect ratio
            width_ratio = (frame_width - 20) / pil_img.width
            height_ratio = (frame_height - 40) / pil_img.height
            scale_factor = min(width_ratio, height_ratio)
            
            new_size = (int(pil_img.width * scale_factor), int(pil_img.height * scale_factor))
            
            if not hasattr(image_label, 'current_size') or image_label.current_size != new_size:
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                
                image_label.configure(image=tk_img)
                image_label.image = tk_img  # Keep a reference
                image_label.current_size = new_size
    else:
        num_cols = min(3, num_images)
        num_rows = (num_images + num_cols - 1) // num_cols

        max_img_width = max(frame_width // num_cols - 20, 1)  # 20 pixels for padding
        max_img_height = max(frame_height // num_rows - 40, 1)  # 40 pixels for padding and filename

        for frame in children:
            if isinstance(frame, tk.Frame):
                if not frame.winfo_children():
                    continue  # Skip if the frame has no children
                container = frame.winfo_children()[0]
                if len(container.winfo_children()) < 2:
                    continue  # Skip if the container doesn't have enough children
                image_label = container.winfo_children()[-1]  # The last child is now the image label
                
                if hasattr(image_label, 'original_image'):
                    pil_img = image_label.original_image.copy()
                    
                    # Calculate the scaling factor to fit within the available space while maintaining aspect ratio
                    width_ratio = max_img_width / pil_img.width
                    height_ratio = max_img_height / pil_img.height
                    scale_factor = min(width_ratio, height_ratio)

                    new_size = (int(pil_img.width * scale_factor), int(pil_img.height * scale_factor))
                    
                    if not hasattr(image_label, 'current_size') or image_label.current_size != new_size:
                        pil_img = pil_img.resize(new_size, Image.LANCZOS)
                        tk_img = ImageTk.PhotoImage(pil_img)
                        
                        image_label.configure(image=tk_img)
                        image_label.image = tk_img  # Keep a reference
                        image_label.current_size = new_size

# Debounce mechanism
last_update_time = 0
update_scheduled = False

def schedule_update(root):
    global last_update_time, update_scheduled
    current_time = time.time()
    
    if not update_scheduled:
        update_scheduled = True
        root.after(200, lambda: check_and_update(root, current_time))

def check_and_update(root, scheduled_time):
    global last_update_time, update_scheduled
    update_scheduled = False
    
    if scheduled_time > last_update_time:
        last_update_time = scheduled_time
        update_root_images(root)
