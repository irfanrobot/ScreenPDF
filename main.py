import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import keyboard
import time
from PIL import Image, ImageGrab, ImageChops, ImageStat
import os
import json

# Initialize Pillow plugins to prevent KeyError: 'JPEG'
Image.init()

class ScreenPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoPDF Screen Printer")
        self.root.geometry("450x500")
        
        self.screenshots = []
        self.config_file = "config.json"
        
        # Track printing areas separately for each mode
        self.printing_area_button = ""
        self.printing_area_scroll = ""
        
        self.setup_ui()
        
        # Track previous mode for area transition saving
        self.prev_mode = self.mode_var.get()
        self.load_config()

    def setup_ui(self):
        tk.Label(self.root, text="AutoPDF Screen Printer", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Mode Selection
        self.mode_var = tk.StringVar(value="button")
        frame_mode = tk.Frame(self.root)
        frame_mode.pack(pady=5)
        tk.Radiobutton(frame_mode, text="Button Mode", variable=self.mode_var, value="button", command=self.on_mode_change, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=15)
        tk.Radiobutton(frame_mode, text="Scroll Mode", variable=self.mode_var, value="scroll", command=self.on_mode_change, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=15)
        
        # Frame Area
        self.frame_area = tk.LabelFrame(self.root, text="1. Printing Area (x1, y1, x2, y2)", padx=10, pady=5)
        self.frame_area.pack(fill="x", padx=15, pady=5)
        
        self.btn_select_area = tk.Button(self.frame_area, text="Select on Screen", command=self.select_area)
        self.btn_select_area.pack(side=tk.LEFT, padx=5)
        
        self.btn_preview_area = tk.Button(self.frame_area, text="Preview", command=self.preview_area)
        self.btn_preview_area.pack(side=tk.RIGHT, padx=5)
        
        self.entry_area = tk.Entry(self.frame_area)
        self.entry_area.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Frame Next Button (Button Mode Specific)
        self.frame_next = tk.LabelFrame(self.root, text="2. Next Button Position (x, y)", padx=10, pady=5)
        self.frame_next.pack(fill="x", padx=15, pady=5)
        
        self.btn_select_next = tk.Button(self.frame_next, text="Select on Screen", command=self.select_next_button)
        self.btn_select_next.pack(side=tk.LEFT, padx=5)
        
        self.entry_next = tk.Entry(self.frame_next)
        self.entry_next.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # Frame Scroll Settings (Scroll Mode Specific, hidden by default)
        self.frame_scroll = tk.LabelFrame(self.root, text="2. Scroll Settings", padx=10, pady=5)
        
        self.scroll_method_var = tk.StringVar(value="key")
        frame_sm = tk.Frame(self.frame_scroll)
        frame_sm.pack(fill="x", pady=2)
        tk.Radiobutton(frame_sm, text="Key Press:", variable=self.scroll_method_var, value="key", command=self.on_scroll_method_change).pack(side=tk.LEFT)
        self.entry_scroll_key = tk.Entry(frame_sm, width=10)
        self.entry_scroll_key.insert(0, "pagedown")
        self.entry_scroll_key.pack(side=tk.LEFT, padx=5)
        tk.Label(frame_sm, text="(e.g., pagedown, space)", fg="gray", font=("Arial", 8)).pack(side=tk.LEFT)
        
        frame_ms = tk.Frame(self.frame_scroll)
        frame_ms.pack(fill="x", pady=2)
        tk.Radiobutton(frame_ms, text="Mouse Scroll:", variable=self.scroll_method_var, value="mouse", command=self.on_scroll_method_change).pack(side=tk.LEFT)
        self.entry_scroll_ticks = tk.Entry(frame_ms, width=8)
        self.entry_scroll_ticks.insert(0, "-100")
        self.entry_scroll_ticks.pack(side=tk.LEFT, padx=5)
        
        # Test Scroll Button
        self.btn_test_scroll = tk.Button(frame_ms, text="Test Scroll", command=self.test_scroll, font=("Arial", 8))
        self.btn_test_scroll.pack(side=tk.LEFT, padx=5)
        
        # Optional Next Button in Scroll Mode
        frame_scroll_next = tk.Frame(self.frame_scroll)
        frame_scroll_next.pack(fill="x", pady=5)
        tk.Label(frame_scroll_next, text="Next Button (optional, x, y):", font=("Arial", 9)).pack(side=tk.LEFT)
        self.btn_select_scroll_next = tk.Button(frame_scroll_next, text="Select", command=self.select_scroll_next_button, font=("Arial", 8))
        self.btn_select_scroll_next.pack(side=tk.LEFT, padx=5)
        self.entry_scroll_next = tk.Entry(frame_scroll_next)
        self.entry_scroll_next.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        
        # 3. Mode Specific Settings Frames
        # Button Settings Frame
        self.frame_btn_settings = tk.Frame(self.root)
        
        frame_delay_btn = tk.Frame(self.frame_btn_settings)
        frame_delay_btn.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_delay_btn, text="Delay (s):").pack(side=tk.LEFT)
        self.entry_delay_btn = tk.Entry(frame_delay_btn, width=8)
        self.entry_delay_btn.insert(0, "1.0")
        self.entry_delay_btn.pack(side=tk.LEFT, padx=5)
        
        frame_total_btn = tk.Frame(self.frame_btn_settings)
        frame_total_btn.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_total_btn, text="Total Clicks:").pack(side=tk.LEFT)
        self.entry_total_btn = tk.Entry(frame_total_btn, width=8)
        self.entry_total_btn.insert(0, "5")
        self.entry_total_btn.pack(side=tk.LEFT, padx=5)

        # Scroll Settings Frame
        self.frame_scroll_settings = tk.Frame(self.root)
        
        frame_delay_scroll = tk.Frame(self.frame_scroll_settings)
        frame_delay_scroll.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_delay_scroll, text="Delay (s):").pack(side=tk.LEFT)
        self.entry_delay_scroll = tk.Entry(frame_delay_scroll, width=6)
        self.entry_delay_scroll.insert(0, "1.0")
        self.entry_delay_scroll.pack(side=tk.LEFT, padx=3)
        
        frame_total_scroll = tk.Frame(self.frame_scroll_settings)
        frame_total_scroll.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_total_scroll, text="Scrolls/Page:").pack(side=tk.LEFT)
        self.entry_total_scroll = tk.Entry(frame_total_scroll, width=6)
        self.entry_total_scroll.insert(0, "3")
        self.entry_total_scroll.pack(side=tk.LEFT, padx=3)
        
        frame_page_scroll = tk.Frame(self.frame_scroll_settings)
        frame_page_scroll.pack(side=tk.LEFT, fill="x", expand=True)
        tk.Label(frame_page_scroll, text="Total Pages:").pack(side=tk.LEFT)
        self.entry_page_scroll = tk.Entry(frame_page_scroll, width=6)
        self.entry_page_scroll.insert(0, "5")
        self.entry_page_scroll.pack(side=tk.LEFT, padx=3)
        
        # Formatting Frame (Auto-Stitch + Format Selection)
        self.frame_format = tk.Frame(self.root)
        self.frame_format.pack(fill="x", padx=15, pady=5)
        
        # Auto Stitch Checkbox
        self.stitch_var = tk.BooleanVar(value=True)
        self.chk_stitch = tk.Checkbutton(self.frame_format, text="Auto-Stitch (Remove Overlap)", variable=self.stitch_var, font=("Arial", 9))
        self.chk_stitch.pack(side=tk.LEFT, padx=5)
        
        # Format radio selection
        self.export_format_var = tk.StringVar(value="pdf")
        tk.Label(self.frame_format, text="Format:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(self.frame_format, text="PDF", variable=self.export_format_var, value="pdf", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(self.frame_format, text="JPG", variable=self.export_format_var, value="jpg", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        # Action Buttons Frame
        self.frame_actions = tk.Frame(self.root)
        self.frame_actions.pack(pady=10)
        
        self.btn_save_config = tk.Button(self.frame_actions, text="Save Config", command=self.save_config, font=("Arial", 10))
        self.btn_save_config.pack(side=tk.LEFT, padx=10)
        
        self.btn_start = tk.Button(self.frame_actions, text="Start & Save", command=self.start_process, bg="green", fg="white", font=("Arial", 11, "bold"))
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        self.lbl_tip = tk.Label(self.root, text="Tip: Press 'ESC' key to cancel while program is running.", fg="gray", font=("Arial", 9, "italic"))
        self.lbl_tip.pack()
        
        # Initial pack states
        self.on_mode_change(init_call=True)
        self.on_scroll_method_change()

    def on_mode_change(self, init_call=False):
        # 1. Save current area entry value to previous mode's variable (if not initial call)
        if not init_call:
            if self.prev_mode == "button":
                self.printing_area_button = self.entry_area.get()
            else:
                self.printing_area_scroll = self.entry_area.get()
        
        # 2. Update tracking variable
        new_mode = self.mode_var.get()
        self.prev_mode = new_mode

        # 3. Load printing area of the newly selected mode into the entry box
        self.entry_area.delete(0, tk.END)
        if new_mode == "button":
            self.entry_area.insert(0, self.printing_area_button)
        else:
            self.entry_area.insert(0, self.printing_area_scroll)

        # 4. Refresh layout (Pack/Unpack frames sequentially to keep correct vertical order)
        self.frame_area.pack_forget()
        self.frame_next.pack_forget()
        self.frame_scroll.pack_forget()
        self.frame_btn_settings.pack_forget()
        self.frame_scroll_settings.pack_forget()
        self.frame_format.pack_forget()
        self.frame_actions.pack_forget()
        self.lbl_tip.pack_forget()
        
        self.frame_area.pack(fill="x", padx=15, pady=5)
        if new_mode == "button":
            self.frame_next.pack(fill="x", padx=15, pady=5)
            self.frame_btn_settings.pack(fill="x", padx=15, pady=5)
            self.chk_stitch.config(state="disabled") # Auto-Stitch is only relevant for Scroll Mode
        else:
            self.frame_scroll.pack(fill="x", padx=15, pady=5)
            self.frame_scroll_settings.pack(fill="x", padx=15, pady=5)
            self.chk_stitch.config(state="normal")
            
        self.frame_format.pack(fill="x", padx=15, pady=5)
        self.frame_actions.pack(pady=10)
        self.lbl_tip.pack()

    def on_scroll_method_change(self):
        method = self.scroll_method_var.get()
        if method == "key":
            self.entry_scroll_key.config(state="normal")
            self.entry_scroll_ticks.config(state="disabled")
            self.btn_test_scroll.config(state="disabled")
        else:
            self.entry_scroll_key.config(state="disabled")
            self.entry_scroll_ticks.config(state="normal")
            self.btn_test_scroll.config(state="normal")

    def test_scroll(self):
        try:
            ticks = int(self.entry_scroll_ticks.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please input a valid integer for scroll ticks.")
            return
            
        # Temporarily hide window to allow user to point mouse to target document
        self.root.withdraw()
        time.sleep(1.5) # Give user 1.5 seconds to reposition cursor
        
        x, y = pyautogui.position()
        pyautogui.scroll(ticks, x=x, y=y)
        
        self.root.deiconify()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                
                # Load mode first
                active_mode = config.get("mode", "button")
                self.mode_var.set(active_mode)
                self.prev_mode = active_mode
                
                # Load printing areas
                self.printing_area_button = config.get("printing_area_button", "")
                self.printing_area_scroll = config.get("printing_area_scroll", "")
                
                # Migrate old format if needed
                if not self.printing_area_button and not self.printing_area_scroll:
                    old_area = config.get("printing_area", "")
                    if active_mode == "button":
                        self.printing_area_button = old_area
                    else:
                        self.printing_area_scroll = old_area
                
                self.on_mode_change(init_call=True)
                
                self.entry_next.delete(0, tk.END)
                self.entry_next.insert(0, config.get("next_button", ""))
                
                self.scroll_method_var.set(config.get("scroll_method", "key"))
                self.on_scroll_method_change()
                
                self.entry_scroll_key.delete(0, tk.END)
                self.entry_scroll_key.insert(0, config.get("scroll_key", "pagedown"))
                
                self.entry_scroll_ticks.delete(0, tk.END)
                self.entry_scroll_ticks.insert(0, config.get("scroll_ticks", "-100"))
                
                self.entry_scroll_next.delete(0, tk.END)
                self.entry_scroll_next.insert(0, config.get("scroll_next_button", ""))
                
                # Load separated delay, clicks, scrolls, pages
                self.entry_delay_btn.delete(0, tk.END)
                self.entry_delay_btn.insert(0, config.get("button_delay", "1.0"))
                
                self.entry_total_btn.delete(0, tk.END)
                self.entry_total_btn.insert(0, config.get("button_total_clicks", "5"))
                
                self.entry_delay_scroll.delete(0, tk.END)
                self.entry_delay_scroll.insert(0, config.get("scroll_delay", "1.0"))
                
                self.entry_total_scroll.delete(0, tk.END)
                self.entry_total_scroll.insert(0, config.get("scroll_scrolls_per_page", "3"))
                
                self.entry_page_scroll.delete(0, tk.END)
                self.entry_page_scroll.insert(0, config.get("scroll_total_pages", "5"))
                
                self.stitch_var.set(config.get("auto_stitch", True))
                self.export_format_var.set(config.get("export_format", "pdf"))
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self, show_msg=True):
        if self.mode_var.get() == "button":
            self.printing_area_button = self.entry_area.get()
        else:
            self.printing_area_scroll = self.entry_area.get()

        config = {
            "mode": self.mode_var.get(),
            "printing_area_button": self.printing_area_button,
            "printing_area_scroll": self.printing_area_scroll,
            "next_button": self.entry_next.get(),
            "scroll_method": self.scroll_method_var.get(),
            "scroll_key": self.entry_scroll_key.get(),
            "scroll_ticks": self.entry_scroll_ticks.get(),
            "scroll_next_button": self.entry_scroll_next.get(),
            
            # Save separated settings
            "button_delay": self.entry_delay_btn.get(),
            "button_total_clicks": self.entry_total_btn.get(),
            
            "scroll_delay": self.entry_delay_scroll.get(),
            "scroll_scrolls_per_page": self.entry_total_scroll.get(),
            "scroll_total_pages": self.entry_page_scroll.get(),
            
            "auto_stitch": self.stitch_var.get(),
            "export_format": self.export_format_var.get()
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            if show_msg:
                messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            if show_msg:
                messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def preview_area(self):
        area_str = self.entry_area.get().strip()
        try:
            rect_coords = [int(x.strip()) for x in area_str.split(",") if x.strip()]
            if len(rect_coords) != 4:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Koordinat Printing Area tidak valid. Pastikan formatnya: x1, y1, x2, y2")
            return
            
        x1, y1, x2, y2 = rect_coords
        
        self.root.withdraw() # Hide main window
        time.sleep(0.2) # Small delay to ensure main window is hidden
        
        overlay = tk.Toplevel()
        overlay.attributes('-alpha', 0.4) # Semi-transparent
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True) # Keep on top
        
        canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw red border around the printing area
        canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=4, fill='')
        
        # Calculate text position (center of printing area, or center of screen if area is too small)
        screen_w = overlay.winfo_screenwidth()
        screen_h = overlay.winfo_screenheight()
        
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        
        # If center of area is out of bounds or area is too small, use center of screen
        if not (0 < cx < screen_w and 0 < cy < screen_h) or abs(x2 - x1) < 100 or abs(y2 - y1) < 100:
            cx = screen_w // 2
            cy = screen_h // 2
            
        canvas.create_text(cx, cy, text="PRINTING AREA PREVIEW\n\n(Klik di mana saja atau tekan tombol apa saja untuk menutup)", 
                           fill="white", font=("Arial", 14, "bold"), justify=tk.CENTER)
                           
        def close_preview(event=None):
            overlay.destroy()
            self.root.deiconify() # Show main window again
            
        overlay.bind("<Button-1>", close_preview)
        overlay.bind("<Key>", close_preview)
        overlay.focus_set()

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

    def select_scroll_next_button(self):
        messagebox.showinfo("Select Next Button", "Move your mouse to the Next button and press the 's' key to save the coordinate.")
        
        def on_key_event(e):
            x, y = pyautogui.position()
            self.entry_scroll_next.delete(0, tk.END)
            self.entry_scroll_next.insert(0, f"{x}, {y}")
            # Clean up after a brief delay
            self.root.after(50, self.clean_entry_scroll_next)
            keyboard.unhook_all()
            
        keyboard.on_press_key('s', on_key_event, suppress=True)

    def clean_entry_next(self):
        val = self.entry_next.get()
        cleaned = "".join([c for c in val if c.isdigit() or c in (',', ' ')]).strip()
        self.entry_next.delete(0, tk.END)
        self.entry_next.insert(0, cleaned)

    def clean_entry_scroll_next(self):
        val = self.entry_scroll_next.get()
        cleaned = "".join([c for c in val if c.isdigit() or c in (',', ' ')]).strip()
        self.entry_scroll_next.delete(0, tk.END)
        self.entry_scroll_next.insert(0, cleaned)

    def get_page_filename(self, save_path, index, total_count):
        if total_count <= 1:
            return save_path
        dir_name = os.path.dirname(save_path)
        base_name = os.path.basename(save_path)
        name_part, ext_part = os.path.splitext(base_name)
        return os.path.join(dir_name, f"{name_part}_{index+1}{ext_part}")

    def sleep_with_cancel_check(self, seconds):
        # Checks every 50ms for cancel flag or 'ESC' key to cancel early
        steps = int(seconds * 20)
        for _ in range(steps):
            time.sleep(0.05)
            if getattr(self, 'cancel_requested', False) or keyboard.is_pressed('esc'):
                return False
        # Remainder time
        time.sleep(max(0.0, seconds - (steps * 0.05)))
        if getattr(self, 'cancel_requested', False) or keyboard.is_pressed('esc'):
            return False
        return True

    def find_overlap(self, img1, img2, max_overlap_pct=0.9, min_overlap_pixels=15):
        w, h = img1.size
        min_s = int(h * (1 - max_overlap_pct))
        max_s = h - min_overlap_pixels
        
        g1 = img1.convert("L")
        g2 = img2.convert("L")
        
        best_s = None
        min_mean_diff = 255.0
        
        for s in range(min_s, max_s):
            overlap_h = h - s
            crop1 = g1.crop((0, s, w, h))
            crop2 = g2.crop((0, 0, w, overlap_h))
            
            diff = ImageChops.difference(crop1, crop2)
            stat = ImageStat.Stat(diff)
            mean_diff = stat.mean[0]
            
            if mean_diff < min_mean_diff:
                min_mean_diff = mean_diff
                best_s = s
                
        if min_mean_diff < 4.0: # threshold of average pixel diff < 4/255
            return best_s
        return None

    def stitch_screenshots_into_single_image(self, screenshots, auto_stitch):
        if not screenshots:
            return None
        if len(screenshots) == 1:
            return screenshots[0]
            
        w = screenshots[0].width
        h = screenshots[0].height
        
        combined_image = screenshots[0]
        
        for i in range(1, len(screenshots)):
            prev_img = screenshots[i-1]
            next_img = screenshots[i]
            
            s = self.find_overlap(prev_img, next_img) if auto_stitch else None
            if s is not None:
                # Crop the bottom part of next_img that is new
                overlap_h = h - s
                cropped = next_img.crop((0, overlap_h, w, next_img.height))
                
                new_combined = Image.new("RGB", (w, combined_image.height + cropped.height))
                new_combined.paste(combined_image, (0, 0))
                new_combined.paste(cropped, (0, combined_image.height))
                combined_image = new_combined
            else:
                # No overlap found, stack fully
                new_combined = Image.new("RGB", (w, combined_image.height + next_img.height))
                new_combined.paste(combined_image, (0, 0))
                new_combined.paste(next_img, (0, combined_image.height))
                combined_image = new_combined
                
        return combined_image

    def start_process(self):
        # Get active mode and format
        mode = self.mode_var.get()
        export_format = self.export_format_var.get()

        # 1. Parse Area coords
        area_str = self.entry_area.get().strip()
        try:
            rect_coords = [int(x.strip()) for x in area_str.split(",") if x.strip()]
            if len(rect_coords) != 4:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please select or input printing area coordinates manually in format: x1, y1, x2, y2")
            return

        # 2. Mode dependent coordinates parsing
        next_coords = None
        scroll_key = None
        scroll_ticks = None
        scroll_method = None
        scroll_next_coords = None
        
        if mode == "button":
            next_str = self.entry_next.get().strip()
            try:
                next_coords = [int(x.strip()) for x in next_str.split(",") if x.strip()]
                if len(next_coords) != 2:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please select or input Next button coordinates manually in format: x, y")
                return
        else: # scroll mode
            scroll_method = self.scroll_method_var.get()
            if scroll_method == "key":
                scroll_key = self.entry_scroll_key.get().strip()
                if not scroll_key:
                    messagebox.showerror("Error", "Please input a valid scroll keyboard key (e.g., pagedown).")
                    return
            else:
                try:
                    scroll_ticks = int(self.entry_scroll_ticks.get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Please input a valid integer for mouse scroll ticks.")
                    return
            
            # Optional next button coordinate
            scroll_next_str = self.entry_scroll_next.get().strip()
            if scroll_next_str:
                try:
                    scroll_next_coords = [int(x.strip()) for x in scroll_next_str.split(",") if x.strip()]
                    if len(scroll_next_coords) != 2:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Error", "Optional Next Button coordinate format invalid. Must be: x, y")
                    return
            
        # 3. Parse Settings for active mode
        try:
            if mode == "button":
                delay = float(self.entry_delay_btn.get())
                total_clicks = int(self.entry_total_btn.get())
                # Button Mode does not have scrolls/page or total_pages settings
                scrolls_per_page = 0
                total_pages = total_clicks 
            else: # scroll mode
                delay = float(self.entry_delay_scroll.get())
                scrolls_per_page = int(self.entry_total_scroll.get())
                total_pages = int(self.entry_page_scroll.get())
                
            if delay < 0 or total_pages < 1 or (mode == "scroll" and scrolls_per_page < 0):
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid inputs. Delay, clicks, scrolls, and pages must be valid positive numbers.")
            return
            
        # 4. Save destination
        if export_format == "pdf":
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        else:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG images", "*.jpg;*.jpeg")])
            
        if not save_path:
            return
            
        # Auto-save configuration before starting process
        self.save_config(show_msg=False)

        # Check for existing JPG pages to support resuming
        start_page_idx = 0
        limit = total_clicks if mode == "button" else total_pages
        if export_format == "jpg":
            existing_count = 0
            for i in range(limit):
                page_path = self.get_page_filename(save_path, i, limit)
                if os.path.exists(page_path):
                    existing_count += 1
                else:
                    break
            
            if existing_count > 0:
                if existing_count >= limit:
                    answer = messagebox.askyesno(
                        "Semua File Sudah Ada",
                        f"Semua {limit} halaman JPG sudah ada di direktori tujuan.\n\n"
                        f"Apakah Anda ingin mengulangi proses ekspor dari halaman awal (menimpa file lama)?"
                    )
                    if answer:
                        start_page_idx = 0
                    else:
                        return
                else:
                    answer = messagebox.askyesnocancel(
                        "Lanjutkan Ekspor JPG?",
                        f"Ditemukan {existing_count} halaman JPG yang sudah tersimpan di direktori tujuan.\n\n"
                        f"Apakah Anda ingin melanjutkan ekspor dari halaman {existing_count + 1}?\n"
                        f"- Klik [YA] untuk melanjutkan ke halaman {existing_count + 1}.\n"
                        f"- Klik [TIDAK] untuk mulai ulang dari halaman 1 (timpa file lama).\n"
                        f"- Klik [BATAL] untuk membatalkan proses ekspor.\n\n"
                        f"PENTING: Jika Anda memilih YA, pastikan dokumen/layar target sudah diposisikan pada halaman {existing_count + 1}."
                    )
                    if answer is None:  # Cancel
                        return
                    elif answer is True:  # Yes, resume
                        start_page_idx = existing_count
                    else:  # No, overwrite
                        start_page_idx = 0

        self.root.withdraw()
        time.sleep(1) # Wait for window to hide
        
        hotkey_id = None
        self.cancel_requested = False
        try:
            # Register a low-level global hotkey for ESC key to guarantee capturing the press event
            try:
                hotkey_id = keyboard.add_hotkey('esc', lambda: setattr(self, 'cancel_requested', True))
            except Exception as e:
                print(f"Warning: Could not register ESC hotkey: {e}")

            pdf_pages = []
            
            if mode == "button":
                # Button Mode logic: simple capture loop
                self.screenshots = []
                for i in range(start_page_idx, total_clicks):
                    if self.cancel_requested or keyboard.is_pressed('esc'):
                        raise Exception("Process cancelled by user (ESC pressed).")
                        
                    img = ImageGrab.grab(bbox=rect_coords)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    
                    if export_format == "jpg":
                        page_path = self.get_page_filename(save_path, i, total_clicks)
                        img.save(page_path)
                    else:
                        self.screenshots.append(img)
                    
                    if i < total_clicks - 1:
                        pyautogui.click(next_coords[0], next_coords[1])
                        if not self.sleep_with_cancel_check(delay):
                            raise Exception("Process cancelled by user (ESC pressed).")
                            
                if export_format == "pdf":
                    pdf_pages = self.screenshots
                    
            else:
                # Scroll Mode logic:
                # Total Pages (total_pages input)
                # Scrolls per page (scrolls_per_page input)
                # Auto-stitch resets per page
                
                center_x = (rect_coords[0] + rect_coords[2]) // 2
                center_y = (rect_coords[1] + rect_coords[3]) // 2
                
                for p in range(start_page_idx, total_pages):
                    # Check cancellation
                    if self.cancel_requested or keyboard.is_pressed('esc'):
                        raise Exception("Process cancelled by user (ESC pressed).")

                    # Focus the target window at the start of every page
                    pyautogui.click(center_x, center_y)
                    time.sleep(0.5) # Wait for focus to register

                    page_screenshots = []
                    
                    # 1. Take initial screenshot for the page
                    img = ImageGrab.grab(bbox=rect_coords)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    page_screenshots.append(img)
                    
                    # 2. Perform scrolls and take screenshots
                    for s in range(scrolls_per_page):
                        if self.cancel_requested or keyboard.is_pressed('esc'):
                            raise Exception("Process cancelled by user (ESC pressed).")
                            
                        # Scroll
                        if scroll_method == "key":
                            pyautogui.press(scroll_key)
                        else:
                            pyautogui.scroll(scroll_ticks, x=center_x, y=center_y)
                            
                        # Wait
                        if not self.sleep_with_cancel_check(delay):
                            raise Exception("Process cancelled by user (ESC pressed).")
                            
                        # Take screenshot
                        img = ImageGrab.grab(bbox=rect_coords)
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')
                        page_screenshots.append(img)
                    
                    # 3. Stitch page_screenshots into 1 full page image
                    stitched_page = self.stitch_screenshots_into_single_image(page_screenshots, self.stitch_var.get())
                    
                    if export_format == "jpg":
                        page_path = self.get_page_filename(save_path, p, total_pages)
                        stitched_page.save(page_path)
                    else:
                        pdf_pages.append(stitched_page)
                    
                    # 4. If there's an optional Next button and we have more pages, click it
                    if p < total_pages - 1 and scroll_next_coords:
                        pyautogui.click(scroll_next_coords[0], scroll_next_coords[1])
                        # Wait for page transition loading
                        if not self.sleep_with_cancel_check(delay + 1.0): # Extra 1.0s to allow next page to load fully
                            raise Exception("Process cancelled by user (ESC pressed).")

            # Save / Export logic
            if export_format == "pdf":
                if pdf_pages:
                    pdf_pages[0].save(save_path, save_all=True, append_images=pdf_pages[1:])
                    messagebox.showinfo("Success", f"PDF saved successfully to:\n{save_path}")
            else:
                # JPG files are already saved directly to disk during the loop.
                messagebox.showinfo("Success", f"JPG images saved successfully to:\n{os.path.dirname(save_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")
        finally:
            if hotkey_id is not None:
                try:
                    keyboard.remove_hotkey(hotkey_id)
                except Exception:
                    pass
            self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenPrinterApp(root)
    root.mainloop()
