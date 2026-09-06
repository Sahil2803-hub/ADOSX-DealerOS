import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand

from reconciliation.models import (
    Disagreement,
    Location,
    SystemARecord,
    SystemBRecord,
)


# Project root:
# ADOSX-DealerOS/
BASE_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = BASE_DIR / "data"


def clean(value):
    """Remove surrounding whitespace and convert blank values to None."""
    if value is None:
        return None

    value = value.strip()

    return value if value else None


def parse_decimal(value):
    """Safely convert a CSV value to Decimal."""
    value = clean(value)

    if value is None:
        return None

    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def parse_date(value):
    """Safely convert YYYY-MM-DD to a Python date."""
    value = clean(value)

    if value is None:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def normalize_record_ref(value):
    """
    Normalize System B record references.

    Example:
        EVT-1001 -> EVT1001
        evt_1001 -> EVT1001
        EVT 1001 -> EVT1001
    """
    value = clean(value)

    if value is None:
        return None

    value = value.upper()

    # Remove spaces, underscores and hyphens.
    value = re.sub(r"[\s_\-]", "", value)

    return value


class Command(BaseCommand):
    help = "Import DealerOS CSV data into the database."

    def handle(self, *args, **options):
        self.stdout.write("Starting DealerOS data import...")

        self.import_locations()
        self.import_system_a()
        self.import_system_b()

        self.stdout.write(
            self.style.SUCCESS(
                "Data import completed successfully."
            )
        )

    def import_locations(self):
        """Import locations.csv."""

        path = DATA_DIR / "locations.csv"

        if not path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"File not found: {path}"
                )
            )
            return

        created = 0
        updated = 0

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                location_id = clean(
                    row.get("location_id")
                )

                if not location_id:
                    continue

                _, was_created = Location.objects.update_or_create(
                    location_id=location_id,
                    defaults={
                        "org_id": (
                            clean(row.get("org_id"))
                            or ""
                        ),
                        "location_name": (
                            clean(row.get("location_name"))
                            or ""
                        ),
                    },
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            f"Locations: "
            f"{created} created, "
            f"{updated} updated."
        )

    def import_system_a(self):
        """Import system_a.csv."""

        path = DATA_DIR / "system_a.csv"

        if not path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"File not found: {path}"
                )
            )
            return

        created = 0
        updated = 0
        invalid_values = 0

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                record_id = clean(
                    row.get("record_id")
                )

                if not record_id:
                    continue

                raw_base_value = clean(
                    row.get("base_value")
                )

                raw_adjustment = clean(
                    row.get("adjustment")
                )

                raw_total_value = clean(
                    row.get("total_value")
                )

                base_value = parse_decimal(
                    raw_base_value
                )

                adjustment = parse_decimal(
                    raw_adjustment
                )

                total_value = parse_decimal(
                    raw_total_value
                )

                if (
                    raw_base_value is not None
                    and base_value is None
                ):
                    invalid_values += 1

                if (
                    raw_adjustment is not None
                    and adjustment is None
                ):
                    invalid_values += 1

                if (
                    raw_total_value is not None
                    and total_value is None
                ):
                    invalid_values += 1

                _, was_created = (
                    SystemARecord.objects.update_or_create(
                        record_id=record_id,
                        defaults={
                            "location_id": (
                                clean(
                                    row.get("location_id")
                                )
                                or ""
                            ),
                            "event_date": parse_date(
                                row.get("event_date")
                            ),
                            "category_code": (
                                clean(
                                    row.get("category_code")
                                )
                                or ""
                            ),
                            "actor_id": (
                                clean(
                                    row.get("actor_id")
                                )
                                or ""
                            ),
                            "base_value": base_value,
                            "adjustment": adjustment,
                            "total_value": total_value,
                            "state": (
                                clean(row.get("state"))
                                or ""
                            ),
                        },
                    )
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            f"System A: "
            f"{created} created, "
            f"{updated} updated, "
            f"{invalid_values} invalid numeric "
            f"values converted to NULL."
        )

    def import_system_b(self):
        """Import system_b.csv."""

        path = DATA_DIR / "system_b.csv"

        if not path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"File not found: {path}"
                )
            )
            return

        created = 0
        updated = 0
        invalid_values = 0

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                entry_id = clean(
                    row.get("entry_id")
                )

                if not entry_id:
                    continue

                raw_record_ref = clean(
                    row.get("record_ref")
                )

                normalized_ref = normalize_record_ref(
                    raw_record_ref
                )

                raw_value = clean(
                    row.get("value")
                )

                value = parse_decimal(
                    raw_value
                )

                if (
                    raw_value is not None
                    and value is None
                ):
                    invalid_values += 1

                _, was_created = (
                    SystemBRecord.objects.update_or_create(
                        entry_id=entry_id,
                        defaults={
                            "record_ref": (
                                raw_record_ref
                                or ""
                            ),
                            "normalized_record_ref": (
                                normalized_ref
                                or ""
                            ),
                            "location_id": (
                                clean(
                                    row.get("location_id")
                                )
                                or ""
                            ),
                            "recorded_on": parse_date(
                                row.get("recorded_on")
                            ),
                            "value": value,
                            "label": (
                                clean(row.get("label"))
                                or ""
                            ),
                        },
                    )
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            f"System B: "
            f"{created} created, "
            f"{updated} updated, "
            f"{invalid_values} invalid numeric "
            f"values converted to NULL."
        )