"""
Modul simulira scenarije napadov na CAN komunikacijo.
- Injection,
- Replay,
- Timing,
- Payload,
- High Frequency (flooding/dos)
"""
from models import CANFrame

class AttackScenario:
    """
    Abstraktni razred s skupnim vmesnikom apply.
    """

    def apply(self, frames: list[CANFrame]) -> list[CANFrame]:
        raise NotImplementedError


class Injection(AttackScenario):
    """
    Simulacija napada z vbrizgavanjem. Doda en okvir prometu.
    """

    def __init__(
        self,
        timestamp: float,
        can_id: int,
        data: bytes,
    ) -> None:
        
        self.timestamp = timestamp
        self.can_id = can_id
        self.data = data

    def apply(self, frames: list[CANFrame]) -> list[CANFrame]:

        frame = CANFrame(
            timestamp = self.timestamp,
            can_id = self.can_id,
            data = self.data,
            source_ecu="Attacker",
            is_attack=True,
            attack_type="Injection"
        )

        frames.append(frame)
        
        frames.sort(key=lambda frame: frame.timestamp)
        return frames
    

class Replay(AttackScenario):
    """
    Simulira napad z ponovno oddajo okvirja z novim časovnim žigom. Doda en okvir prometu.
    """

    def __init__(
        self,
        timestamp: float,
        can_id: int,
    ) -> None:
        
        self.timestamp = timestamp
        self.can_id = can_id

    def apply(self, frames: list[CANFrame]) -> list[CANFrame]:

        for frame in reversed(frames):

            if (self.can_id == frame.can_id) and (self.timestamp > frame.timestamp):

                replayed_frame = CANFrame(
                    timestamp = frame.timestamp,
                    can_id = self.can_id,
                    data = frame.data,
                    source_ecu = "Attacker",
                    is_attack = True,
                    attack_type = "Replay"
                )

                frames.append(replayed_frame)
        frames.sort(key=lambda frame: frame.timestamp)
        return frames
            
        #raise ValueError(f"Ni okvirja z ID: {self.can_id}")

        
        


class TimingAttack(AttackScenario):
    """
    Simulacija napada s spreminjanjem časovnega žiga okvirjev z določenim ID, 
    v določenem časovnem intervalu. 
    """

    def __init__(
        self,
        delay: float,
        can_id: int,
        start_time: float,
        end_time: float
        
    ) -> None:
        
        self.delay = delay
        self.can_id = can_id
        self.start_time = start_time
        self.end_time = end_time

    def apply(self, frames: list[CANFrame]) -> list[CANFrame]:

        for frame in frames:

            if (self.can_id == frame.can_id) and (self.start_time <= frame.timestamp <= self.end_time):
                frame.timestamp = frame.timestamp + self.delay
                frame.is_attack = True
                frame.attack_type = "Timing"
        
        frames.sort(key=lambda frame: frame.timestamp)
        return frames

        
class PayloadAttack(AttackScenario):
    """
    Simulacija napada s spreminjanjem koristne vsebine obstoječega okvirja
    znotraj določenega časovnega intervala. 
    """

    def __init__(
        self,
        data: bytes,
        can_id: int,
        start_time: float,
        end_time: float
    ) -> None:
        
        self.data = data
        self.can_id = can_id
        self.start_time = start_time
        self.end_time = end_time

    def apply(self, frames: list[CANFrame]) -> list[CANFrame]:

        for frame in frames:

            if (self.can_id == frame.can_id) and (self.start_time <= frame.timestamp <= self.end_time):
                frame.data = self.data
                frame.is_attack = True
                frame.attack_type = "Payload"

        frames.sort(key=lambda frame: frame.timestamp)
        return frames


class Flooding(AttackScenario):
    """
    Simulira flooding/dos napad.
    """

    def __init__(
        self,
        can_id: int,
        data: bytes,
        start_time: float,
        end_time: float,
        period: float
    ) -> None:
        
        self.can_id = can_id
        self.data = data
        self.start_time = start_time
        self.end_time = end_time
        self.period = period

        if period <= 0:
            raise ValueError("Perioda mora biti večja od 0.")

        if end_time < start_time:
            raise ValueError(
                "Končni čas mora biti večji ali enak začetnemu času."
            )
        
        if len(data) > 8:
            raise ValueError(
                "Klasični CAN okvir lahko vsebuje največ 8 podatkovnih bajtov."
            )


    def apply(self, frames: list[CANFrame]) -> list[CANFrame]:

        time_track = self.start_time

        while time_track <= self.end_time:

            frame = CANFrame(
                timestamp = time_track,
                can_id = self.can_id,
                data = self.data,
                source_ecu="Attacker",
                is_attack=True,
                attack_type="Flooding"

            )

            frames.append(frame)
            time_track += self.period
        frames.sort(key=lambda frame: frame.timestamp)
        return frames

        