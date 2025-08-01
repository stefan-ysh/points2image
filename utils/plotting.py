import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from utils.image_processing import GaussianFilter
import random


class Plot3D:
    def __init__(self, img, filename, theme='document'):
        self.img = img
        self.filename = filename
        self.themes = [pv.themes.Theme(), pv.themes.DocumentTheme(), pv.themes.DarkTheme(), pv.themes.ParaViewTheme()]
        self.current_theme_index = 0
        self.change_theme(theme)
        self.grid = None
        self.default_colors = ["#3B4CC0", "#6788EE", "#B4B4B4", "#EA8169", "#B40426"]
        self.color_list = self.default_colors.copy()
        self.color_window = None
        self.temp_color_list = []
        self.render_mode = 'surface'
        self.render_mode_text = None
        self.elevation_scale = 50  # Default scale factor

    def change_theme(self, theme):
        if isinstance(theme, str):
            if theme == 'document':
                self.current_theme_index = 1
            elif theme == 'dark':
                self.current_theme_index = 2
            elif theme == 'paraview':
                self.current_theme_index = 3
            else:
                self.current_theme_index = 0
        self.p = pv.Plotter(theme=self.themes[self.current_theme_index], window_size=[1024, 768])
        self.p.window_size = [1024, 768]
        self.p.add_title(self.filename, font_size=12)

    def cycle_theme(self):
        old_theme_index = self.current_theme_index
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        new_theme = self.themes[self.current_theme_index]

        # only change the theme when it is really changed
        if old_theme_index != self.current_theme_index:
            # Apply the new theme to the existing plotter
            self.p.theme = new_theme

            # Update the background color
            self.p.background_color = new_theme.background
            
            # Update the text color for all existing text actors
            text_color = self.get_contrasting_color(new_theme.background)
            
            for actor in self.p.renderer.GetActors():
                if actor.GetClassName() == 'vtkTextActor':
                    actor.GetTextProperty().SetColor(text_color)
            
            # Update axes colors if present
            for actor in self.p.renderer.GetActors():
                if isinstance(actor, pv.AxesActor):
                    for axis in [actor.GetXAxisCaptionActor2D(), actor.GetYAxisCaptionActor2D(), actor.GetZAxisCaptionActor2D()]:
                        axis.GetCaptionTextProperty().SetColor(text_color)
            
            # Update title color
            self.update_title_color(text_color)
            
            # Force a redraw of the scene
            self.p.render()
            
            print(f"Theme changed to: {type(new_theme).__name__}")
        else:
            print("Theme unchanged")

    def get_contrasting_color(self, background_color):
        # Convert background color to brightness
        brightness = np.dot(background_color[:3], [0.299, 0.587, 0.114])
        
        # Return white if background is dark, otherwise return black
        return (1, 1, 1) if brightness < 0.5 else (0, 0, 0)

    def update_title_color(self, color):
        # Find and update the color of the title actor
        for actor in self.p.renderer.GetActors():
            if actor.GetClassName() == 'vtkTextActor':
                # Assume the first text actor is the title
                actor.GetTextProperty().SetColor(color)
                break

    def preprocess_image(self):
        Z = self.img.astype(np.float32)
        Z = (Z - Z.min()) / (Z.max() - Z.min())
        Z = 1 - Z
        Z = np.sqrt(Z)  # faster than np.power(Z, 0.5)
        Z = GaussianFilter(sigma=1).apply(Z)
        return Z

    def create_grid(self, Z):
        y, x = np.mgrid[: Z.shape[0], : Z.shape[1]]
        self.grid = pv.StructuredGrid(
            x.astype(np.float32), y.astype(np.float32), (Z * self.elevation_scale).astype(np.float32)
        )
        self.grid["elevation"] = Z.ravel(order="F")

    def update_elevation(self, scale):
        self.elevation_scale = scale
        Z = self.grid["elevation"].reshape(self.img.shape, order="F")
        
        # Recreate the grid with the new elevation scale
        y, x = np.mgrid[: Z.shape[0], : Z.shape[1]]
        self.grid = pv.StructuredGrid(
            x.astype(np.float32), y.astype(np.float32), (Z * self.elevation_scale).astype(np.float32)
        )
        self.grid["elevation"] = Z.ravel(order="F")
        
        # Update the mesh for all render modes
        if hasattr(self, 'mesh_actor'):
            self.p.remove_actor(self.mesh_actor)
        
        self.mesh_actor = self.p.add_mesh(
            self.grid,
            scalars=self.grid["elevation"],
            cmap=self.current_cmap,
            clim=self.scalar_range,
            smooth_shading=(self.render_mode == 'surface'),
            style=self.render_mode,
            specular=1,
            specular_power=15,
        )
        
        self.p.render()

    def choose_colors(self):
        if self.color_window is not None and self.color_window.winfo_exists():
            self.color_window.lift()
            self.color_window.focus_force()
            return

        self.color_window = tk.Toplevel()
        self.color_window.title("Choose colors for 3D plot")
        self.color_window.geometry("300x400")

        self.color_buttons = []
        self.temp_color_list = self.color_list.copy()

        def add_random_color():
            color = self.generate_random_color()
            self.temp_color_list.append(color)
            update_color_buttons()

        def edit_color(index):
            new_color = self.pick_color(initial_color=self.temp_color_list[index])
            if new_color:
                self.temp_color_list[index] = new_color
                update_color_buttons()

        def remove_color(index):
            del self.temp_color_list[index]
            update_color_buttons()

        def reset_to_default():
            self.temp_color_list = self.default_colors.copy()
            self.color_list = self.default_colors.copy()
            self.update_color(self.color_list)
            self.color_window.destroy()
            self.color_window = None

        def move_color(index, direction):
            if direction == "up" and index > 0:
                self.temp_color_list[index], self.temp_color_list[index-1] = self.temp_color_list[index-1], self.temp_color_list[index]
            elif direction == "down" and index < len(self.temp_color_list) - 1:
                self.temp_color_list[index], self.temp_color_list[index+1] = self.temp_color_list[index+1], self.temp_color_list[index]
            update_color_buttons()

        def update_color_buttons():
            # Remove excess buttons
            while len(self.color_buttons) > len(self.temp_color_list):
                self.color_buttons[-1].destroy()
                self.color_buttons.pop()

            # Update existing buttons and add new ones if needed
            for i, color in enumerate(self.temp_color_list):
                if i < len(self.color_buttons):
                    # Update existing button
                    frame = self.color_buttons[i]
                    color_btn = frame.winfo_children()[0]
                    color_btn.configure(bg=color, command=lambda idx=i: edit_color(idx))
                else:
                    # Create new button
                    frame = ttk.Frame(self.color_window)
                    frame.pack(fill=tk.X, padx=5, pady=2)

                    color_btn = tk.Button(frame, bg=color, command=lambda idx=i: edit_color(idx))
                    color_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

                    up_btn = ttk.Button(frame, text="↑", width=3, command=lambda idx=i: move_color(idx, "up"))
                    up_btn.pack(side=tk.LEFT, padx=(0, 2))

                    down_btn = ttk.Button(frame, text="↓", width=3, command=lambda idx=i: move_color(idx, "down"))
                    down_btn.pack(side=tk.LEFT, padx=(0, 2))

                    remove_btn = ttk.Button(frame, text="Remove", command=lambda idx=i: remove_color(idx))
                    remove_btn.pack(side=tk.RIGHT)

                    self.color_buttons.append(frame)

                # Update button commands
                frame.winfo_children()[1].configure(command=lambda idx=i: move_color(idx, "up"))
                frame.winfo_children()[2].configure(command=lambda idx=i: move_color(idx, "down"))
                frame.winfo_children()[3].configure(command=lambda idx=i: remove_color(idx))

        def apply_colors():
            if self.validate_colors(self.temp_color_list):
                self.color_list = self.temp_color_list.copy()
                self.update_color(self.color_list)
                self.color_window.destroy()
                self.color_window = None
            else:
                tk.messagebox.showwarning("Invalid Color Selection", "Please select at least two different colors.")

        button_frame = ttk.Frame(self.color_window)
        button_frame.pack(pady=10)

        add_button = ttk.Button(button_frame, text="Add Color", command=add_random_color)
        add_button.pack(side=tk.LEFT, padx=5)

        reset_button = ttk.Button(button_frame, text="Reset", command=reset_to_default)
        reset_button.pack(side=tk.LEFT, padx=5)

        apply_button = ttk.Button(button_frame, text="Apply", command=apply_colors)
        apply_button.pack(side=tk.LEFT, padx=5)

        self.color_window.style = ttk.Style()
        update_color_buttons()
        self.color_window.protocol("WM_DELETE_WINDOW", self.on_color_window_close)
        self.color_window.grab_set()
        self.color_window.wait_window()

    def generate_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def pick_color(self, initial_color=None):
        while True:
            color = colorchooser.askcolor(title="Pick a color", initialcolor=initial_color)[1]
            if color is None:  # User cancelled
                return None
            return color


    # validate selected color_list is valid or not
    def validate_colors(self, color_list):
        '''
            1. at least two colors selected
            2. if two colors selected, they must be different
        '''
        if len(color_list) == 2:
            return color_list[0] != color_list[1]
        return len(color_list) >= 2


    def update_color(self, colors):
        if not colors or len(colors) < 2:
            print("Not enough colors selected. Using default.")
            colors = self.default_colors

        # create a custom color map with user selected colors
        self.current_cmap = plt.cm.colors.LinearSegmentedColormap.from_list("custom", colors, N=256)

        # normalize the data to the range [0, 1]
        self.scalar_range = self.grid.get_data_range("elevation")
        self.update_render_mode()

    def on_color_window_close(self):
        if self.color_window:
            self.color_window.destroy()
        self.color_window = None
        # do not apply the changes of the temporary color list
        self.temp_color_list = []

    def cycle_render_mode(self):
        modes = ['surface', 'wireframe', 'points']
        current_index = modes.index(self.render_mode)
        self.render_mode = modes[(current_index + 1) % len(modes)]
        self.update_render_mode()

    def update_render_mode(self):
        # Save current camera position
        camera_position = self.p.camera_position

        if hasattr(self, 'mesh_actor'):
            self.p.remove_actor(self.mesh_actor)
        
        self.mesh_actor = self.p.add_mesh(
            self.grid,
            scalars=self.grid["elevation"],
            cmap=self.current_cmap,
            clim=self.scalar_range,
            smooth_shading=(self.render_mode == 'surface'),
            style=self.render_mode,
            specular=1,
            specular_power=15,
        )
        
        # Restore camera position
        self.p.camera_position = camera_position
        
        # Re-add the axes and text
        self.p.add_axes()
        self.add_help_text()
        
        self.p.render()

    def add_help_text(self):
        self.p.add_text(
            "L: Change color\n"
            "X, Y, Z: Change view\n"
            "V: Reset view\n"
            "M: Change render mode\n"
            "R: Reset camera position\n"
            "T: Change theme\n"
            "Q or E: Quit\n"
            "Middle-click & drag: Move\n"
            "Slider: Adjust elevation",
            font_size=8,
        )

    def setup_plot(self):
        # disable all picking functions
        self.p.disable_picking()
        
        # Redefine 'C' key behavior to no operation
        self.p.add_key_event('c', lambda: None)
        self.p.add_key_event('C', lambda: None)
        
        # Use 'L' key to trigger color selection
        self.p.add_key_event("l", self.handle_l_key)
        self.p.add_key_event("L", self.handle_l_key)
        
        # Use 'T' key to cycle themes
        self.p.add_key_event("t", self.cycle_theme)
        self.p.add_key_event("T", self.cycle_theme)
        
        # Add 'M' key to cycle render modes
        self.p.add_key_event("m", self.cycle_render_mode)
        self.p.add_key_event("M", self.cycle_render_mode)
        
        #  Keep other keyboard events unchanged
        self.p.add_key_event("x", lambda: self.p.view_yx())
        self.p.add_key_event("X", lambda: self.p.view_yx())
        self.p.add_key_event("y", lambda: self.p.view_xz())
        self.p.add_key_event("Y", lambda: self.p.view_xz())
        self.p.add_key_event("z", lambda: self.p.view_xy())
        self.p.add_key_event("Z", lambda: self.p.view_xy())
        self.p.add_key_event("v", lambda: self.p.isometric_view())
        self.p.add_key_event("V", lambda: self.p.isometric_view())

        self.update_color(self.color_list)

        light = pv.Light(position=(0, 0, 1), focal_point=(0, 0, 0), intensity=0.7)
        self.p.add_light(light)

        # Replace the current camera position setting with isometric view
        self.p.camera_position = 'iso'
        self.p.camera.zoom(1.2)

        self.p.add_axes()
        self.add_help_text()

        # Add elevation slider
        self.p.add_slider_widget(
            self.update_elevation,
            [1, 100],
            value=self.elevation_scale,
            # title="Elevation",
            pointa=(0.98, 0.1),  # 右侧底部
            pointb=(0.98, 0.9),  # 右侧顶部
            style='modern',
            tube_width=0.02,
            interaction_event='end' 
        )

    def handle_l_key(self):
        if self.color_window is None or not self.color_window.winfo_exists():
            self.choose_colors()
        else:
            self.color_window.lift()
            self.color_window.focus_force()

    def show(self):
        Z = self.preprocess_image()
        self.create_grid(Z)
        self.setup_plot()
        self.p.show()


def show_3d_plot(img, filename):
    plot = Plot3D(img, filename)
    plot.show()
