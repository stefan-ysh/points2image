# Points2Image

A tool for converting point cloud data to grayscale images and visualizing them in 3D, using Python and various libraries.

## Features

- Import CSV and Excel files containing point cloud data
- Convert point cloud data to grayscale images
- Display multiple images in a grid layout
- 3D visualization of the grayscale images
- Save processed images

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/stefan-ysh/points2image.git
   ```

2. Navigate to the project directory:

   ```
   cd points2image
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

## Usage

1. Run the script:

   ```
   python main.py
   ```

2. Use the "Import Data" button to select CSV or Excel files containing point cloud data.
3. The application will process the files and display the resulting grayscale images.
4. Use the "3D Model" button to view a 3D representation of each image.
5. Use the "Save Image" button to save processed images.

## 3D Visualization Controls

- C: Change color
- X, Y, Z: Change view
- V: Reset view
- W: Wireframe mode
- S: Smooth shading
- R: Reset camera position
- Q or E: Quit
- Middle-click & drag: Move

## Building Executable

> **Note:** If you want to build a standalone executable, you need to install `PyInstaller` first.And open a new terminal in the project directory.

```
pip install pyinstaller
```

To create a standalone executable:

```
pyinstaller --onefile --windowed --icon ./logo.ico ./main.py -n Points2Image
```

To create a folder with all dependencies:

```
pyinstaller --onedir --windowed --icon ./logo.ico ./main.py -n Points2Image
```

## Dependencies

- matplotlib
- numpy
- pandas
- Pillow
- pyvista
- tkinter

For a complete list of dependencies, see the `requirements.txt` file.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
