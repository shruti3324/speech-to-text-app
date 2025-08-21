import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import speech_recognition as sr
import threading
import os

APP_TITLE = "Speech to Text App"
LOGO_PATH = "microphone_icon.png"

def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    label = tk.Label(tooltip, text=text, background="#222", foreground="#fff", relief='solid', borderwidth=1, font=("Segoe UI", 9))
    label.pack()
    def enter(event):
        x, y, _, _ = widget.bbox("insert") if hasattr(widget, 'bbox') else (0, 0, 0, 0)
        x += widget.winfo_rootx() + 20
        y += widget.winfo_rooty() + 25
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()
    def leave(event):
        tooltip.withdraw()
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def transcribe_audio_file():
    file_path = filedialog.askopenfilename(title="Select Audio File", 
                                           filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
    if not file_path:
        return
    recognizer = sr.Recognizer()
    try:
        if file_path.endswith('.mp3'):
            try:
                from pydub import AudioSegment
            except ImportError:
                messagebox.showerror("Dependency Missing", "Please install pydub for MP3 support: pip install pydub")
                return
            sound = AudioSegment.from_mp3(file_path)
            wav_path = file_path + ".wav"
            sound.export(wav_path, format="wav")
            file_path = wav_path
        with sr.AudioFile(file_path) as source:
            set_status("Transcribing file...")
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            text_area.insert(tk.END, f"Transcribed Text:\n{text}\n\n")
            set_status("Idle")
    except Exception as e:
        set_status("Idle")
        messagebox.showerror("Error", str(e))

def live_subtitles():
    def recognize_loop():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            set_status("Listening...")
            while subtitle_running[0]:
                try:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio)
                    text_area.insert(tk.END, f"{text} ")
                    text_area.see(tk.END)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    text_area.insert(tk.END, f"\nAPI error: {e}\n")
                    break
        set_status("Idle")
    subtitle_running[0] = True
    threading.Thread(target=recognize_loop, daemon=True).start()

def stop_subtitles():
    subtitle_running[0] = False
    set_status("Idle")
    text_area.insert(tk.END, "\nStopped live subtitles.\n")

def clear_text():
    text_area.delete('1.0', tk.END)

def set_status(text):
    status_var.set(text)
    status_label.update_idletasks()

root = tk.Tk()
root.title(APP_TITLE)
root.geometry("950x750")
root.resizable(False, False)

def make_vertical_gradient(width, height, top_color, bottom_color):
    base = Image.new('RGB', (width, height), top_color)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return ImageTk.PhotoImage(base)

bg_gradient = make_vertical_gradient(950, 750, (205,218,253), (39,64,139))
bg_label = tk.Label(root, image=bg_gradient)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

style = ttk.Style(root)
style.theme_use('clam')
style.configure("TButton",
    font=("Segoe UI", 12, "bold"),
    padding=10,
    relief="flat",
    borderwidth=0,
    background="#FFD600",
    foreground="#1a237e"
)
style.map("TButton",
    background=[('active', '#FF8F00')],
    foreground=[('active', 'white')]
)
style.configure("Exit.TButton", background="#FFD600", foreground="#1a237e")
style.map("Exit.TButton", background=[('active', '#FF8F00')])

top_frame = tk.Frame(root, bg="#cddafd")
top_frame.pack(pady=(18, 0))

circle = tk.Canvas(top_frame, width=90, height=90, bg="#cddafd", highlightthickness=0)
circle.create_oval(8, 8, 82, 82, fill="#eaf6fb", outline="#4367c7", width=5)
circle.pack()
try:
    logo_img = Image.open(LOGO_PATH).resize((60, 60), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(logo_img)
    circle.create_image(45, 45, image=logo)
except Exception:
    circle.create_text(45, 45, text="🎤", font=("Arial", 34))

app_label = tk.Label(top_frame, text="Speech to Text Converter", font=("Segoe UI", 28, "bold"),
                     bg="#cddafd", fg="#112d4e")
app_label.pack(pady=(7, 0))

# MAIN TEXT AREA (shorter so buttons are visible at bottom)
shadow = tk.Frame(root, bg="#4367c7")
shadow.pack(pady=(10, 0), padx=24, fill="both", expand=False)
main_frame = tk.Frame(shadow, bg="#eaf6fb", bd=0, highlightbackground="#27408b", highlightthickness=3)
main_frame.pack(padx=4, pady=4)

text_area = scrolledtext.ScrolledText(
    main_frame, width=104, height=16, wrap=tk.WORD,   # reduce height from 21 to 16
    font=("Segoe UI", 13), bg="#eaf6fb", fg="#112d4e", borderwidth=0, relief=tk.FLAT
)
text_area.pack(padx=18, pady=14)

# ---- Button section, at the bottom ----
button_frame = tk.Frame(root, bg="#eaf6fb")
button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0,0), padx=24, before=None)

live_btn = ttk.Button(button_frame, text="Start Live Subtitles", command=live_subtitles)
live_btn.grid(row=0, column=0, sticky="ew", padx=6, pady=3)
create_tooltip(live_btn, "Transcribe your speech live as subtitles.")

stop_btn = ttk.Button(button_frame, text="Stop Subtitles", command=stop_subtitles)
stop_btn.grid(row=0, column=1, sticky="ew", padx=6, pady=3)
create_tooltip(stop_btn, "Stop listening and subtitle transcription.")

file_btn = ttk.Button(button_frame, text="Transcribe Audio File", command=transcribe_audio_file)
file_btn.grid(row=0, column=2, sticky="ew", padx=6, pady=3)
create_tooltip(file_btn, "Convert a saved audio file (wav, mp3, flac) to text.")

clear_btn = ttk.Button(button_frame, text="Clear", command=clear_text)
clear_btn.grid(row=0, column=3, sticky="ew", padx=6, pady=3)
create_tooltip(clear_btn, "Clear all text.")

exit_btn = ttk.Button(button_frame, text="❌ Exit", command=root.quit, style="Exit.TButton")
exit_btn.grid(row=0, column=4, sticky="ew", padx=6, pady=3)
create_tooltip(exit_btn, "Exit the app.")

for i in range(5):
    button_frame.grid_columnconfigure(i, weight=1)

status_var = tk.StringVar(value="Idle")
status_label = tk.Label(
    root, textvariable=status_var, bd=0, relief=tk.FLAT, anchor=tk.W,
    bg="#27408b", fg="white", font=("Segoe UI", 13, "bold"), height=2
)
status_label.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

subtitle_running = [False]

root.mainloop()