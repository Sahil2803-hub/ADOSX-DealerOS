from collections import defaultdict

from django.core.management.base import BaseCommand

from reconciliation.models import (
    Disagreement,
    SystemARecord,
    SystemBRecord,
)


def normalize_reference(value):
    """
    Normalize record references so values such as:

        REC-1001
        REC1001

    are treated as the same record.
    """
    if value is None:
        return ""

    return "".join(
        character
        for character in str(value).upper()
        if character.isalnum()
    )


class Command(BaseCommand):
    help = "Compare System A and System B records."

    def handle(self, *args, **options):
        self.stdout.write("Starting reconciliation...")

        # Remove results from previous reconciliation runs.
        Disagreement.objects.all().delete()

        system_a_records = list(
            SystemARecord.objects.all()
        )

        system_b_records = list(
            SystemBRecord.objects.all()
        )

        # ---------------------------------------------------------
        # Build System A lookup
        # ---------------------------------------------------------

        system_a_by_ref = {}

        for record in system_a_records:
            normalized_ref = normalize_reference(
                record.record_id
            )

            system_a_by_ref[normalized_ref] = record

        # ---------------------------------------------------------
        # Build System B lookup
        # ---------------------------------------------------------

        system_b_by_ref = defaultdict(list)

        for record in system_b_records:
            normalized_ref = normalize_reference(
                record.record_ref
            )

            system_b_by_ref[normalized_ref].append(record)

        # ---------------------------------------------------------
        # Counters
        # ---------------------------------------------------------

        missing_in_b = 0
        orphan_b = 0
        duplicate_b = 0
        value_mismatch = 0

        # ---------------------------------------------------------
        # Compare System A → System B
        # ---------------------------------------------------------

        for a_record in system_a_records:

            normalized_ref = normalize_reference(
                a_record.record_id
            )

            matching_b_records = system_b_by_ref.get(
                normalized_ref,
                []
            )

            # ---------------------------------------------
            # Missing in System B
            # ---------------------------------------------

            if not matching_b_records:

                Disagreement.objects.create(
                    record_ref=a_record.record_id,
                    reason="missing_in_b",
                    system_a_value=a_record.total_value,
                    system_b_value=None,
                    location_id=a_record.location_id,
                )

                missing_in_b += 1

                continue

            # ---------------------------------------------
            # Duplicate in System B
            # ---------------------------------------------

            if len(matching_b_records) > 1:

                Disagreement.objects.create(
                    record_ref=a_record.record_id,
                    reason="duplicate_b",
                    system_a_value=a_record.total_value,
                    system_b_value=matching_b_records[0].value,
                    location_id=a_record.location_id,
                )

                duplicate_b += 1

            # ---------------------------------------------
            # Value comparison
            # ---------------------------------------------

            b_record = matching_b_records[0]

            a_value = a_record.total_value
            b_value = b_record.value

            # Handle NULL values safely.
            if a_value != b_value:

                Disagreement.objects.create(
                    record_ref=a_record.record_id,
                    reason="value_mismatch",
                    system_a_value=a_value,
                    system_b_value=b_value,
                    location_id=a_record.location_id,
                )

                value_mismatch += 1

        # ---------------------------------------------------------
        # Find orphan records in System B
        # ---------------------------------------------------------

        for b_record in system_b_records:

            normalized_ref = normalize_reference(
                b_record.record_ref
            )

            if normalized_ref not in system_a_by_ref:

                Disagreement.objects.create(
                    record_ref=b_record.record_ref,
                    reason="orphan_b",
                    system_a_value=None,
                    system_b_value=b_record.value,
                    location_id=b_record.location_id,
                )

                orphan_b += 1

        # ---------------------------------------------------------
        # Final summary
        # ---------------------------------------------------------

        total = Disagreement.objects.count()

        self.stdout.write("")
        self.stdout.write(
            "Reconciliation complete."
        )

        self.stdout.write(
            f"Missing in B: {missing_in_b}"
        )

        self.stdout.write(
            f"Orphan B: {orphan_b}"
        )

        self.stdout.write(
            f"Duplicate B: {duplicate_b}"
        )

        self.stdout.write(
            f"Value mismatch: {value_mismatch}"
        )

        self.stdout.write(
            f"Total disagreements: {total}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Reconciliation completed successfully."
            )
        )