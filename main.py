import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import keyboard
import time
from PIL import Image, ImageGrab
import os
import json

# Initialize Pillow plugins to prevent KeyError: 'JPEG'
Image.init()

class ScreenPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoPDF Screen Printer")
        self.root.geometry("450x400")
        
        self.screenshots = []
        self.config_file = "config.json"
        
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        tk.Label(self.root, text="AutoPDF Screen Printer", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Frame Area
        frame_area = tk.LabelFrame(self.root, text="1. Printing Area (x1, y1, x2, y2)", padx=10, pady=5)
        frame_area.pack(fill="x", padx=15, pady=5)
        
        self.btn_select_area = tk.Button(frame_area, text="Select on Screen", command=self.select_area)
        self.btn_select_area.pack(side=tk.LEFT, padx=5)
        
        self.entry_area = tk.Entry(frame_area)
        self.entry_area.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Frame Next Button
        frame_next = tk.LabelFrame(self.root, text="2. Next Button Position (x, y)", padx=10, pady=5)
        frame_next.pack(fill="x", padx=15, pady=5)
        
        self.btn_select_next = tk.Button(frame_next, text="Select on Screen", command=self.select_next_button)
        self.btn_select_next.pack(side=tk.LEFT, padx=5)
        
        self.entry_next = tk.Entry(frame_next)
        self.entry_next.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Click Delay & Total Clicks Frame
        frame_settings = tk.Frame(self.root)
        frame_settings.pack(fill="x", padx=15, pady=5)
        
        # Click Delay
        frame_delay = tk.Frame(frame_settings)
        frame_delay.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_delay, text="Delay (seconds):").pack(side=tk.LEFT)
        self.entry_delay = tk.Entry(frame_delay, width=8)
        self.entry_delay.insert(0, "1.0")
        self.entry_delay.pack(side=tk.LEFT, padx=5)
        
        # Total Click
        frame_total = tk.Frame(frame_settings)
        frame_total.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_total, text="Total Clicks:").pack(side=tk.LEFT)
        self.entry_total = tk.Entry(frame_total, width=8)
        self.entry_total.insert(0, "5")
        self.entry_total.pack(side=tk.LEFT, padx=5)
        
        # Action Buttons Frame
        frame_actions = tk.Frame(self.root)
        frame_actions.pack(pady=15)
        
        self.btn_save_config = tk.Button(frame_actions, text="Save Config", command=self.save_config, font=("Arial", 10))
        self.btn_save_config.pack(side=tk.LEFT, padx=10)
        
        self.btn_start = tk.Button(frame_actions, text="Start & Save to PDF", command=self.start_process, bg="green", fg="white", font=("Arial", 11, "bold"))
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.root, text="Tip: Press 'ESC' key to cancel while program is running.", fg="gray", font=("Arial", 9, "italic")).pack()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    
                self.entry_area.delete(0, tk.END)
                self.entry_area.insert(0, config.get("printing_area", ""))
                
                self.entry_next.delete(0, tk.END)
                self.entry_next.insert(0, config.get("next_button", ""))
                
                self.entry_delay.delete(0, tk.END)
                self.entry_delay.insert(0, config.get("click_delay", "1.0"))
                
                self.entry_total.delete(0, tk.END)
                self.entry_total.insert(0, config.get("total_clicks", "5"))
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self, show_msg=True):
        config = {
            "printing_area": self.entry_area.get(),
            "next_button": self.entry_next.get(),
            "click_delay": self.entry_delay.get(),
            "total_clicks": self.entry_total.get()
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            if show_msg:
                messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            if show_msg:
                messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

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
            
            # Put into text box
            self.entry_area.delete(0, tk.END)
            self.entry_area.insert(0, f"{x1}, {y1}, {x2}, {y2}")
            
            overlay.destroy()
            self.root.deiconify() # Show main window again
            
        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

    def select_next_button(self):
        messagebox.showinfo("Select Next Button", "Move your mouse to the Next button and press the 's' key to save the coordinate.")
        
        def on_key_event(e):
            x, y = pyautogui.position()
            self.entry_next.delete(0, tk.END)
            self.entry_next.insert(0, f"{x}, {y}")
            # Clean up after a brief delay to ensure no trailing 's' remains
            self.root.after(50, self.clean_entry_next)
            keyboard.unhook_all()
        
        keyboard.on_press_key('s', on_key_event, suppress=True)

    def clean_entry_next(self):
        val = self.entry_next.get()
        cleaned = "".join([c for c in val if c.isdigit() or c in (',', ' ')]).strip()
        self.entry_next.delete(0, tk.END)
        self.entry_next.insert(0, cleaned)

    def sleep_with_cancel_check(self, seconds):
        # Checks every 100ms for 'ESC' key to cancel early
        steps = int(seconds * 10)
        for _ in range(steps):
            time.sleep(0.1)
            if keyboard.is_pressed('esc'):
                return False
        # Remainder time
        time.sleep(seconds - (steps * 0.1))
        if keyboard.is_pressed('esc'):
            return False
        return True

    def start_process(self):
        # 1. Parse Area coords
        area_str = self.entry_area.get().strip()
        try:
            rect_coords = [int(x.strip()) for x in area_str.split(",") if x.strip()]
            if len(rect_coords) != 4:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please select or input printing area coordinates manually in format: x1, y1, x2, y2")
            return

        # 2. Parse Next button coords
        next_str = self.entry_next.get().strip()
        try:
            next_coords = [int(x.strip()) for x in next_str.split(",") if x.strip()]
            if len(next_coords) != 2:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please select or input Next button coordinates manually in format: x, y")
            return
            
        # 3. Parse click settings
        try:
            delay = float(self.entry_delay.get())
            total_clicks = int(self.entry_total.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid delay or total clicks value.")
            return
            
        # 4. Save destination
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return
            
        # Auto-save configuration before starting process
        self.save_config(show_msg=False)

        self.root.withdraw()
        time.sleep(1) # Wait for window to hide
        
        try:
            self.screenshots = []
            
            for i in range(total_clicks):
                # Check cancellation
                if keyboard.is_pressed('esc'):
                    raise Exception("Process cancelled by user (ESC pressed).")

                # Take screenshot
                img = ImageGrab.grab(bbox=rect_coords)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                self.screenshots.append(img)
                
                if i < total_clicks - 1: # Don't click on the last iteration
                    # Click next
                    pyautogui.click(next_coords[0], next_coords[1])
                    # Wait with cancel check
                    if not self.sleep_with_cancel_check(delay):
                        raise Exception("Process cancelled by user (ESC pressed).")
                    
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
