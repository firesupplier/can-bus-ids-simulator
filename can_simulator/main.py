
"""
Glavna skripta simulacijskega okolja.

Inicializira GUI, izvaja učenje IDS ter
koordinira simulacijo CAN prometa, napadov in zaznavanja anomalij.
"""

from collections import defaultdict
from queue import Queue

from ids.detection_event import EntropyDetectionEvent, TimingDetectionEvent
from models import CANFrame, SimulationConfig
from simulator.traffic_simulator import TrafficSimulator
from simulator.vehicle import create_vehicle
from simulator.attacks import (
    Injection,
    Replay,
    TimingAttack,
    PayloadAttack,
    Flooding,
)
from simulator.can_bus import CANBus
from simulator.socketcan_player import SocketCANPlayer
from ids.timing import TimingIDS
from ids.entropy import EntropyIDS
from gui import SimulatorGUI
from export.export_txt import export_txt
import threading
import copy


timing_ids = None
entropy_ids = None

timestamp_queues = defaultdict(Queue)

def generate_frames(duration: float) -> list[CANFrame]:
    """Generira normalen CAN promet za podano trajanje simulacije."""

    config = SimulationConfig(
            duration=duration,
            bitrate=500_000
        )
        
    vehicle = create_vehicle()
    simulator = TrafficSimulator(config=config, ecus=vehicle)
    return simulator.run()


def run_learning(window_size: int, tolerance: float, learning_duration: float):
    """Izvede učenje časovnega in entropijskega IDS."""
    print(f"{'Začenjam učenje sistema:':37}{learning_duration:5} s")
    

    print()
    tolerance = tolerance / 100

    global entropy_ids
    global timing_ids

    entropy_ids = EntropyIDS(window_size=window_size)
    timing_ids = TimingIDS(
        tolerance=tolerance,
        timestamp_queues=timestamp_queues
        )


    frames = generate_frames(learning_duration)

    # Simulacija CAN vodila

    # nepadeni
    bus = CANBus(500_000)
    normal_frames_bus = bus.can_simulation(frames)

    from collections import defaultdict

    last_times = {}
    intervals = defaultdict(list)

    for frame in normal_frames_bus:
        if frame.can_id in last_times:
            intervals[frame.can_id].append(
                frame.timestamp - last_times[frame.can_id]
            )

        last_times[frame.can_id] = frame.timestamp


    # ucenje timing
    learning_player = SocketCANPlayer(timestamp_queues=timestamp_queues)

    learning_thread = threading.Thread(
        target=timing_ids.learn,
        name="timing-ids-learning",
    )

    learning_thread.start()
    timing_ids.learning_ready.wait()

    learning_player.play(normal_frames_bus)
    timing_ids.stop_learning()
    learning_thread.join()

     # ucenje entropy
    learning_player = SocketCANPlayer()

    learning_thread = threading.Thread(
        target=entropy_ids.learn,
        name="entropy-ids-learning",
    )

    learning_thread.start()
    entropy_ids.learning_ready.wait()

    learning_player.play(normal_frames_bus)
    entropy_ids.stop_learning()
    learning_thread.join()

    timing_ready = (
        bool(timing_ids.profiles)
        and all(
            profile.is_calculated
            for profile in timing_ids.profiles.values()
        )
    )

    entropy_ready = (
        bool(entropy_ids.profiles)
        and all(
            profile.is_calculated
            for profile in entropy_ids.profiles.values()
        )
    )
    return timing_ready and entropy_ready


def run_detecting(duration: float, attacks_choice: list, ids_choice: str) -> None:
    """Zažene simulacijo CAN prometa, napade in izbrani IDS."""

    print("------------------------------------------")
    print(f"{'Začenjam simulacijo, trajanje:':37} {duration} s")

    frames = generate_frames(duration)

    # Simulacija napadov 

    attacks = {
        "injection": lambda: Injection(
            timestamp=0.15,
            can_id=0x204,
            data=b"\xff\x00",
        ),
        "replay": lambda: Replay(
            timestamp=0.05,
            can_id=0x100,
        ),
        "payload": lambda: PayloadAttack(
            can_id=0x200,
            data=b"\xff\xff",
            start_time=0.40,
            end_time=0.50,
        ),
        "timing": lambda: TimingAttack(
            can_id=0x201,
            delay=0.1,
            start_time=0.50,
            end_time=0.70,
        ),
        "flooding": lambda: Flooding(
            can_id=0x102,
            data=b"\x00",
            start_time=0.60,
            end_time=0.65,
            period=0.001,
        ),
    }

    attacked_frames = copy.deepcopy(frames)

    attack_scenarios = [attacks[attack_name]() for attack_name in attacks_choice]


    for scenario in attack_scenarios:
        attacked_frames = scenario.apply(attacked_frames)


    attacked = [frame for frame in attacked_frames if frame.is_attack]
    print(f"{'Število vseh okvirjev:':37}{len(attacked_frames):5}")
    print(f"{'Število napadenih okvirjev:':37}{len(attacked):5}\n")

    if attack_scenarios:
        print("Izvedeni napadi:")
        for attack_name in attacks_choice:
            print(f"{attack_name:>42}")

        print()


    # Simulacija CAN vodila

    # napadeni
    bus = CANBus(500_000)
    attacked_frames_bus = bus.can_simulation(attacked_frames)


    def run_timing_ids() -> list[TimingDetectionEvent]:
        if not timing_ids.profiles:
            raise ValueError("Časovni IDS še ni bil naučen.")

        detection_player = SocketCANPlayer(
            timestamp_queues=timestamp_queues
        )

        detection_thread = threading.Thread(
            target=timing_ids.detect,
            name="timing-ids-detection",
        )

        detection_thread.start()
        timing_ids.detecting_ready.wait()

        detection_player.play(attacked_frames_bus)

        timing_ids.stop_detecting()
        detection_thread.join()

        alarms = timing_ids.alarms.copy()

        print(f"{'Število alarmov:':37}{len(alarms):5}\n")

        return alarms

    def run_entropy_ids() -> list[EntropyDetectionEvent]:
        if not entropy_ids.profiles:
            raise ValueError("Entropijski IDS še ni bil naučen.")

        detection_player = SocketCANPlayer()

        detection_thread = threading.Thread(
            target=entropy_ids.detect,
            name="entropy-ids-detection",
        )

        detection_thread.start()
        entropy_ids.detecting_ready.wait()

        detection_player.play(attacked_frames_bus)

        entropy_ids.stop_detecting()
        detection_thread.join()

        alarms = entropy_ids.alarms.copy()

        print(f"{'Število alarmov:':37}{len(alarms):5}")

        return alarms

    if ids_choice == "timing": 
        print("Časovno zaznavanje se izvaja...")
        timing_alarms = run_timing_ids()
        export_txt(timing_alarms,"timing_results.txt")

    elif ids_choice == "entropy": 
        print("Entropijsko zaznavanje se izvaja...")
        entropy_alarms = run_entropy_ids()
        export_txt(entropy_alarms,"entropy_results.txt")


def main() -> None:
    """Inicializira GUI in zažene simulator."""
    gui = SimulatorGUI(
        detect_callback=run_detecting,
        learn_callback=run_learning,
        
    )
    try:
        gui.run()
    finally:
        if timing_ids is not None: timing_ids.shutdown()
        if entropy_ids is not None: entropy_ids.shutdown()



if __name__ == "__main__":
    main()





    
