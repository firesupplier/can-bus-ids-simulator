"""Implementacija časovnega sistema za zaznavanje napadov."""

from queue import Empty
import statistics
import time

import can
import threading
from .timing_profile import TimingProfile
from ids.detection_event import DetectionType, TimingDetectionEvent


class TimingIDS:
    """Časovni IDS za učenje profilov in zaznavanje anomalij."""

    def __init__(self, tolerance: float, timestamp_queues):
        self.bus = can.Bus(
            channel="vcan0",
            interface="socketcan"
        )
        self.tolerance = tolerance
        self.timestamp_queues = timestamp_queues
        self.learning_stop = threading.Event()
        self.detecting_stop = threading.Event()

        self.learning_ready = threading.Event()
        self.detecting_ready = threading.Event()

        self.profiles: dict[int, TimingProfile] = {}
        self.alarms: list[TimingDetectionEvent] = []
        

    """ LEARNING """

    def learn(self) -> None:
        """Ustvari referenčne časovne profile iz učnega prometa."""

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

            try:
                recieve_time = self.timestamp_queues[msg.arbitration_id].get(timeout=0.1)

            except Empty:
                if self.detecting_stop.is_set():
                    break
                continue

            if msg.arbitration_id not in self.profiles:
                self.profiles[msg.arbitration_id] = TimingProfile(
                    can_id=msg.arbitration_id,
                    last_time=recieve_time,
                    relative_tolerance=self.tolerance,
                )

            else:
                profile = self.profiles[msg.arbitration_id]
                interval = recieve_time - profile.last_time
                profile.intervals.append(interval)
                profile.last_time = recieve_time


        for profile in self.profiles.values(): 
            profile.calculate_profile()



    """ DETECTING """

    def detect(self) -> None:
        """Analizira promet in zazna razlike v časovnih intervalih."""

        self.alarms.clear()
        self.detecting_stop.clear()
        self.clear_bus_buffer()
        self.detecting_ready.clear()

        if not self.profiles:
            raise ValueError("Profili niso bili ustvarjeni.")

        for profile in self.profiles.values():
            if not profile.is_calculated:
                raise ValueError("Vsi profili niso izračunani.")
            profile.last_time = None
            profile.missing_alarm_active = False

        self.detecting_ready.set()

        while True:
            msg = self.bus.recv(timeout=0.001)

            if msg is None: 
                if self.detecting_stop.is_set(): 
                    break
                continue

            try:
                recieve_time = self.timestamp_queues[msg.arbitration_id].get(timeout=0.1)

            except Empty:
                if self.detecting_stop.is_set():
                    break
                continue


            self.check_missing_messages(recieve_time)


            if msg.arbitration_id not in self.profiles:
                self.alarms.append(
                    TimingDetectionEvent(
                        timestamp=recieve_time,
                        can_id=msg.arbitration_id,
                        detection_type=DetectionType.UNKNOWN_ID,
                        observed_interval=None,
                        expected_period=None,
                        lower_bound=None,
                        upper_bound=None,
                    )
                )
                continue

            profile = self.profiles[msg.arbitration_id]

            if profile.missing_alarm_active:
                profile.missing_alarm_active = False
                profile.last_time = recieve_time
                continue

            if profile.last_time is None:
                profile.last_time = recieve_time
                continue

            interval = recieve_time - profile.last_time
            interval_status = profile.check_interval(interval)

            if interval_status != DetectionType.NORMAL:
                self.alarms.append(
                    TimingDetectionEvent(
                        timestamp = recieve_time,
                        can_id = msg.arbitration_id,
                        detection_type = interval_status,
                        observed_interval = interval,
                        expected_period = profile.expected_period,
                        lower_bound = profile.lower_bound,
                        upper_bound = profile.upper_bound,
                    )
                )
            profile.last_time = recieve_time

    def check_missing_messages(self, current_time: float) -> None:
        """Logika za preverjanje manjkajočih sporočil"""

        for profile in self.profiles.values():
            if profile.last_time is None:
                continue

            if profile.missing_threshold is None:
                raise ValueError(
                    f"Prag manjkajočega sporočila za ID "
                    f"{profile.can_id:#05x} ni izračunan."
                )

            elapsed_time = current_time - profile.last_time

            if (
                elapsed_time > profile.missing_threshold
                and not profile.missing_alarm_active
            ):
                self.alarms.append(
                    TimingDetectionEvent(
                        timestamp=current_time,
                        can_id=profile.can_id,
                        detection_type=DetectionType.MISSING_MESSAGE,
                        observed_interval=elapsed_time,
                        expected_period=profile.expected_period,
                        lower_bound=profile.lower_bound,
                        upper_bound=profile.missing_threshold,
                    )
                )

                profile.missing_alarm_active = True


    def stop_learning(self) -> None:
        self.learning_stop.set()

    def stop_detecting(self) -> None:
        self.detecting_stop.set()

    def shutdown(self) -> None:
        """Zapre SocketCAN vodilo."""
        self.bus.shutdown()

    def clear_bus_buffer(self) -> None:
        """Izprazni buffer"""
        while self.bus.recv(timeout=0) is not None:
            pass