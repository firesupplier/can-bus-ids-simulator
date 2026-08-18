"""Profili za hrambo referenčnih časovnih vrednosti."""

import statistics
from ids.detection_event import DetectionType

class TimingProfile:
    """Hrani in izračuna referenčni časovni profil za posamezen CAN ID."""

    MIN_INTERVALS = 20

    def __init__(
        self,
        can_id: int,
        last_time: float,
        relative_tolerance: float
    ) -> None:
        self.can_id = can_id
        self.last_time: float | None = last_time
        self.relative_tolerance = relative_tolerance

        self.intervals: list[float] = []

        self.expected_period: float | None = None
        self.tolerance: float | None = None
        self.lower_bound: float | None = None
        self.upper_bound: float | None = None
        self.is_calculated: bool = False
        self.missing_alarm_active: bool = False
        self.missing_threshold: float | None = None
        
    def calculate_profile(self) -> None:
        """Izračuna časovni profil."""

        if len(self.intervals) < self.MIN_INTERVALS:
            raise ValueError(f"Za profil ID {self.can_id:#05x} je premalo učnih podatkov")

        self.expected_period = statistics.median(self.intervals)

        abs_dev = [abs(self.expected_period - interval) for interval in self.intervals]

        mad = statistics.median(abs_dev)

        # jitter
        madn = mad / 0.6745

        self.tolerance = max(3*madn, self.relative_tolerance*self.expected_period)

        self.lower_bound = max(0.0, self.expected_period - self.tolerance)
        self.upper_bound = self.expected_period + self.tolerance

        # manjkajoce sporocilo, sele ko manjkata dve pojavitvi
        self.missing_threshold = (2 * self.expected_period + self.tolerance)

        self.is_calculated = True


    def check_interval(self, interval: float) -> DetectionType:
        """ Preveri dolžino intervala"""
        if interval < self.lower_bound: 
            return DetectionType.INTERVAL_TOO_SHORT
        elif interval > self.upper_bound:
            return DetectionType.INTERVAL_TOO_LONG
        else: 
            return DetectionType.NORMAL

        



    