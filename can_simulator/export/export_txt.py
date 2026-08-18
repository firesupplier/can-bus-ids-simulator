"""Izvoz zaznanih alarmov v TXT datoteko."""

from pathlib import Path
from ids.detection_event import DetectionEvent

def export_txt(events: list[DetectionEvent],filename: str) -> None:

    results_dir = Path(__file__).resolve().parent.parent / "results" 

    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / filename 

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(f"Število zaznanih alarmov: {len(events)}\n\n")

        for i, event in enumerate(events, start=1):
            file.write(f"ALARM {i}\n")
            file.write("-" * 50 + "\n")
            file.write(str(event))
            file.write("\n\n")

    print(f"Rezultati so bili zapisani v: /results/{output_path.name}")
    print()