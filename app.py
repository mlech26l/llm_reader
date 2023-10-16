import tkinter as tk
from tkinter import ttk, filedialog
import fitz

from tkinter import messagebox, scrolledtext

from llm_personalizer import Personalizer


def read_file(filename):
    if filename.endswith(".txt"):
        with open(filename, "r") as file:
            text = file.read()
        return text
    elif filename.endswith(".pdf"):
        doc = fitz.open(filename)
        text = ""
        for i, page in enumerate(doc):
            text += page.get_text("text")
        return text
    else:
        return ""


class TextApp:
    def __init__(self, root):
        self.personalizer = None
        self.root = root
        root.geometry("900x700")
        self.root.title("LLM Content Personalizer")

        # Configure grid weights to ensure that second row expands with window resizing
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Top frame with buttons for file operations
        self.top_frame = ttk.Frame(root)
        self.top_frame.grid(row=0, column=0, sticky="ew")
        self.open_button = ttk.Button(
            self.top_frame, text="Open File", command=self.open_file
        )
        self.open_button.pack(side="left", padx=5)

        label = ttk.Label(self.top_frame, text="Select model: ")
        label.pack(side="left", padx=5)
        self.combobox = ttk.Combobox(
            self.top_frame, values=["ChatGPT", "GPT-4", "Claude 2"], state="readonly"
        )
        # set a default value
        self.combobox.set("ChatGPT")
        self.combobox.pack(side="left", padx=5)
        self.combobox.bind("<<ComboboxSelected>>", self.select_model)

        # You can add more buttons to this frame if needed.

        font_tuple = ("Calibri", 16, "normal")
        self.text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=font_tuple)
        self.text_box.grid(row=1, column=0, sticky="nsew")
        self.text_box.config(state=tk.DISABLED)

        # Frame for widgets at the bottom
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.grid(row=3, column=0, sticky="ew")

        self.style_label = tk.Label(self.root, text="Current style: ")
        self.style_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # Some buttons
        self.button_prev = ttk.Button(
            self.bottom_frame, text="Previous", command=self.click_prev
        )
        self.button_prev.pack(side="left", padx=5)
        self.button_next = ttk.Button(
            self.bottom_frame, text="Re-generate", command=self.click_generate
        )
        self.button_next.pack(side="left", padx=5)
        self.button_gen = ttk.Button(
            self.bottom_frame, text="Next", command=self.click_next
        )
        self.button_gen.pack(side="left", padx=5)
        self.button_orig = ttk.Button(
            self.bottom_frame, text="Original", command=self.click_orig
        )
        self.button_orig.pack(side="left", padx=5)

        entry_frame = ttk.Frame(root)
        entry_frame.grid(row=4, column=0, sticky="ew")
        entry_frame.grid_columnconfigure(
            1, weight=1
        )  # Entry widget should expand with window resizing

        label = tk.Label(entry_frame, text="In the style of")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.entry_widget = tk.Entry(entry_frame, width=200)
        self.entry_widget.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.entry_widget.bind("<Return>", self.click_generate)

        self.active_widgets = [
            self.open_button,
            self.button_gen,
            self.button_next,
            self.button_prev,
            self.button_orig,
            self.entry_widget,
        ]

    def select_model(self, event):
        # Get the selected item from combobox
        selected_model = self.combobox.get()
        print(f"[GUI]: Selected model is {selected_model}")
        self.personalizer.set_model(selected_model)

    def disable_widgets(self):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, "Generating...")
        self.text_box.config(state=tk.DISABLED)
        for widget in self.active_widgets:
            widget.config(state=tk.DISABLED)

    def enable_widgets(self):
        for widget in self.active_widgets:
            widget.config(state=tk.NORMAL)

    def click_orig(self):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, self.personalizer.section)
        self.text_box.config(state=tk.DISABLED)

    def click_generate(self, event=None):
        print("[GUI]: Send text sent to personalizer.")
        self.disable_widgets()
        text = self.entry_widget.get()
        self.personalizer.set_style(text)
        self.style_label.config(text="Current style: " + text)
        self.personalizer.query_styled_selection(callback=self.set_main_text)

    def click_next(self):
        print("[GUI]: Send text sent to personalizer.")
        self.disable_widgets()
        self.personalizer.advance_section()
        self.personalizer.query_styled_selection(callback=self.set_main_text)

    def click_prev(self):
        print("[GUI]: Send text sent to personalizer.")
        self.disable_widgets()
        self.personalizer.retreat_section()
        self.personalizer.query_styled_selection(callback=self.set_main_text)

    def set_main_text(self, text):
        # print("Callback called -> set text to:", text)
        # print("Callback called -> set text to:", text[0 : min(20, len(text))])
        print("[GUI] Received text of length", len(text), "characters")
        # print(text)
        # print("===========================")
        self.enable_widgets()
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, text)
        self.text_box.config(state=tk.DISABLED)

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
            ),
        )
        if filepath:
            content = read_file(filepath)
            print("[GUI}: Read file with length", len(content))
            if content == "":
                messagebox.showerror("Error", "Could not read file!")
            else:
                print("[GUI]: Send text sent to personalizer.")
                self.disable_widgets()
                self.personalizer = Personalizer(content)
                self.personalizer.query_styled_selection(callback=self.set_main_text)

            # self.text_box.insert(tk.END, file.read())


if __name__ == "__main__":
    root = tk.Tk()
    app = TextApp(root)
    root.mainloop()