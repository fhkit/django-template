from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import SystemMessage, User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    # The custom form handling for creating a user
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email_address",
        "email_verified",
        "tmp_email_address",
        "is_active",
        "is_admin",
        "default_superuser",
    )

    list_filter = ("is_active", "is_admin", "default_superuser")

    readonly_fields = ("is_admin", "default_superuser", "created_at")

    fieldsets = (
        (None, {"fields": ("username", "is_active", "ban_reason")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Contact info",
            {
                "fields": (
                    "email_address",
                    "tmp_email_address",
                    "email_verified",
                    "email_token",
                    "email_token_created",
                    "phone_number",
                    "tmp_phone_number",
                )
            },
        ),
        (
            "Contact data anti-spam",
            {
                "fields": (
                    "last_phone_request",
                    "last_phone_code_request",
                    "password_reset_token_created",
                )
            },
        ),
        ("Permissions", {"fields": ("utype", "is_admin", "default_superuser")}),
        ("Meta", {"fields": ("created_at", "last_logout_all")}),
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"fields": ("username", "utype", "password1", "password2")}),
    )

    search_fields = ("id", "username", "email_address")
    ordering = ("id",)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


# Add SystemMessageAdmin
class SystemMessageAdmin(admin.ModelAdmin):
    list_display = ("message", "code", "user", "created_at")


admin.site.register(SystemMessage, SystemMessageAdmin)
