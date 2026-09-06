from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=100, unique=True)
    org_id = models.CharField(max_length=100)
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.location_id} - {self.location_name}"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=100, unique=True)
    location_id = models.CharField(max_length=100, blank=True)
    event_date = models.DateField(null=True, blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    actor_id = models.CharField(max_length=100, blank=True)
    base_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    adjustment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    total_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.record_id


class SystemBRecord(models.Model):
    entry_id = models.CharField(max_length=100, unique=True)
    record_ref = models.CharField(max_length=100, blank=True)
    normalized_record_ref = models.CharField(max_length=100, blank=True)
    location_id = models.CharField(max_length=100, blank=True)
    recorded_on = models.DateField(null=True, blank=True)
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    label = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.entry_id


class Disagreement(models.Model):
    REASON_CHOICES = [
        ("missing_in_b", "Missing in B"),
        ("orphan_b", "Orphan B"),
        ("duplicate_b", "Duplicate B"),
        ("value_mismatch", "Value mismatch"),
    ]

    record_ref = models.CharField(max_length=100)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    system_a_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    system_b_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    location_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["record_ref", "reason"]

    def __str__(self):
        return f"{self.record_ref} - {self.reason}"