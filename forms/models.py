from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models


class KanbonForm(models.Model):
    # organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, related_name='forms',
    #                                 null=True, blank=True)

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # A status is stored on the form.
    # A form is not available for the employees on the mobile app when its inactive.
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    )

    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="ACTIVE")

    # The field order stores all fields in the order they are displayed on the mobile app.
    field_order = models.JSONField(null=True, blank=True, default=list)

    # Stores the monthly activity over a period of 12 months.
    activity_metrics = models.JSONField(null=True, blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="forms_created",
        null=True,
        blank=True,
    )

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="forms_deleted",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def is_deleted(self):
        return self.deleted_at is not None

    # override save()
    def save(self, *args, **kwargs):
        if not self.organization:
            raise ValidationError(
                "Organization is required.", code="ORGANIZATION_REQUIRED"
            )

        super().save(*args, **kwargs)
