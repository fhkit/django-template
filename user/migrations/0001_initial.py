# Generated by Django 5.0.6 on 2024-06-18 08:55

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("username", models.CharField(max_length=40, unique=True)),
                ("utype", models.IntegerField(default=0, verbose_name="User Type")),
                ("is_admin", models.BooleanField(default=False)),
                ("default_superuser", models.BooleanField(default=False)),
                (
                    "password_reset_token",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "password_reset_token_created",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "password_reset_blocked_until",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("ban_reason", models.IntegerField(blank=True, default=0, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_logout_all", models.DateTimeField(blank=True, null=True)),
                (
                    "email_address",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        validators=[django.core.validators.EmailValidator()],
                    ),
                ),
                (
                    "tmp_email_address",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        validators=[django.core.validators.EmailValidator()],
                    ),
                ),
                (
                    "email_token",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("email_token_created", models.DateTimeField(blank=True, null=True)),
                ("email_verified", models.BooleanField(default=False)),
                (
                    "next_email_verification_request_allowed",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "tmp_phone_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("avatar", models.JSONField(blank=True, null=True)),
                ("street_1", models.CharField(blank=True, max_length=255, null=True)),
                ("street_2", models.CharField(blank=True, max_length=255, null=True)),
                ("zip_code", models.CharField(blank=True, max_length=255, null=True)),
                ("city", models.CharField(blank=True, max_length=255, null=True)),
                ("country", models.CharField(blank=True, max_length=255, null=True)),
                ("last_phone_request", models.DateTimeField(blank=True, null=True)),
                (
                    "last_phone_code_request",
                    models.DateTimeField(blank=True, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SystemMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.JSONField(blank=True, null=True)),
                ("code", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("read", models.BooleanField(default=False)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="system_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
