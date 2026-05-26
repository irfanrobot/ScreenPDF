# AutoScreenPDF (AutoPDF Screen Printer)

Python-based automated utility to take multiple sequential screenshots of a selected screen area and convert them into a single PDF document. This project is a Python recreation of the [plainprinter](https://github.com/plainlab/plainprinter) tool, now featuring scroll-based capture.

## Features

- **Select Printing Area**: Draw a red rectangle over a transparent overlay to select the screen area you want to screenshot.
- **Two Capture Modes**:
  - **Button Mode**: Automate navigation by clicking a next-page button at a specific coordinate (saves X, Y mouse position via hotkey).
  - **Scroll Mode**: Automate navigation by simulating keyboard keypresses (e.g. `pagedown`, `space`, `down` arrow) or mouse scroll ticks (e.g., `-100` ticks).
- **Auto-Focus Target**: In Scroll Mode, automatically clicks the center of the printing area once before starting to ensure the target window has keyboard focus.
- **Configurable Click Delay**: Set a delay (in seconds) between capturing a page and scrolling/clicking to allow contents to load properly.
- **Total Clicks / Pages**: Choose how many screenshots you want to take.
- **Auto-Export to PDF**: Compiles all screenshots directly into a single PDF file of your choice.
- **Local Configurations**: Automatically saves and loads your last configurations from `config.json`.
- **Easy Cancellation**: Press the `ESC` key at any point while the process is running to cancel instantly.

## Prerequisites

- Python 3.8 or above
- Windows OS (recommended, uses OS-specific keyboard hooks and screen grab functions)

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/irfanrobot/ScreenPDF.git
   cd ScreenPDF
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - On Windows CMD:
     ```cmd
     .\venv\Scripts\activate
     ```
   - On Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application**:
   Double click the `run.bat` file or run:
   ```bash
   python main.py
   ```
2. **Select Mode**: Choose between **Button Mode** or **Scroll Mode** at the top of the GUI.
3. **Select Printing Area**: Click "Select on Screen" and drag your mouse to draw a box around the area you want to screenshot.
4. **Configure Navigation**:
   - **For Button Mode**: Place your mouse pointer over the "Next Page" button and press the `s` key to save the position.
   - **For Scroll Mode**: Select either **Key Press** (e.g., `pagedown`) or **Mouse Scroll** (e.g., `-100` ticks to scroll down).
5. Set the **Delay (seconds)** and **Total Clicks**.
6. Click **Start & Save to PDF**:
   - Choose where to save your output PDF file.
   - The application will automatically save your settings, hide itself, and execute the captures.
   - Press **ESC** if you need to cancel.

## License

This project is licensed under the MIT License.
