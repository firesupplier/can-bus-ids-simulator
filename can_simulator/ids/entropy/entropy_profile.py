"""Profili za hrambo refrenčne entropije, glede na zaznavne simbole."""

import math
import statistics
import can
from collections import Counter
from ids.detection_event import DetectionType, EntropyType


class EntropyProfile:
    """Hrani in izračuna referenčni entropijski profil."""

    MIN_WINDOWS = 30
    MIN_TOLERANCE = 0.005
    RELATIVE_TOLERANCE = 0.01

    def __init__(
        self,
        window_size: int,
        entropy_type: EntropyType, 
    ) -> None:

        if window_size <= 0:
            raise ValueError("Velikost okna mora biti večja od 0.")
        
        self.window_size: int = window_size
        self.entropy_type: EntropyType = entropy_type
        self.entropy_values: list[float] = []

        self.expected_entropy: float | None = None
        self.tolerance: float | None = None
        self.lower_bound: float | None = None
        self.upper_bound: float | None = None

        self.is_calculated: bool = False

    def add_window(self, window_data: list[can.Message]) -> None:
        """Iz učnega okna izračuna entropijo in jo shrani."""

        entropy_value = self.entropy_from_window(window_data)
        self.entropy_values.append(entropy_value)


    def entropy_from_window(self, window_data: list[can.Message]) -> float:
        """Iz komunikacijskega okna izbere simbole in izračuna njihovo Shannonovo entropijo."""

        if len(window_data) != self.window_size:
            raise ValueError(f"Okno mora vsebovati natanko {self.window_size} sporočil.")
        
        if self.entropy_type == EntropyType.ID_BASED:
            symbols = [msg.arbitration_id for msg in window_data]

        elif self.entropy_type == EntropyType.PAYLOAD_BASED:
            symbols = [bytes(msg.data) for msg in window_data]

        elif self.entropy_type == EntropyType.ID_PAYLOAD_BASED:
            symbols = [(msg.arbitration_id, bytes(msg.data)) for msg in window_data]

        else:
            raise ValueError(f"Nepodprta vrsta entropije: {self.entropy_type}")

        return self.calculate_entropy(symbols)


    @staticmethod
    def calculate_entropy(symbols: list[object]) -> float:
        """Izračuna Shannonovo entropijo podanih simbolov."""

        if not symbols:
            raise ValueError("Entropije praznega seznama ni mogoče izračunati.")

        frequencies = Counter(symbols)
        total_symbols = len(symbols)

        entropy = 0.0
        for count in frequencies.values():
            probability = count / total_symbols
            entropy -= probability * math.log2(probability)

        return entropy

    def calculate_profile(self) -> None:
        """Iz učnih entropij izdela referenčni profil."""

        if len(self.entropy_values) < self.MIN_WINDOWS:
            raise ValueError(
                "Premalo učnih oken za izdelavo entropijskega profila: "
                f"{len(self.entropy_values)} od zahtevanih "
                f"{self.MIN_WINDOWS}."
            )

        self.expected_entropy = statistics.median(self.entropy_values)

        abs_dev = [abs(value - self.expected_entropy)for value in self.entropy_values]

        mad = statistics.median(abs_dev)

        #jitter
        madn = mad / 0.6745

        self.tolerance = max(3*madn,self.RELATIVE_TOLERANCE* self.expected_entropy)

        lower_bound = self.expected_entropy - self.tolerance
        upper_bound = self.expected_entropy + self.tolerance

        # vecje nihanje entropije

        lower_min = min(self.entropy_values) - self.MIN_TOLERANCE
        upper_max = max(self.entropy_values) + self.MIN_TOLERANCE

        self.lower_bound = max(0.0, min(lower_min, lower_bound))
        self.upper_bound = max(upper_max, upper_bound)

        self.is_calculated = True

    def check_entropy(
        self,
        entropy_value: float,
    ) -> DetectionType:
        """Razvrsti entropijo okna glede na referenčni profil."""

        if not self.is_calculated:
            raise ValueError("Entropijski profil še ni izračunan.")

        if (self.lower_bound is None or self.upper_bound is None):
            raise ValueError("Meji entropijskega profila nista določeni.")

        if entropy_value < self.lower_bound:
            return DetectionType.ENTROPY_TOO_LOW

        if entropy_value > self.upper_bound:
            return DetectionType.ENTROPY_TOO_HIGH

        return DetectionType.NORMAL













        



    