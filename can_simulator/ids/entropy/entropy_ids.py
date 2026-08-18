"""Implementacija entropijskega sistema za zaznavanje napadov."""

import can
import threading

from .entropy_profile import EntropyProfile, EntropyType
from ids.detection_event import DetectionType, EntropyDetectionEvent

class EntropyIDS:
    """Entropijski IDS za učenje profilov in zaznavanje anomalij."""

    def __init__(self, window_size:int):
        self.bus = can.Bus(
            channel="vcan0",
            interface="socketcan",
        )
        self.window_size = window_size
        self.learning_stop = threading.Event()
        self.detecting_stop = threading.Event()

        self.learning_ready = threading.Event()
        self.detecting_ready = threading.Event()

        
        self.profiles: dict[EntropyType, EntropyProfile] = {
            EntropyType.ID_BASED: EntropyProfile(
                window_size=self.window_size,
                entropy_type=EntropyType.ID_BASED,
            ),
            EntropyType.PAYLOAD_BASED: EntropyProfile(
                window_size=self.window_size,
                entropy_type=EntropyType.PAYLOAD_BASED,
            ),
            EntropyType.ID_PAYLOAD_BASED: EntropyProfile(
                window_size=self.window_size,
                entropy_type=EntropyType.ID_PAYLOAD_BASED,
            ),
        }
 
        self.window_data: list[can.Message] = []
        self.alarms: list[EntropyDetectionEvent] = []


    """ LEARNING """

    def learn(self) -> None:
        """Ustvari referenčne entropijske profile iz učnega prometa."""

        self.learning_stop.clear()
        self.learning_ready.clear()
        self.clear_bus_buffer()
        self.learning_ready.set()

        while True:
            msg = self.bus.recv(timeout=0.1)

            if msg is None: 
                if self.learning_stop.is_set():
                    break
                continue

            self.window_data.append(msg)

            if len(self.window_data) == self.window_size:
                self.profiles[EntropyType.ID_BASED].add_window(self.window_data)
                self.profiles[EntropyType.PAYLOAD_BASED].add_window(self.window_data)
                self.profiles[EntropyType.ID_PAYLOAD_BASED].add_window(self.window_data)
                self.window_data.clear()

        self.profiles[EntropyType.ID_BASED].calculate_profile()
        self.profiles[EntropyType.PAYLOAD_BASED].calculate_profile()
        self.profiles[EntropyType.ID_PAYLOAD_BASED].calculate_profile()
                        

    """ DETECTING """

    def detect(self) -> None:
        """Analizira promet in zazna odstopanja entropije."""

        if not self.profiles:
            raise ValueError("Entropijski profili niso izračunani.")

        self.alarms.clear()
        self.window_data.clear()

        self.detecting_stop.clear()
        self.detecting_ready.clear()
        self.clear_bus_buffer()
        self.detecting_ready.set()

        while True:
            msg = self.bus.recv(timeout=0.1)

            if msg is None:
                if self.detecting_stop.is_set():
                    break
                continue

            self.window_data.append(msg)

            if len(self.window_data) < self.window_size: continue

            if len(self.window_data) > self.window_size:
                raise RuntimeError("Zaznavno okno je preseglo nastavljeno velikost.")

            for entropy_type, profile in self.profiles.items():

                observed_entropy = profile.entropy_from_window(self.window_data)
                detection_type = profile.check_entropy(observed_entropy)

                if detection_type != DetectionType.NORMAL:
                    self.alarms.append(
                        EntropyDetectionEvent(
                            timestamp=self.window_data[-1].timestamp,
                            can_id=None,
                            detection_type=detection_type,
                            entropy_type=entropy_type,
                            observed_entropy=observed_entropy,
                            expected_entropy=profile.expected_entropy,
                            lower_bound=profile.lower_bound,
                            upper_bound=profile.upper_bound,
                            window_size=self.window_size,
                        )
                    )

            self.window_data.clear()


    def stop_learning(self) -> None:
        self.learning_stop.set()

    def stop_detecting(self) -> None:
        self.detecting_stop.set()

    def shutdown(self) -> None:
        """Zapre SocketCAN vodilo"""
        self.bus.shutdown()

    def clear_bus_buffer(self) -> None:
        """Izprazni buffer"""
        while self.bus.recv(timeout=0) is not None:
            pass


