import graphene
from api.permissions import is_org_member
from django.utils import timezone
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_relay import from_global_id
from organization.models import Organization

from .models import KanbonForm


class KanbonFormType(DjangoObjectType):
    class Meta:
        model = KanbonForm
        fields = [
            "name",
            "description",
            "status",
            "field_order",
            "activity_metrics",
            "created_at",
            "updated_at",
            "created_by",
            "fields",
        ]

        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_node(cls, info, id):
        return KanbonForm.objects.get(id=id)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset


class KanbonFieldType(DjangoObjectType):
    class Meta:
        model = KanbonField
        fields = [
            "title",
            "help_text",
            "is_required",
            "field_type",
            "field_options",
            "client_id",
            "conditions",
        ]

        interfaces = (graphene.relay.Node,)


class ConditionType(DjangoObjectType):
    content = GenericScalar()

    class Meta:
        model = Condition
        fields = [
            "compare_to",
            "operator",
            "content",
        ]

        interfaces = (graphene.relay.Node,)


class KanbonFormInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    status = graphene.String()
    field_order = graphene.List(graphene.String)


# Create a Input object for KanbonField
class KanbonFieldInput(graphene.InputObjectType):
    title = graphene.String()
    help_text = graphene.String()
    is_required = graphene.Boolean()
    field_type = graphene.String()
    field_options = GenericScalar()


class ConditionInput(graphene.InputObjectType):
    compare_to = graphene.ID()
    operator = graphene.String()
    content = GenericScalar()


class CreateKanbonForm(graphene.Mutation):
    """
    Create a new form.

    Erros:
    - FORM_NAME_REQUIRED: Cannot create form without a name.
    - FORM_NAME_EXISTS: Cannot create form with a name that already exists within your organization.
    """

    class Arguments:
        org_id = graphene.ID(required=True)
        form_input = KanbonFormInput(required=True)

    form = graphene.Field(KanbonFormType)

    @staticmethod
    @is_org_member("ADMIN")
    def mutate(root, info, org_id: graphene.ID, form_input: KanbonFormInput):
        # Get the organization
        org_id = from_global_id(org_id)[1]
        organization = Organization.objects.get(id=org_id)

        if not form_input.name:
            raise GraphQLError(
                "Form name is required to create a form.", code="FORM_NAME_REQUIRED"
            )

        # Return an error if there's already a form with the same name in the organization.
        if KanbonForm.objects.filter(
            name=form_input.name, organization=organization
        ).exists():
            raise GraphQLError(
                "Form with the same name already exists.", code="FORM_NAME_EXISTS"
            )

        # Create the form
        form: KanbonForm = KanbonForm(
            name=form_input.name,
            description=form_input.description,
            status=form_input.status,
        )

        form.save()

        return CreateKanbonForm(form=form)


class UpdateKanbonForm(graphene.Mutation):
    """
    Update a form.

    Errors:
    - FORM_NAME_EXISTS: Cannot update form with a name that already exists within your organization.
    - NO_INPUT: No input provided.
    """

    class Arguments:
        org_id = graphene.ID(required=True)
        form_id = graphene.ID(required=True)
        form_input = KanbonFormInput()
        delete = graphene.Boolean()

    form = graphene.Field(KanbonFormType)

    @staticmethod
    @is_org_member("ADMIN")
    def mutate(
        root,
        info,
        org_id: graphene.ID,
        form_id: graphene.ID,
        form_input: KanbonFormInput = None,
        delete: bool = False,
    ):
        # Get the organization
        org_id = from_global_id(org_id)[1]
        organization = Organization.objects.get(id=org_id)

        # Get the form
        form_id = from_global_id(form_id)[1]
        form: KanbonForm = KanbonForm.objects.get(id=form_id)

        # If delete is true, delete the form.
        if delete:
            form.deleted_at = timezone.now()
            form.deleted_by = info.context.user
            form.save()

            return UpdateKanbonForm(form=None)

        if not form_input:
            raise GraphQLError("No input provided.", code="NO_INPUT")

        if form_input.name:
            # Return an error if there's already a form with the same name in the organization.
            if KanbonForm.objects.filter(
                name=form_input.name, organization=organization
            ).exists():
                raise GraphQLError(
                    "Form with the same name already exists.", code="FORM_NAME_EXISTS"
                )

            else:
                form.name = form_input.name

        # Update the form
        form.description = (
            form_input.description if form_input.description else form.description
        )
        form.status = form_input.status if form_input.status else form.status
        form.field_order = (
            form_input.field_order if form_input.field_order else form_input.field_order
        )

        form.save()

        return UpdateKanbonForm(form=form)


class CreateKanbonField(graphene.Mutation):
    """
    Responsible for adding a new field to a given form.

    Errors:
    - FORM_DOES_NOT_EXIST: There's no form with the given ID in the organization.
    """

    class Arguments:
        org_id = graphene.ID(required=True)
        form_id = graphene.ID(required=True)
        field_input = KanbonFieldInput(required=True)
        client_id = graphene.String()
        conditions = graphene.List(ConditionInput)

    field = graphene.Field(KanbonFieldType)

    @staticmethod
    @is_org_member("ADMIN")
    def mutate(
        root,
        info,
        org_id: graphene.ID,
        form_id: graphene.ID,
        field_input: KanbonFieldInput,
        conditions: list[ConditionInput] = [],
        client_id: str = None,
    ):
        # Get given organization and form
        org_id = from_global_id(org_id)[1]
        org = Organization.objects.get(id=org_id)

        form_id = from_global_id(form_id)[1]

        try:
            form = KanbonForm.objects.get(id=form_id, organization=org)
        except KanbonForm.DoesNotExist:
            raise GraphQLError(
                "Form with given ID does not exist in given organization.",
                extensions={"code": "FORM_DOES_NOT_EXIST"},
            )

        for condition in conditions:
            pass

        field: KanbonField = KanbonField(
            form=form,
            title=field_input.title,
            help_text=field_input.help_text,
            is_required=field_input.is_required,
            field_type=field_input.field_type,
            field_options=field_input.field_options,
            client_id=client_id,
        )

        field.save()

        return CreateKanbonField(field=field)


class UpdateKanbonField(graphene.Mutation):
    """
    Update a single form field.

    Errors:
    - FIELD_DOES_NOT_EXIST: There's no field with the given ID in the organization.
    - NO_INPUT: No input provided.
    """

    class Arguments:
        org_id = graphene.ID(required=True)
        field_id = graphene.ID(required=True)
        field_input = KanbonFieldInput()
        delete = graphene.Boolean()

    field = graphene.Field(KanbonFieldType)

    @staticmethod
    @is_org_member("ADMIN")
    def mutate(
        root,
        info,
        org_id: graphene.ID,
        field_id: graphene.ID,
        field_input: KanbonFieldInput = None,
        delete: bool = False,
    ):
        # Get the organization
        org_id = from_global_id(org_id)[1]
        org = Organization.objects.get(id=org_id)

        # Get the form
        field_id = from_global_id(field_id)[1]

        try:
            field: KanbonField = KanbonField.objects.get(
                id=field_id, form__organization=org
            )
        except KanbonField.DoesNotExist:
            raise GraphQLError(
                "Field with given ID does not exist in given organization.",
                extensions={"code": "FIELD_DOES_NOT_EXIST"},
            )

        if delete:
            field.deleted_at = timezone.now()
            field.deleted_by = info.context.user
            field.save()

            return UpdateKanbonField(field=None)

        if not field_input:
            raise GraphQLError("No input provided.", code="NO_INPUT")

        # Update the field
        field.title = field_input.title if field_input.title else field.title
        field.help_text = (
            field_input.help_text if field_input.help_text else field.help_text
        )
        field.is_required = (
            field_input.is_required if field_input.is_required else field.is_required
        )
        field.field_type = (
            field_input.field_type if field_input.field_type else field.field_type
        )
        field.field_options = (
            field_input.field_options
            if field_input.field_options
            else field.field_options
        )

        field.save()

        return UpdateKanbonField(field=field)


class Mutation(graphene.ObjectType):
    create_kanbon_form = CreateKanbonForm.Field()
    update_kanbon_form = UpdateKanbonForm.Field()
    create_kanbon_field = CreateKanbonField.Field()
    update_kanbon_field = UpdateKanbonField.Field()
