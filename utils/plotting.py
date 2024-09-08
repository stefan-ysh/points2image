import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import tkinter as tk
from tkinter import colorchooser, Toplevel
from utils.image_processing import gaussian_filter


def show_3d_plot(img):
    # Normalize the image
    Z = img.astype(np.float32)  # 修改这一行
    Z = (Z - Z.min()) / (Z.max() - Z.min())

    # Invert the values so that ridges are higher than valleys
    Z = 1 - Z

    # Enhance contrast
    Z = np.power(Z, 0.5)

    # Apply Gaussian smoothing
    Z = gaussian_filter(Z, sigma=1)

    # Create a grid
    y, x = np.mgrid[:Z.shape[0], :Z.shape[1]]

    # Create PyVista grid
    grid = pv.StructuredGrid(x.astype(np.float32), y.astype(np.float32), (Z * 50).astype(np.float32))  # 修改这一行
    grid["elevation"] = Z.ravel(order="F")

    # Create PyVista plotter
    p = pv.Plotter()

    # Function to update the color map
    def update_color(color_or_cmap):
        if isinstance(color_or_cmap, str) and color_or_cmap in plt.colormaps():
            # If it's a valid colormap name, use it directly
            cmap = color_or_cmap
        else:
            # If it's a color, create a custom colormap
            try:
                rgb = mcolors.to_rgb(color_or_cmap)
                cmap = plt.cm.colors.LinearSegmentedColormap.from_list(
                    "custom", [(1, 1, 1), rgb])
            except ValueError:
                print(
                    f"Invalid color or colormap: {color_or_cmap}. Using default.")
                cmap = 'coolwarm'

        p.add_mesh(grid, cmap=cmap, smooth_shading=True,
                   specular=1, specular_power=15)
        p.render()

    # Create a color chooser function
    def choose_color():
        color_window = tk.Toplevel()
        color_window.withdraw()
        color_window.attributes('-topmost', True)
        color = colorchooser.askcolor(
            title="Choose color for 3D plot", parent=color_window)[1]
        color_window.destroy()
        if color:
            update_color(color)

    # Add a key event to open color chooser
    p.add_key_event('c', choose_color)

    # Initial plot with default colormap
    update_color('coolwarm')

    # Set up lighting for better 3D effect
    light = pv.Light(position=(0, 0, 1), focal_point=(0, 0, 0), intensity=0.7)
    p.add_light(light)

    # Set camera position for a view similar to the image
    p.camera_position = [(grid.bounds[1]*0.7, grid.bounds[3]*1.3, grid.bounds[5]*2),
                         (grid.center[0], grid.center[1], 0),
                         (0, 1, 0)]

    # Adjust the camera zoom
    p.camera.zoom(1.2)

    # Add axes
    p.add_axes()

    # Add text to inform user about the color change option
    p.add_text("Press 'c' to change color", font_size=12)

    # Show the plot
    p.show()
