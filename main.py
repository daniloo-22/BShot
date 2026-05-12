import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import time
import os
from PIL import ImageGrab, Image, ImageTk
import pyautogui

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AreaSelector(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.start_x = self.start_y = 0
        self.rect = None

        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.3)
        self.configure(background="black")
        self.attributes("-topmost", True)
        self.config(cursor="crosshair")

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_press(self, event):
        self.start_x, self.start_y = event.x_root, event.y_root
        if self.rect:
            self.canvas.delete(self.rect)

    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        x0 = self.start_x - self.winfo_rootx()
        y0 = self.start_y - self.winfo_rooty()
        x1 = event.x
        y1 = event.y
        self.rect = self.canvas.create_rectangle(
            x0, y0, x1, y1,
            outline="red", width=2, fill=""
        )

    def on_release(self, event):
        x1 = min(self.start_x, event.x_root)
        y1 = min(self.start_y, event.y_root)
        x2 = max(self.start_x, event.x_root)
        y2 = max(self.start_y, event.y_root)
        self.destroy()
        if x2 - x1 > 5 and y2 - y1 > 5:
            self.callback(x1, y1, x2, y2)


class BShot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BShot")
        self.geometry("520x620")
        self.resizable(False, False)

        self.area = None
        self._stop_flag = False
        self._running = False

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 6))
        ctk.CTkLabel(header, text="BShot", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="screenshot loop", font=ctk.CTkFont(size=13), text_color="gray").pack(side="left", padx=10, pady=4)

        # Settings card
        card = ctk.CTkFrame(self)
        card.pack(fill="x", padx=20, pady=8)

        def row(parent, label, widget_factory, row_idx):
            ctk.CTkLabel(parent, text=label, anchor="w", width=160).grid(row=row_idx, column=0, sticky="w", padx=14, pady=6)
            w = widget_factory(parent)
            w.grid(row=row_idx, column=1, sticky="ew", padx=14, pady=6)
            parent.columnconfigure(1, weight=1)
            return w

        self.start_page_var = ctk.StringVar(value="1")
        self.total_pages_var = ctk.StringVar(value="10")
        self.delay_var = ctk.StringVar(value="2.0")
        self.countdown_var = ctk.StringVar(value="3")

        row(card, "Pagina iniziale", lambda p: ctk.CTkEntry(p, textvariable=self.start_page_var, width=120), 0)
        row(card, "Totale pagine", lambda p: ctk.CTkEntry(p, textvariable=self.total_pages_var, width=120), 1)
        row(card, "Delay (secondi)", lambda p: ctk.CTkEntry(p, textvariable=self.delay_var, width=120), 2)
        row(card, "Countdown (sec)", lambda p: ctk.CTkEntry(p, textvariable=self.countdown_var, width=120), 3)

        # Output folder
        folder_row = ctk.CTkFrame(card, fg_color="transparent")
        folder_row.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=6)
        ctk.CTkLabel(folder_row, text="Cartella output", anchor="w", width=160).pack(side="left")
        self.folder_var = ctk.StringVar(value=os.path.expanduser("~\\Desktop"))
        folder_entry = ctk.CTkEntry(folder_row, textvariable=self.folder_var)
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(folder_row, text="📁", width=36, command=self._pick_folder).pack(side="left")

        # Area label
        self.area_label = ctk.CTkLabel(card, text="Area: non selezionata", text_color="gray", anchor="w")
        self.area_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=14, pady=(4, 10))

        # Area selector button
        ctk.CTkButton(
            self, text="🎯  Seleziona Area",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44, corner_radius=10,
            command=self._select_area
        ).pack(fill="x", padx=20, pady=(6, 4))

        # Preview
        self.preview_label = ctk.CTkLabel(self, text="", fg_color="#1a1a2e", corner_radius=8)
        self.preview_label.pack(fill="x", padx=20, pady=4)
        self._preview_img_ref = None

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, height=10)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=(8, 2))

        self.status_label = ctk.CTkLabel(self, text="Pronto", text_color="gray", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=2)

        # Start / Stop buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(8, 16))
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(
            btn_row, text="▶  Avvia",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42, fg_color="#2d8c4e", hover_color="#1e6b38",
            command=self._start
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.stop_btn = ctk.CTkButton(
            btn_row, text="⏹  Stop",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42, fg_color="#8c2d2d", hover_color="#6b1e1e",
            command=self._stop, state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _pick_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_var.get())
        if path:
            self.folder_var.set(path)

    def _select_area(self):
        self.withdraw()
        self.after(150, self._open_overlay)

    def _open_overlay(self):
        AreaSelector(self, self._on_area_selected)

    def _on_area_selected(self, x1, y1, x2, y2):
        self.area = (x1, y1, x2, y2)
        self.area_label.configure(
            text=f"Area: {x1}×{y1}  →  {x2}×{y2}  ({x2-x1}×{y2-y1} px)",
            text_color="white"
        )
        self.deiconify()
        self._update_preview()

    def _update_preview(self):
        if not self.area:
            return
        try:
            img = ImageGrab.grab(bbox=self.area)
            img.thumbnail((480, 120))
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo, text="")
            self._preview_img_ref = photo
        except Exception:
            pass

    def _set_status(self, text, color="gray"):
        self.status_label.configure(text=text, text_color=color)

    # ── capture loop ─────────────────────────────────────────────────────────

    def _start(self):
        if self._running:
            return
        if not self.area:
            self._set_status("Seleziona prima un'area!", "red")
            return
        try:
            start_page = int(self.start_page_var.get())
            total = int(self.total_pages_var.get())
            delay = float(self.delay_var.get())
            countdown = int(self.countdown_var.get())
            folder = self.folder_var.get()
        except ValueError:
            self._set_status("Controlla i valori nelle impostazioni", "red")
            return

        if not os.path.isdir(folder):
            self._set_status("Cartella output non valida", "red")
            return

        self._stop_flag = False
        self._running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_bar.set(0)

        t = threading.Thread(
            target=self._run_loop,
            args=(start_page, total, delay, countdown, folder),
            daemon=True
        )
        t.start()

    def _stop(self):
        self._stop_flag = True

    def _run_loop(self, start_page, total, delay, countdown, folder):
        # Countdown
        for i in range(countdown, 0, -1):
            if self._stop_flag:
                self._finish("Interrotto", "red")
                return
            self._set_status(f"Avvio tra {i}…", "#e07b00")
            time.sleep(1)

        for i in range(total):
            if self._stop_flag:
                self._finish("Interrotto", "red")
                return

            page_num = start_page + i
            filename = f"pagina_{page_num:04d}.png"
            filepath = os.path.join(folder, filename)

            try:
                img = ImageGrab.grab(bbox=self.area)
                img.save(filepath)
            except Exception as e:
                self._set_status(f"Errore: {e}", "red")
                self._finish("Errore durante la cattura", "red")
                return

            progress = (i + 1) / total
            self.after(0, self.progress_bar.set, progress)
            self._set_status(f"✔ {filename}  ({i+1}/{total})", "#2ecc71")

            if i < total - 1:
                pyautogui.press("right")
                time.sleep(delay)

        self._finish(f"Completato! {total} pagine salvate.", "#2ecc71")

    def _finish(self, msg, color):
        self._running = False
        self._stop_flag = False
        self.after(0, lambda: self._set_status(msg, color))
        self.after(0, lambda: self.start_btn.configure(state="normal"))
        self.after(0, lambda: self.stop_btn.configure(state="disabled"))


if __name__ == "__main__":
    app = BShot()
    app.mainloop()
