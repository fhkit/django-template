from datetime import timedelta
from django.core import exceptions
from django.core.validators import validate_email
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone

from uuid import uuid4

from .ban_codes import ban_codes
from .system_messages import system_messages


class UserManager(BaseUserManager):
    def create_user(
        self,
        username: str = None,
        email_address: str = None,
        email_verified: bool = False,
        first_name: str = None,
        last_name: str = None,
        password: str = None,
        utype: int = 1,
        default_superuser: bool = False,
        invite_token: str = None,
    ) -> "User":
        # If no username is set (which is standard, as usernames are only used programmatically), generate a random one.
        if not username:
            username = uuid4()

        if email_address and User.objects.filter(email_address=email_address).exists():
            # There should be only one user with a given email address,
            # therefore objects.get() is ok without error handling.
            user: User = User.objects.get(email_address=email_address)
            if user.check_password(password):
                raise exceptions.ValidationError(
                    "User already registered. Please log in."
                )
            else:
                raise exceptions.ValidationError(
                    "This email address already exists on another account."
                )

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email_address=email_address,
            email_verified=email_verified,
            utype=utype,
            default_superuser=default_superuser,
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(
        self, username, email=None, password=None, default_superuser=False
    ):
        user: User = self.create_user(
            username=username,
            email_address=email,
            password=password,
            utype=9,
            default_superuser=default_superuser,
        )

        user.verify_email()

        return user


class User(AbstractBaseUser):
    # Essential fields
    username = models.CharField(max_length=40, unique=True)
    utype = models.IntegerField(verbose_name="User Type", default=0)
    is_admin = models.BooleanField(default=False)
    default_superuser = models.BooleanField(default=False)

    # Password reset info.
    # - password_reset_token stores the latest token for password reset.
    # - password_reset_token_created stores the time when this token was created.
    # - password_reset_blocked_until ????
    # - password_reset_expiration_time is the time after which the token is no longer valid.
    # - password_reset_duration_between_requests is the time after which a new token can be requested.
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    password_reset_blocked_until = models.DateTimeField(null=True, blank=True)

    # Anti-spam settings
    password_reset_expiration_time = timedelta(minutes=15)
    password_reset_duration_between_requests = timedelta(minutes=12)

    def seconds_until_next_password_reset(self) -> int:
        """
        Returns the number of seconds until the next password reset can be requested.
        If there has never been a password reset request or the last request is older
        than the duration between requests, this function returns 0.
        """

        if not self.password_reset_token or not self.password_reset_token_created:
            return 0

        # To calculate the time until the next password reset is possible,
        # check if the current datetime is greater than the datetime when the token was created
        # plus the password_reset_duration_between_requests.
        time_remaining = (
            self.password_reset_token_created
            + self.password_reset_duration_between_requests
            - timezone.now()
        )

        # If the time remaining is negative, just return 0.
        if time_remaining.total_seconds() < 0:
            return 0

        # Otherwise, return the time remaining in seconds.
        # (time_remaining.total_seconds() returns a float, so we need to cast it to int.)
        return int(time_remaining.total_seconds())

    def reset_token_valid(self) -> bool:
        """
        Returns True if the password reset token is valid.
        """

        # If there's no token, there's nothing to validate.
        if not self.password_reset_token_created:
            return False

        # Check if password_reset_token_created is not older than password_reset_expiration_time.
        if (
            self.password_reset_token_created + self.password_reset_expiration_time
            < timezone.now()
        ):
            return False

        return True

    # In order to be able to block user accounts and show them a specific message
    is_active = models.BooleanField(default=True)
    ban_reason = models.IntegerField(default=0, null=True, blank=True)

    # Meta fields
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    last_logout_all = models.DateTimeField(null=True, blank=True)

    # Email and phone number
    email_address = models.CharField(
        max_length=255, null=True, blank=True, validators=[validate_email]
    )
    tmp_email_address = models.CharField(
        max_length=255, null=True, blank=True, validators=[validate_email]
    )
    email_token = models.CharField(max_length=255, null=True, blank=True)
    email_token_created = models.DateTimeField(null=True, blank=True)
    # This is required for first-time validations. It is not used afterwards.
    # After the first validation, every other email is saved to tmp_email_address before validation.
    email_verified = models.BooleanField(default=False)

    # Anti-spam settings
    email_verification_expiration_time = timedelta(minutes=15)
    email_block_duration_between_requests = timedelta(minutes=10)

    next_email_verification_request_allowed = models.DateTimeField(
        null=True, blank=True
    )

    def seconds_until_next_email_request(self) -> int:
        """
        Returns the number of seconds until the next email verification can be requested.
        If there has never been a email verification request or the last request is older
        than the duration between requests, this function returns 0.
        """

        if not self.next_email_verification_request_allowed:
            return 0

        # To calculate the time until the next email verification is possible, check the
        # differnece between the current datetime and the datetime when the next request is allowed.
        time_remaining = self.next_email_verification_request_allowed - timezone.now()

        # If the time remaining is negative, just return 0.
        if time_remaining.total_seconds() < 0:
            return 0

        # Otherwise, return the time remaining in seconds.
        # (time_remaining.total_seconds() returns a float, so we need to cast it to int.)
        return int(time_remaining.total_seconds())

    def email_verification_token_valid(self) -> bool:
        """
        Returns True if the email verification token is valid.
        """

        # If there's no token, there's nothing to validate.
        if not self.email_token_created:
            return False

        # Check if password_reset_token_created is not older than password_reset_expiration_time.
        if (
            self.email_token_created + self.email_verification_expiration_time
            < timezone.now()
        ):
            return False

        return True

    phone_number = models.CharField(max_length=255, null=True, blank=True)
    tmp_phone_number = models.CharField(max_length=255, null=True, blank=True)

    # Contact fields
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    avatar = models.JSONField(null=True, blank=True)

    # Personal address fields
    street_1 = models.CharField(max_length=255, null=True, blank=True)
    street_2 = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    # Anti-Spam
    last_phone_request = models.DateTimeField(null=True, blank=True)
    last_phone_code_request = models.DateTimeField(null=True, blank=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def set_last_login(self):
        self.last_login = timezone.now()
        self.save()

    def verify_email(self):
        # If its a first time validation, the self.email_address is to be verified.
        # If the user changes his email address, the self.tmp_email_address is to be verified.
        # If the first email address is to be verified, self.email_verified is currently set to False.
        if not self.email_verified:
            self.email_verified = True
        else:
            if not self.tmp_email_address:
                raise exceptions.ValidationError(
                    "No temporary email address to verify."
                )

            # Set the unverified, tmp_email_address to primary.
            self.email_address = self.tmp_email_address
            self.tmp_email_address = None

        self.email_token = None
        self.save()

        # Add a system message to every user account of which an email address was removed.
        users_to_inform = User.objects.filter(
            Q(tmp_email_address=self.email_address), ~Q(email_address=None)
        )

        for user in users_to_inform:
            user: User
            user.add_system_message(self.email_address, code=1)
            user.tmp_email_address = None
            user.save()

    def verify_phone(self):
        if not self.tmp_phone_number:
            raise exceptions.ValidationError("No temporary phone number to verify.")

        # Set the phone number to primary.
        self.phone_number = self.tmp_phone_number
        self.tmp_phone_number = None
        self.save()

        # Add a system message to every user account of which a phone number was removed.
        users_to_inform = User.objects.filter(
            Q(tmp_phone_number=self.phone_number), ~Q(phone_number=None)
        )

        for user in users_to_inform:
            user: User
            user.add_system_message(self.phone_number, code=2)
            user.tmp_phone_number = None
            user.save()

    def deactivate_account(self, reason):
        self.is_active = False
        self.ban_reason = reason
        self.save()

    @property
    def ban_reason_message(self):
        return ban_codes.get(self.ban_reason)

    # Is this some higher form of python i did there?
    def add_system_message(self, *variables, code=None, message=None):
        """
        Usage:

        If you provide both a code and a message, the message will be ignored.
        For any custom message, the code 0 will be used.
        For more information about codes, see the system_messages.py file.

        User.add_system_message(
            'provide',
            'as many',
            'variables',
            'as you need',
            code=1
        )

        or:

        User.add_system_message(
            'provide',
            'as many',
            'variables',
            'as you need',
            message={'en': 'This is a message with four variables. 1: {} 2: {} 3: {} 4: {}.'}
        )
        """
        if code:
            message = system_messages[code]
        else:
            if not message:
                raise ValueError(
                    "User.add_system_message called without providing either code or message."
                )

            code = 0

        if variables:
            formatted_message = {}

            for locale, text in message.items():
                formatted_text = text.format(*variables)
                formatted_message.update({locale: formatted_text})
        else:
            formatted_message = message

        sys_message: SystemMessage = SystemMessage.objects.create(
            user=self, code=code, message=formatted_message
        )

        sys_message.save()

        return sys_message

    def __str__(self):
        return (
            str(self.first_name) + " " + str(self.last_name) + " (" + str(self.id) + ")"
        )

    def save(self, *args, **kwargs):
        # If the utype attribute is greater than or equal to 7, the is_admin attribute is automatically set to True.
        if self.utype < 7:
            self.is_admin = False
        else:
            self.is_admin = True

        # Remove the ban_reason for active accounts.
        if self.is_active:
            self.ban_reason = 0

        super(User, self).save(*args, **kwargs)

    # Needed for Django functionality
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    # Needed for Django functionality
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    # Needed for Django functionality
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Staff has utype above 7.
        return self.utype >= 7 or self.is_admin


class SystemMessage(models.Model):
    """
    System messages sent to users.
    """

    user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="system_messages"
    )
    # Message in the format {locale: message}
    message = models.JSONField(null=True, blank=True)
    code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    @property
    def custom(self):
        return True if self.code == 0 else False
