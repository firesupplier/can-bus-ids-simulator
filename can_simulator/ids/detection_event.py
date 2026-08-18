"""Razredi za predstavitev dogodkov zaznavanja napadov."""

from dataclasses import dataclass, field
from enum import Enum

class DetectionType(Enum):
    NORMAL = "normal"
    UNKNOWN_ID = "Unknown CAN ID"
    INTERVAL_TOO_SHORT = "Interval too short"
    INTERVAL_TOO_LONG = "Interval too long"
    MISSING_MESSAGE = "Missing message"

    ENTROPY_TOO_LOW = "Entropy too low"
    ENTROPY_TOO_HIGH = "Entropy too high"


class DetectorType(Enum):
    TIMING_IDS = "Timing IDS"
    ENTROPY_IDS = "Entropy IDS"


class EntropyType(Enum):
    ID_BASED = "ID based"
    PAYLOAD_BASED = "Payload based"
    ID_PAYLOAD_BASED = "ID and payload based"

    
@dataclass
class DetectionEvent:
    """Starševski razred, ki hrani kategorizacijo in značilnosti zaznane anomalije."""
    timestamp: float
    can_id: int | None
    detection_type: DetectionType
    detector: DetectorType


@dataclass
class TimingDetectionEvent(DetectionEvent):
    """Dogodek zaznave časovnega IDS, ki definira končni izpis anomalije"""
    detector: DetectorType = field(
        init=False,
        default=DetectorType.TIMING_IDS,
    )

    observed_interval: float | None = None
    expected_period: float | None = None
    lower_bound: float | None = None
    upper_bound: float | None = None

    def __str__(self) -> str:
        if self.detection_type == DetectionType.UNKNOWN_ID:
            return (
                f"[{self.detector.value}] {self.timestamp:.3f} s | "
                f"{self.detection_type.value}\n"
                f"  CAN ID: 0x{self.can_id:03X}"
            )

        if self.detection_type == DetectionType.MISSING_MESSAGE:
            return (
                f"[{self.detector.value}] {self.timestamp:.3f} s | "
                f"{self.detection_type.value}\n"
                f"  CAN ID: 0x{self.can_id:03X}\n"
                f"  Čas od zadnjega sporočila: "
                f"{self.observed_interval:.6f} s\n"
                f"  Prag odsotnosti: "
                f"{self.upper_bound:.6f} s"
            )

        return (
            f"[{self.detector.value}] {self.timestamp:.3f} s | "
            f"{self.detection_type.value}\n"
            f"  CAN ID: 0x{self.can_id:03X}\n"
            f"  Izmerjeni interval: {self.observed_interval:.6f} s\n"
            f"  Pričakovani interval: {self.expected_period:.6f} s\n"
            f"  Dovoljeno območje: "
            f"{self.lower_bound:.6f}–{self.upper_bound:.6f} s"
        )

    
@dataclass
class EntropyDetectionEvent(DetectionEvent):
    """Dogodek zaznave entropijskega IDS, ki definira končni izpis anomalije."""
    detector: DetectorType = field(
        init=False,
        default=DetectorType.ENTROPY_IDS,
    )
    entropy_type: EntropyType | None = None
    observed_entropy: float | None = None
    expected_entropy: float | None = None
    lower_bound: float | None = None
    upper_bound: float | None = None
    window_size: int | None = None

    def __str__(self) -> str:
        entropy_type_text = (
            self.entropy_type.value
            if self.entropy_type is not None
            else "Ni določeno"
        )

        return (
            f"[{self.detector.value}] {self.timestamp:.3f} s | "
            f"{self.detection_type.value}\n"
            f"  Vrsta entropije: {entropy_type_text}\n"
            f"  Izmerjena entropija: {self.observed_entropy:.4f}\n"
            f"  Pričakovana entropija: {self.expected_entropy:.4f}\n"
            f"  Dovoljeno območje: "
            f"{self.lower_bound:.4f}–{self.upper_bound:.4f}\n"
            f"  Velikost okna: {self.window_size}"
        )







