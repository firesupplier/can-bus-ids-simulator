"""Grafični uporabniški vmesnik za konfiguracijo in zagon simulatorja."""

import tkinter as tk
from tkinter import messagebox
from collections.abc import Callable


class SimulatorGUI:
    """Omogoča nastavitev simulacije, učenje IDS in zagon zaznavanja."""

    def __init__(
        self,
        detect_callback: Callable[[float, list[str], str], None],
        learn_callback: Callable[[int, float, float], bool],

    ) -> None:
        self.detect_callback = detect_callback
        self.learn_callback = learn_callback

        self.root = tk.Tk()
        self.root.title("Simulator CAN Bus IDS")
        self.root.geometry("360x630")
        self.root.resizable(False, False)

        title_label = tk.Label(
            self.root,
            text="Simulator CAN Bus IDS",
            font=("Arial", 14),
        )
        title_label.pack(pady=(20, 15))

        """UCENJE"""

        ids_learning_frame = tk.LabelFrame(
            self.root,
            text="Pred zaznavanjem nauči IDS:",
            padx=10,
            pady=10,
        )
        ids_learning_frame.pack(padx=20, pady=10, fill="x")


        self.learn_button = tk.Button(
            ids_learning_frame,
            text="Začni učenje",
            width=15,
            command=self.start_learning,
            state=tk.NORMAL,
        )
        self.learn_button.pack(pady=5)

        """ NAPADI """

        self.attack_vars = {
            "injection": tk.BooleanVar(value=False),
            "replay": tk.BooleanVar(value=False),
            "payload": tk.BooleanVar(value=False),
            "timing": tk.BooleanVar(value=False),
            "flooding": tk.BooleanVar(value=False),
        }

        attacks_frame = tk.LabelFrame(
            self.root,
            text="Izberi napade na omrežje: ",
            padx=10,
            pady=10,
        )
        attacks_frame.pack(padx=20, pady=10, fill="x")

        tk.Checkbutton(
            attacks_frame,
            text="Injection",
            variable=self.attack_vars["injection"],
        ).pack(anchor="w")

        tk.Checkbutton(
            attacks_frame,
            text="Replay",
            variable=self.attack_vars["replay"],
        ).pack(anchor="w")

        tk.Checkbutton(
            attacks_frame,
            text="Payload",
            variable=self.attack_vars["payload"],
        ).pack(anchor="w")

        tk.Checkbutton(
            attacks_frame,
            text="Timing",
            variable=self.attack_vars["timing"],
        ).pack(anchor="w")

        tk.Checkbutton(
            attacks_frame,
            text="Flooding",
            variable=self.attack_vars["flooding"],
        ).pack(anchor="w")


        """ VRSTA IDS """
        self.ids_choice = tk.StringVar(value = "timing")

        ids_frame = tk.LabelFrame(
            self.root,
            text="Izberi metodo zaznavanja:",
            padx=10,
            pady=10,
        )
        ids_frame.pack(padx=20, pady=10, fill="x")

        tk.Radiobutton(
            ids_frame,
            text="Časovna",
            variable=self.ids_choice,
            value="timing",
        ).pack(anchor="w")

        tk.Radiobutton(
            ids_frame,
            text="Entropijska",
            variable=self.ids_choice,
            value="entropy",
        ).pack(anchor="w")

        tk.Radiobutton(
            ids_frame,
            text="Hibridna",
            variable=self.ids_choice,
            value="hybrid",
        ).pack(anchor="w")


        """ TRAJANJE SIMULACIJE """

        duration_frame = tk.Frame(self.root)
        duration_frame.pack(
            padx=20,
            pady=(5, 20),
        )

        duration_label = tk.Label(
            duration_frame,
            text="Trajanje simulacije [s]:",
        )
        duration_label.pack(side=tk.LEFT, padx=(10, 20))

        self.duration_entry = tk.Entry(
            duration_frame,
            width=10,
        )
        self.duration_entry.insert(0, "20")
        self.duration_entry.pack(side=tk.LEFT)

        """NAPREDNE NASTAVITVE"""

        self.advanced_settings_button = tk.Button(
            self.root,
            text="Napredne nastavitve",
            width=20,
            command=self.open_advanced_settings,
            state=tk.NORMAL
        )
        self.advanced_settings_button.pack(pady=(10,2))

        self.start_button = tk.Button(
            self.root,
            text="Začni zaznavanje",
            width=20,
            command=self.start_detecting,
            state=tk.DISABLED
        )
        self.start_button.pack(pady=(10,2))

        self.advanced_frame = tk.LabelFrame(
            self.root,
            text="Napredne nastavitve",
            padx=10,
            pady=10,
        )
        """entropy window"""
        tk.Label(
            self.advanced_frame,
            text="Velikost entropijskega okna:",
        ).pack(anchor="w")

        self.window_entry = tk.Entry(
            self.advanced_frame,
            width=10,
        )
        self.window_entry.insert(0, "100")
        self.window_entry.pack(anchor="w")

        """toleranca timing ids"""

        tk.Label(
            self.advanced_frame,
            text="Toleranca časovnega IDS [%]:",
        ).pack(anchor="w")

        self.tolerance_entry = tk.Entry(
            self.advanced_frame,
            width=10,
        )
        self.tolerance_entry.insert(0, "5")
        self.tolerance_entry.pack(anchor="w")


        tk.Label(
            self.advanced_frame,
            text="Trajanje učenja [s]:",
        ).pack(anchor="w")

        self.learning_time_entry = tk.Entry(
            self.advanced_frame,
            width=10,
        )
        self.learning_time_entry.insert(0, "20")
        self.learning_time_entry.pack(anchor="w")

    def start_detecting(self) -> None:
        """Začne z izvajanjem simulacije s klikom na gumb."""
        duration = self.duration_entry.get().strip()

        try:
            duration = float(duration)

            if duration <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Neveljaven vnos",
                "Trajanje simulacije mora biti pozitivno število.",
            )
            return

        selected_attacks = [
            attack_name
            for attack_name, selected in self.attack_vars.items()
            if selected.get()
        ]

        selected_ids = self.ids_choice.get()

        self.detect_callback(
            duration, 
            selected_attacks,
            selected_ids
            )

    def start_learning(self):
        """Začne učenje refrenčnih profilov z naprednimi nastavitvami."""
        window_size = self.window_entry.get().strip()
        tolerance = self.tolerance_entry.get().strip()
        learning_duration = self.learning_time_entry.get().strip()


        try:
            window_size = int(window_size)
            tolerance = float(tolerance)
            learning_duration = float(learning_duration)

            if window_size <= 0 or tolerance <= 0 or learning_duration <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Neveljaven vnos",
                "Napredne nastavitve morajoi biti pozitivne.",
            )
            return

        learning_successful = self.learn_callback(window_size, tolerance, learning_duration)

        if not learning_successful:
            messagebox.showinfo(
                "Učenje ni uspelo",
                "Profili niso bili pravilno izracunani",
            )
            return 

        self.advanced_frame.pack_forget()
        self.root.geometry("360x630")
        self.start_button.config(state=tk.NORMAL)
        self.advanced_settings_button.config(state=tk.DISABLED)
        self.learn_button.config(state=tk.DISABLED)
        messagebox.showinfo(
            "Učenje je uspelo.",
            "Časovni in entropijski IDS sta naučena."
            )

    def open_advanced_settings(self) -> None:
        """Odpre napredne nastavitve."""

        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
            self.root.geometry("360x630")

        else:
            self.advanced_frame.pack(
                padx=20,
                pady=10,
                fill="x",
            )
            self.root.geometry("360x820")


    def run(self) -> None:
        self.root.mainloop()


        