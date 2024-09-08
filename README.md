# Points2Image

A tool for converting images to grayscale, using the OpenCV library.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/stefan-ysh/image-grayscale-converter.git
   ```

2. Install the required dependencies:

   ```
   pip install -r ./requirements.txt
   ```

## Usage

1. Run the script:

   ```
   python ./main.py
   ```

## License

MIT License

## Build

```

pyinstaller --onefile --windowed --icon ./logo.ico ./main.py -n Points2Image

> 打包文件夹
pyinstaller --onedir --windowed --icon ./logo.ico ./main.py -n Points2Image

```