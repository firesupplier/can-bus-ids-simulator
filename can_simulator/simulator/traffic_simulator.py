"""
Modul za simulacijo periodične CAN komunikacije.

- Iterira skozi vsa ECU vozlišča
- iterira skozi vsa sporočila vozlišča,
- naredi okvirje glede na trenutnen čas simulacije, id, data in source. 
"""
from random import Random

from models import (
    CANFrame,
    ECU, 
    SimulationConfig
)

class TrafficSimulator:
    """
    Simulator za generiranje CAN prometa.
    """
    
    def __init__(
        self,
        config: SimulationConfig,
        ecus: list[ECU],
    ) -> None:
        self.config = config
        self.ecus = ecus
        self.random = Random(config.random_seed)


    def run(self) -> list[CANFrame]:
        """ Izvede CAN sim, rezultat je list ustvarjenih CAN okvirjev"""

        frames: list[CANFrame] = []

        if len(self.ecus) == 0:
            raise ValueError("Simulator nima seznama ECU-jev za generiranje prometa.")

        # obdela vsako vozlišče posebej
        for ecu in self.ecus:
            # obdela vsako sporočilo ecu-ja
            for msg in ecu.messages:

                current_time = msg.start_time

                while current_time <= self.config.duration:
                    frame = self.create_frame(current_time, msg, ecu)

                    frames.append(frame)
                    # periodično pošiljanje
                    current_time += msg.period

        # sortira glede na časovne žige
        frames.sort(key=lambda frame: frame.timestamp)
        return frames
    
    
    def create_frame(self, current_time, msg, ecu) -> CANFrame:
        """
        Ustvari en CAN okvir.
        """
        frame = CANFrame(
            timestamp = current_time, 
            can_id = msg.can_id, 
            data = msg.payload, 
            source_ecu = ecu.name,
        )
        return frame


# kasneje dogodkovno vrsto, kjer simulator vedno obdela naslednji časovno najbližji dogodek.




