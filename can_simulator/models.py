"""
Definira razrede 
- ECUMessage, 
- ECU, 
- CANFrame, 
- SimulationConfig
"""

from dataclasses import dataclass, field 

@dataclass 
class ECUMessage:
    """Definicija ene vrste CAN-sporočila. """
    can_id: int 
    period: float
    payload: bytes
    name: str
    start_time: float = 0.0


    def __post_init__(self) -> None:

        if self.period <= 0:
            raise ValueError("Perioda mora biti večja od 0.")
        
        if self.start_time < 0:
            raise ValueError("Začetni čas mora biti večji ali enak 0.")
        
        if self.can_id < 0x000 or self.can_id > 0x7FF:
            raise ValueError("CAN ID mora biti v razponu 0x000–0x7FF.")
        
        if len(self.payload) > 8:
            raise ValueError("Payload je lahko največ 8 bajtov.")


@dataclass 
class ECU:
    """Eno ECU vozlišče"""
    name: str
    messages: list[ECUMessage] = field(default_factory=list)



@dataclass 
class CANFrame:
    """En okvir komunikacije """
    timestamp: float
    can_id: int
    data: bytes
    source_ecu: str
    is_attack: bool = False
    attack_type: str | None = None

    def __post_init__(self) -> None:
        
        if self.can_id < 0x000 or self.can_id > 0x7FF:
            raise ValueError("CAN ID mora biti v razponu 0x000–0x7FF.")
        
        if len(self.data) > 8:
            raise ValueError("Payload je lahko največ 8 bajtov.")
        
        if self.timestamp < 0:
            raise ValueError("Časovni žig mora biti večji ali enak 0.")
        
        
        if not self.is_attack and self.attack_type is not None:
            raise ValueError("Običajen okvir ne sme imeti določene vrste napada.")
        

        if self.is_attack and self.attack_type is None:
            raise ValueError("Napadalni okvir mora imeti določeno vrsto napada.")

    @property
    def dlc(self) -> int: # data lenth code, vrne število bajtov
        return len(self.data)
    
    def __str__(self) -> str: # data lenth code, vrne število bajtov
        return (
         f"{self.timestamp:.3f} s | "
         f"ID={self.can_id:#05x} | "
         f"DLC={self.dlc} | "
         f"DATA={self.data.hex(' '):5} | "
         f"ECU={self.source_ecu}"
        )


@dataclass
class SimulationConfig:
    """Konfiguracija simulacije"""
    duration: float
    bitrate: int = 500_000
    random_seed: int = 42 # za ponovljivost eksperimentov, jitter, nakljucni payloadi in napadi

    def __post_init__(self) -> None:

        if self.duration <= 0:
            raise ValueError("Dolžina simulacije mora biti večja od 0.")
        
        if self.bitrate <= 0:
            raise ValueError("Bitrate mora biti večji od 0.")


