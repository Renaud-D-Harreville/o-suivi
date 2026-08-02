"""Migration script: convert beacon 'gate' field to 'is_ph' boolean.

Converts:
  - "gate": "PH1"|"PH2"|... → "is_ph": true
  - "gate": null             → "is_ph": false

Applies to:
  - data/templates/*.json (beacons array)
  - data/events/*/event.json (beacons array)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def migrate_beacons(beacons: list[dict]) -> bool:
    """Migrate beacons in place. Returns True if any change was made."""
    changed = False
    for beacon in beacons:
        if "gate" in beacon:
            beacon["is_ph"] = beacon["gate"] is not None
            del beacon["gate"]
            changed = True
    return changed


def migrate_file(filepath: Path) -> None:
    """Migrate a single JSON file."""
    with filepath.open() as f:
        data = json.load(f)

    changed = False

    if "beacons" in data:
        changed = migrate_beacons(data["beacons"]) or changed

    if changed:
        with filepath.open("w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Migrated: {filepath}")
    else:
        print(f"  ⏭️  No change: {filepath}")


def main() -> None:
    print("=== Migration: gate → is_ph ===\n")

    # Templates
    templates_dir = DATA_DIR / "templates"
    if templates_dir.exists():
        print("Templates:")
        for f in sorted(templates_dir.glob("*.json")):
            migrate_file(f)
    else:
        print("No templates directory found.")

    print()

    # Events
    events_dir = DATA_DIR / "events"
    if events_dir.exists():
        print("Events:")
        for event_dir in sorted(events_dir.iterdir()):
            event_file = event_dir / "event.json"
            if event_file.exists():
                migrate_file(event_file)
    else:
        print("No events directory found.")

    print("\n=== Migration complete ===")


if __name__ == "__main__":
    main()

