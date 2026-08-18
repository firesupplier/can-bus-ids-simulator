# Engine ECU,Brake ECU, Dashboard ECU, Transmission ECU
"""
Definira konkretne ECU-je, njihova sporočila in vrne seznam ECU-jev.

ECU(Messages(ECUMessage))
"""

from models import(
    ECU,
    ECUMessage
)

def create_vehicle() -> list[ECU]:
    """
    Ustvari vozilo s ECU motorja, abs in nadzorne plošče.
    """

    engine_ecu = create_engine_ecu()
    abs_ecu = create_abs_ecu()
    dashboard_ecu = create_dashboard_ecu()

    return [engine_ecu, abs_ecu, dashboard_ecu]


def create_engine_ecu() -> ECU:
    """
    Ustvari ECU motorja in njegova sporočila.
    """
    engine_rpm_msg = ECUMessage(
        name = "Engine RPM",
        can_id = 0x100,
        period = 0.01,
        payload = b"\x03\x20",
        start_time = 0.0,
    )

    engine_temp_msg = ECUMessage(
        name = "Engine Temperature",
        can_id = 0x101,
        period = 0.05,
        payload = b"\x5A",
        start_time = 0.05,
    )


    engine_ecu = ECU (
        name = "Engine ECU",
        messages = [
            engine_rpm_msg,
            engine_temp_msg
        ]
    )
    return engine_ecu


def create_abs_ecu() -> ECU:
    """
    Ustvari ECU abs in njegova sporočila.
    """

    vehicle_speed_msg = ECUMessage(
        name="Vehicle Speed",
        can_id=0x200,
        period=0.02,
        payload=b"\x00\x3C",
        start_time=0.0,
    )

    brake_status_msg = ECUMessage(
        name="Brake Status",
        can_id=0x201,
        period=0.05,
        payload=b"\x00",
        start_time=0.0,
    )

    abs_ecu = ECU(
        name="ABS ECU",
        messages=[
            vehicle_speed_msg,
            brake_status_msg,
        ]
    )

    return abs_ecu


def create_dashboard_ecu() -> ECU:
    """
    Ustvari ECU nadzorne plošče in njena sporočila.
    """

    fuel_level_msg = ECUMessage(
        name="Fuel Level",
        can_id=0x300,
        period=0.5,
        payload=b"\x50",
        start_time=0.0,
    )

    warning_lights_msg = ECUMessage(
        name="Warning Lights",
        can_id=0x301,
        period=0.1,
        payload=b"\x00",
        start_time=0.0,
    )

    dashboard_ecu = ECU(
        name="Dashboard ECU",
        messages=[
            fuel_level_msg,
            warning_lights_msg,
        ]
    )

    return dashboard_ecu