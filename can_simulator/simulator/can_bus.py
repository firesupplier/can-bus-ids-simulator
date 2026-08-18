"""
Model CAN Bus vodila, prejme okvirje in načrtuje CAN komunikacijo.

- Pogleda katera imajo enak timestamp,
- izbere tistega z višjo prioriteto (ID),
- zamakne čas prenosa ostalih za čas prenosa.
"""
from models import CANFrame

class CANBus:

    def __init__(
            self,
            bitrate: int
            ):
        self.bitrate = bitrate


    def can_simulation(self, frames:list[CANFrame]) -> list[CANFrame]:

        if not frames: return []

        remaining_frames = frames.copy()
        queue: list[CANFrame] = []

        remaining_frames.sort(key=lambda frame: (frame.timestamp, frame.can_id))
        can_free_at = remaining_frames[0].timestamp


        while remaining_frames:
            frames_eligible = [frame for frame in remaining_frames if frame.timestamp <= can_free_at]

            if not frames_eligible:
                selected_frame = remaining_frames[0]
                self.can_free_at = selected_frame.timestamp

            else:
                frames_eligible.sort(key=lambda frame: frame.can_id)
                selected_frame = frames_eligible[0]
                selected_frame.timestamp = can_free_at
                

            send_time = (47 + selected_frame.dlc * 8) / self.bitrate
            can_free_at += send_time

            queue.append(selected_frame)
            remaining_frames.remove(selected_frame)

        return queue





        



    
