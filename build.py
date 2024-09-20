import PyInstaller.__main__
import os

def build_app():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the PyInstaller command arguments
    args = [
        'main.py',
        '--onedir',
        '--windowed',
        '--icon', './logo.ico',
        '--name', 'Points2Image',
        '--add-data', f'{current_dir}/logo.ico:.',
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build_app()
