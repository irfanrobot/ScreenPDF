import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import keyboard
import time
from PIL import Image, ImageGrab
import os

# Initialize Pillow plugins to prevent KeyError: 'JPEG'
Image.init()

class ScreenPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoPDF Screen Printer")
        self.root.geometry("400x300")
        
        self.rect_coords = None
        self.next_btn_coord = None
        self.screenshots = []
        
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="AutoPDF Screen Printer", font=("Arial", 16)).pack(pady=10)
        
        # Select Area Button
        self.btn_select_area = tk.Button(self.root, text="Select Printing Area", command=self.select_area)
        self.btn_select_area.pack(pady=5)
        self.lbl_area = tk.Label(self.root, text="Area: Not Selected")
        self.lbl_area.pack()
        
        # Select Next Button
        self.btn_select_next = tk.Button(self.root, text="Select Next Button", command=self.select_next_button)
        self.btn_select_next.pack(pady=5)
        self.lbl_next = tk.Label(self.root, text="Next Button: Not Selected")
        self.lbl_next.pack()
        
        # Click Delay
        frame_delay = tk.Frame(self.root)
        frame_delay.pack(pady=5)
        tk.Label(frame_delay, text="Click Delay (seconds):").pack(side=tk.LEFT)
        self.entry_delay = tk.Entry(frame_delay, width=10)
        self.entry_delay.insert(0, "1.0")
        self.entry_delay.pack(side=tk.LEFT)
        
        # Total Click
        frame_total = tk.Frame(self.root)
        frame_total.pack(pady=5)
        tk.Label(frame_total, text="Total Clicks:").pack(side=tk.LEFT)
        self.entry_total = tk.Entry(frame_total, width=10)
        self.entry_total.insert(0, "5")
        self.entry_total.pack(side=tk.LEFT)
        
        # Start Button
        self.btn_start = tk.Button(self.root, text="Start & Save to PDF", command=self.start_process, bg="green", fg="white")
        self.btn_start.pack(pady=15)

    def select_area(self):
        self.root.withdraw() # Hide main window
        
        overlay = tk.Toplevel()
        overlay.attributes('-alpha', 0.3) # Transparent
        overlay.attributes('-fullscreen', True)
        overlay.config(cursor="cross")
        
        canvas = tk.Canvas(overlay, cursor="cross", bg="gray")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        rect = None
        start_x = None
        start_y = None
        
        def on_mouse_down(event):
            nonlocal start_x, start_y, rect
            start_x = event.x
            start_y = event.y
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2, fill="black")
            
        def on_mouse_drag(event):
            nonlocal rect
            canvas.coords(rect, start_x, start_y, event.x, event.y)
            
        def on_mouse_up(event):
            end_x = event.x
            end_y = event.y
            
            x1 = min(start_x, end_x)
            y1 = min(start_y, end_y)
            x2 = max(start_x, end_x)
            y2 = max(start_y, end_y)
            
            self.rect_coords = (x1, y1, x2, y2)
            self.lbl_area.config(text=f"Area: ({x1}, {y1}) to ({x2}, {y2})")
            
            overlay.destroy()
            self.root.deiconify() # Show main window again
            
        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

    def select_next_button(self):
        messagebox.showinfo("Select Next Button", "Move your mouse to the Next button and press the 's' key to save the coordinate.")
        
        def on_key_event(e):
            if e.name == 's':
                x, y = pyautogui.position()
                self.next_btn_coord = (x, y)
                self.lbl_next.config(text=f"Next Button: ({x}, {y})")
                keyboard.unhook_all()
        
        keyboard.on_press(on_key_event)

    def start_process(self):
        if not self.rect_coords:
            messagebox.showerror("Error", "Please select a printing area first.")
            return
        if not self.next_btn_coord:
            messagebox.showerror("Error", "Please select the Next button coordinate first.")
            return
            
        try:
            delay = float(self.entry_delay.get())
            total_clicks = int(self.entry_total.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid delay or total clicks value.")
            return
            
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return
            
        self.root.withdraw()
        time.sleep(1) # Wait for window to hide
        
        try:
            self.screenshots = []
            
            for i in range(total_clicks):
                # Take screenshot
                img = ImageGrab.grab(bbox=self.rect_coords)
                # convert to RGB if it's RGBA
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                self.screenshots.append(img)
                
                if i < total_clicks - 1: # Don't click on the last iteration
                    # Click next
                    pyautogui.click(self.next_btn_coord[0], self.next_btn_coord[1])
                    # Wait
                    time.sleep(delay)
                    
            # Save to PDF
            if self.screenshots:
                self.screenshots[0].save(pdf_path, save_all=True, append_images=self.screenshots[1:])
                messagebox.showinfo("Success", f"PDF saved successfully to:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")
        finally:
            self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenPrinterApp(root)
    root.mainloop()
