import tkinter as tk
from utils.gui import create_gui
from utils.launch_loading import show_loading_screen


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially

    show_loading_screen()  # Show loading screen

    root.deiconify()  # Show the main window after loading screen
    root.title("Images")

    create_gui(root)

    # root 宽高设置
    root.minsize(600, 400)  # 设置最小宽度为600像素，最小高度为400像素
    # 居中
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 600
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
