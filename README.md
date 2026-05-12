# 📚 BShot

> Automatically screenshot book pages directly from your browser.

BShot lets you select a custom screen area and captures pages one by one, saving them as numbered PNGs and automatically advancing with the arrow key — no manual work needed.

---

## ✨ Features

- 🎯 Custom area selection with a fullscreen snipping overlay
- 🔢 Set the starting page number — files are saved as `pagina_0042.png`, `pagina_0043.png`, etc.
- ⏱ Configurable delay between captures
- ⏳ Countdown before start so you can focus the browser
- 📁 Choose any output folder
- ⏹ Stop the capture at any time
- 🖥️ Clean dark UI built with customtkinter

---

## 🚀 Usage

1. Launch `BShot.exe`
2. Click **🎯 Seleziona Area** and drag to select the region to capture
3. Set the starting page number, total pages, delay and output folder
4. Click **▶ Avvia** — switch to your browser before the countdown ends
5. BShot will screenshot and advance pages automatically
6. Click **⏹ Stop** to interrupt at any time

---

## 🛠️ Build from source

**Requirements:** Python 3.11+

```bash
pip install customtkinter pyautogui pillow pyinstaller
pyinstaller --onefile --windowed --name BShot main.py
```

The executable will be at `dist/BShot.exe`.

---

## 📦 Tech Stack

| Library | Purpose |
|---|---|
| customtkinter | Dark UI |
| pyautogui | Keyboard automation |
| Pillow | Screen capture |
| PyInstaller | Build to .exe |

---

## 📄 License

MIT
