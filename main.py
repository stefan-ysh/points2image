import tkinter as tk
from tkinter import messagebox
from utils.gui import create_gui
from utils.launch_loading import show_loading_screen

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window initially

    def setup(self):
        show_loading_screen()  # Show loading screen

        self.root.deiconify()  # Show the main window after loading screen
        self.root.title("Images")

        create_gui(self.root)

        # 设置窗口大小和位置
        self.root.minsize(600, 400)
        self.center_window(800, 600)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Exit", "Are you sure to exit?"):
            self.root.destroy()

def main():
    app = Application()
    app.setup()
    app.run()

if __name__ == "__main__":
    main()
