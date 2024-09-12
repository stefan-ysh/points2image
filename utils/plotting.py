import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import tkinter as tk
from tkinter import colorchooser
from utils.image_processing import gaussian_filter


class Plot3D:
    def __init__(self, img):
        self.img = img
        self.p = pv.Plotter()
        self.grid = None

    def preprocess_image(self):
        Z = self.img.astype(np.float32)
        Z = (Z - Z.min()) / (Z.max() - Z.min())
        Z = 1 - Z
        Z = np.power(Z, 0.5)
        Z = gaussian_filter(Z, sigma=1)
        return Z

    def create_grid(self, Z):
        y, x = np.mgrid[: Z.shape[0], : Z.shape[1]]
        self.grid = pv.StructuredGrid(
            x.astype(np.float32), y.astype(np.float32), (Z * 50).astype(np.float32)
        )
        self.grid["elevation"] = Z.ravel(order="F")

    def update_color(self, color_or_cmap):
        if isinstance(color_or_cmap, str) and color_or_cmap in plt.colormaps():
            cmap = color_or_cmap
        else:
            try:
                rgb = mcolors.to_rgb(color_or_cmap)
                cmap = plt.cm.colors.LinearSegmentedColormap.from_list(
                    "custom", [(1, 1, 1), rgb]
                )
            except ValueError:
                print(f"Invalid color or colormap: {color_or_cmap}. Using default.")
                cmap = "coolwarm"

        self.p.add_mesh(
            self.grid, cmap=cmap, smooth_shading=True, specular=1, specular_power=15
        )
        self.p.render()

    def choose_color(self):
        color_window = tk.Toplevel()
        color_window.withdraw()
        color_window.attributes("-topmost", True)
        color = colorchooser.askcolor(
            title="Choose color for 3D plot", parent=color_window
        )[1]
        color_window.destroy()
        if color:
            self.update_color(color)

    def setup_plot(self):
        self.p.add_key_event("c", self.choose_color)
        self.p.add_key_event("C", self.choose_color)
        self.p.add_key_event("x", lambda: self.p.view_yx())
        self.p.add_key_event("X", lambda: self.p.view_yx())
        self.p.add_key_event("y", lambda: self.p.view_xz())
        self.p.add_key_event("Y", lambda: self.p.view_xz())
        self.p.add_key_event("z", lambda: self.p.view_xy())
        self.p.add_key_event("Z", lambda: self.p.view_xy())

        self.update_color("coolwarm")

        light = pv.Light(position=(0, 0, 1), focal_point=(0, 0, 0), intensity=0.7)
        self.p.add_light(light)

        self.p.camera_position = [
            (
                self.grid.bounds[1] * 0.7,
                self.grid.bounds[3] * 1.3,
                self.grid.bounds[5] * 2,
            ),
            (self.grid.center[0], self.grid.center[1], 0),
            (0, 1, 0),
        ]
        self.p.camera.zoom(1.2)

        self.p.add_axes()
        self.p.add_text(
            "C: Change color\n"
            "X, Y, Z: Change view\n"
            "V: Reset view\n"
            "W: Wireframe mode\n"
            "S: Smooth shading\n"
            "R: Reset camera position\n"
            "Q or E: Quit\n"
            "Middle-click & drag: Move\n",
            font_size=8,
        )

    def show(self):
        Z = self.preprocess_image()
        self.create_grid(Z)
        self.setup_plot()
        self.p.show()


def show_3d_plot(img):
    plot = Plot3D(img)
    plot.show()
