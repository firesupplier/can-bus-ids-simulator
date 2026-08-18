"""Predvajanje simuliranih CAN okvirjev na virtualno SocketCAN vodilo."""

from collections import defaultdict
from queue import Queue

import can
from models import CANFrame
import time

class SocketCANPlayer:
    """Pošilja simulirane CAN okvirje na virtualni CAN vmesnik."""

    def __init__(self, timestamp_queues=None):
        self.bus = can.Bus(
            channel="vcan0",
            interface="socketcan"
        )

        if timestamp_queues is None:
            timestamp_queues = defaultdict(Queue)

        self.timestamp_queues = timestamp_queues

    def send_frame(self, frame: CANFrame):
        self.timestamp_queues[frame.can_id].put(frame.timestamp)

        msg = can.Message(
            arbitration_id = frame.can_id, 
            is_extended_id =  False, 
            data = frame.data
        )
        self.bus.send(msg)

    def play(self, frames:list[CANFrame]):

        if not frames:
            raise ValueError("Seznam okvirjev je prazen.")

        try:
            start_time = time.monotonic()
            wait_time = 0

            for frame in frames:
                wait_time = (start_time + frame.timestamp) - time.monotonic()
                if wait_time > 0: time.sleep(wait_time)
                self.send_frame(frame)

        finally:
            self.shutdown()


    def shutdown(self):
        self.bus.shutdown()
