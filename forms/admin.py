from django.contrib import admin

from .models import KanbonForm


# class KanbonFieldInline(admin.TabularInline):
#     model = KanbonField
#     extra = 0

#     # exclude fields
#     exclude = (
#         'help_text',
#         'field_options'
#     )


# Add KanbonFormAdmin
class KanbonFormAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        #'organization',
        "name",
        "created_by",
        "created_at",
    )

    search_fields = (
        "name",
        #'organization__display_name',
        "created_by__email_address",
        "created_by__first_name",
        "created_by__last_name",
    )

    # inlines = [KanbonFieldInline]


admin.site.register(KanbonForm, KanbonFormAdmin)


# class ConditionInline(admin.TabularInline):
#     model = Condition
#     extra = 0

#     fk_name = 'field'


# Add KanbonFieldAdmin
# class KanbonFieldAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'form',
#         'title',
#         'field_type',
#         'created_by',
#         'created_at'
#     )

#     search_fields = (
#         'title',
#         'form__title',
#         'form__organization__display_name'
#     )

#     #inlines = [ConditionInline]


# admin.site.register(KanbonField, KanbonFieldAdmin)


# Add ConditionAdmin
# class ConditionAdmin(admin.ModelAdmin):
#     list_display = (
#         'id',
#         'field',
#         'content',
#         'operator'
#     )

#     search_fields = (
#         'field__title',
#         'field__form__title',
#         'field__form__organization__display_name'
#     )


# admin.site.register(Condition, ConditionAdmin)
