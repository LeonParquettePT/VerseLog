import tkinter as tk

_FONT = ("Segoe UI", 14)
_MESSAGE = "Welcome to the VerseLog installer.\n\nClick Next to check your hardware."


class WelcomeStep:
    title = "Welcome"

    def build(self, parent: tk.Frame) -> tk.Frame:
        frame = tk.Frame(parent)
        tk.Label(frame, text=_MESSAGE, font=_FONT, justify="left").pack(pady=20)
        return frame
