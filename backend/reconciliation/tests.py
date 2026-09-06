from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from .models import (
    Disagreement,
    Location,
    SystemARecord,
    SystemBRecord,
)


class ReconciliationTests(TestCase):

    def setUp(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
            location_name="Location 101",
        )

    def run_reconciliation(self):
        call_command("reconcile")

    def create_system_a(self, record_id="REC-1001", value="1000.00"):
        return SystemARecord.objects.create(
            record_id=record_id,
            location_id="LOC-101",
            total_value=Decimal(value),
        )

    def create_system_b(
        self,
        entry_id="ENT-1001",
        record_ref="REC-1001",
        value="1000.00",
    ):
        return SystemBRecord.objects.create(
            entry_id=entry_id,
            record_ref=record_ref,
            normalized_record_ref=record_ref.replace("-", ""),
            location_id="LOC-101",
            value=Decimal(value),
        )

    def test_missing_in_b(self):
        """
        System A has a record that does not exist in System B.
        """
        self.create_system_a()

        self.run_reconciliation()

        self.assertEqual(
            Disagreement.objects.filter(
                reason="missing_in_b"
            ).count(),
            1,
        )

    def test_orphan_b(self):
        """
        System B has a record that does not exist in System A.
        """
        self.create_system_b(
            record_ref="REC-9999"
        )

        self.run_reconciliation()

        self.assertEqual(
            Disagreement.objects.filter(
                reason="orphan_b"
            ).count(),
            1,
        )

    def test_duplicate_b(self):
        """
        System B contains multiple records for the same reference.
        """
        self.create_system_a()

        self.create_system_b(
            entry_id="ENT-1001",
            record_ref="REC-1001",
        )

        self.create_system_b(
            entry_id="ENT-1002",
            record_ref="REC-1001",
        )

        self.run_reconciliation()

        self.assertEqual(
            Disagreement.objects.filter(
                reason="duplicate_b"
            ).count(),
            1,
        )

    def test_value_mismatch(self):
        """
        System A and System B contain the same record reference
        but different values.
        """
        self.create_system_a(
            value="1000.00"
        )

        self.create_system_b(
            value="1200.00"
        )

        self.run_reconciliation()

        self.assertEqual(
            Disagreement.objects.filter(
                reason="value_mismatch"
            ).count(),
            1,
        )