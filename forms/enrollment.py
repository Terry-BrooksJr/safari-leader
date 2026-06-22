from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from applications.accounts.models import ROLES, Role, RoleAssignment
from applications.children.models import (
    ALLERGEN_SEVERITY,
    RELATIONSHIP,
    Allergy,
    AuthorizedPickupProfile,
    Child,
    ChildGuardianRelationship,
    CustodyRestriction,
    EmergencyContact,
    GuardianProfile,
    MedicalNote,
    STUDENT_STATUS,
)
from applications.enrollment.models import ChildSchedule, ENROLLMENT_STATUS, Enrollment
from applications.facilities.models import Program
from applications.staffing.models import StaffProfile
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.layout import Column, Div, Field, Fieldset, HTML, Layout, Row
from django.templatetags.static import static


class EnrollmentIntakeForm(forms.Form):
    """
    Single intake form for creating a guardian user, child profile, enrollment,
    schedule, and optional child support records.

    This is intentionally a plain Form because the workflow writes to models
    across multiple apps. The view can instantiate this form and call save()
    after is_valid().
    """

    # Parent / guardian user fields
    parent_first_name = forms.CharField(max_length=150)
    parent_last_name = forms.CharField(max_length=150)
    parent_email = forms.EmailField()
    parent_contact_number = forms.CharField(max_length=12)
    parent_relationship = forms.ChoiceField(choices=RELATIONSHIP.choices)
    parent_is_primary_contact = forms.BooleanField(required=False, initial=True)
    parent_has_custody_rights = forms.BooleanField(required=False, initial=True)
    parent_can_pickup = forms.BooleanField(required=False, initial=True)
    parent_pickup_pin = forms.IntegerField(min_value=0)
    parent_verification_notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )
    # Child fields
    child_first_name = forms.CharField(max_length=325)
    child_last_name = forms.CharField(max_length=325)
    child_date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    child_status = forms.ChoiceField(
        choices=STUDENT_STATUS.choices,
        initial=STUDENT_STATUS.ENROLLED,
    )
    # Optional allergy fields
    has_allergy = forms.BooleanField(required=False)
    allergy_allergen = forms.CharField(max_length=50, required=False)
    allergy_severity = forms.ChoiceField(
        choices=ALLERGEN_SEVERITY.choices,
        required=False,
    )
    allergy_instructions = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )
    # Optional custody restriction fields
    has_custody_restriction = forms.BooleanField(required=False)
    custody_restriction_notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )
    # Enrollment fields
    program = forms.ModelChoiceField(queryset=Program.objects.none())
    enrollment_start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )
    enrollment_end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
    )
    enrollment_status = forms.ChoiceField(
        choices=ENROLLMENT_STATUS.choices,
        initial=ENROLLMENT_STATUS.PENDING,
    )
    # Schedule fields
    instructor = forms.ModelChoiceField(queryset=StaffProfile.objects.none())
    schedule_start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"})
    )
    schedule_end_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    schedule_sunday = forms.BooleanField(required=False)
    schedule_monday = forms.BooleanField(required=False, initial=True)
    schedule_tuesday = forms.BooleanField(required=False, initial=True)
    schedule_wednesday = forms.BooleanField(required=False, initial=True)
    schedule_thursday = forms.BooleanField(required=False, initial=True)
    schedule_friday = forms.BooleanField(required=False, initial=True)
    schedule_saturday = forms.BooleanField(required=False)
    # Optional emergency contact fields
    create_emergency_contact = forms.BooleanField(required=False)
    emergency_first_name = forms.CharField(max_length=80, required=False)
    emergency_last_name = forms.CharField(max_length=80, required=False)
    emergency_contact_number = forms.CharField(max_length=12, required=False)
    emergency_relationship = forms.ChoiceField(
        choices=RELATIONSHIP.choices,
        required=False,
    )
    emergency_is_authorized = forms.BooleanField(required=False, initial=True)
    emergency_verification_notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["program"].queryset = Program.objects.filter(is_active=True)
        self.fields["instructor"].queryset = StaffProfile.objects.all()
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = False

        self.boolean_fields = [
            "parent_is_primary_contact",
            "parent_has_custody_rights",
            "parent_can_pickup",
            "has_allergy",
            "has_custody_restriction",
            "schedule_sunday",
            "schedule_monday",
            "schedule_tuesday",
            "schedule_wednesday",
            "schedule_thursday",
            "schedule_friday",
            "schedule_saturday",
            "create_emergency_contact",
            "emergency_is_authorized",
        ]

        for field_name in self.boolean_fields:
            existing_classes = self.fields[field_name].widget.attrs.get("class", "")
            self.fields[field_name].widget.attrs.update(
                {
                    "class": f"{existing_classes} form-check-input".strip(),
                    "role": "switch",
                }
            )

        self.fields["parent_is_primary_contact"].label = "Parent is primary contact"
        self.fields["parent_has_custody_rights"].label = "Parent has custody rights"
        self.fields["parent_can_pickup"].label = "Parent can pickup"

        # Short labels so each schedule day renders as a compact toggle button.
        day_labels = {
            "schedule_sunday": "Sun",
            "schedule_monday": "Mon",
            "schedule_tuesday": "Tue",
            "schedule_wednesday": "Wed",
            "schedule_thursday": "Thu",
            "schedule_friday": "Fri",
            "schedule_saturday": "Sat",
        }
        for field_name, label in day_labels.items():
            self.fields[field_name].label = label

        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(
                f'<img src="{static("images/img-child-enrollment-form-header.png")}" class="w-75 d-block mx-auto" alt="Child enrollment form header">'
            ),
            Fieldset(
                "Parent / Guardian Information",
                Row(
                    Column(
                        Field("parent_first_name", css_class="col-md-6"),
                    ),
                    Column(
                        Field("parent_last_name", css_class="col-md-6"),
                    ),
                ),
                Row(
                    Column(
                        Field("parent_email", css_class="col-md-6"),
                    ),
                    Column(
                        Field("parent_contact_number", css_class="col-md-6"),
                    ),
                ),
                Row(
                    Column(
                        Row(
                            Column(Field("parent_relationship"), css_class="col-md-6"),
                            Column(Field("parent_pickup_pin"), css_class="col-md-6"),
                        ),
                        css_class="col-md-7",
                    ),
                    Column(
                        Div(
                            Field("parent_is_primary_contact"),
                            css_class="form-check form-switch d-flex align-items-center gap-2 mb-2 safari-switch-row",
                        ),
                        Div(
                            Field("parent_has_custody_rights"),
                            css_class="form-check form-switch d-flex align-items-center gap-2 mb-2 safari-switch-row",
                        ),
                        Div(
                            Field("parent_can_pickup"),
                            css_class="form-check form-switch d-flex align-items-,center gap-2 mb-2 safari-switch-row",
                        ),
                        css_class="col-md-5 parent-switches",
                    ),
                ),
                HTML("<hr class='border border-primary border-3 opacity-100'>"),
                Fieldset(
                    "Health and Safety",
                    Div(
                        Field("has_allergy"),
                        css_class="form-check form-switch safari-switch-row mb-3",
                    ),
                    Row(
                        Column(Field("allergy_allergen"), css_class="col-md-4"),
                        Column(Field("allergy_severity"), css_class="col-md-4"),
                        Column(Field("allergy_instructions"), css_class="col-md-4"),
                    ),
                    css_id="allergy-fields-container",
                ),
                Field("has_custody_restriction"),
                HTML("<hr class='border border-primary border-3 opacity-100'>"),
                Fieldset(
                    "Enrollment",
                    Field("program"),
                    Div(
                        Field("enrollment_start_date", css_class="col-md-6"),
                        Field("enrollment_end_date", css_class="col-md-6"),
                    ),
                    Field("enrollment_status"),
                ),
                HTML("<hr class='border border-primary border-3 opacity-100'>"),
                Fieldset(
                    "Schedule",
                    Row(
                        Column(
                            Field("instructor"),
                            css_class="col-md-3",
                        ),
                        Column(Field("schedule_start_time"), css_class="col-md-4"),
                        Column(Field("schedule_end_time"), css_class="col-md-4"),
                    ),
                    HTML(
                        '<label class="form-label fw-semibold d-block mt-2 mb-2">'
                        "Days of the Week</label>"
                    ),
                    Div(
                        Div(Field("schedule_sunday"), css_class="day-toggle"),
                        Div(Field("schedule_monday"), css_class="day-toggle"),
                        Div(Field("schedule_tuesday"), css_class="day-toggle"),
                        Div(Field("schedule_wednesday"), css_class="day-toggle"),
                        Div(Field("schedule_thursday"), css_class="day-toggle"),
                        Div(Field("schedule_friday"), css_class="day-toggle"),
                        Div(Field("schedule_saturday"), css_class="day-toggle"),
                        css_class="day-toggle-group",
                    ),
                ),
                HTML("<hr class='border border-primary border-3 opacity-100'>"),
                Fieldset(
                    "Emergency Contact",
                    Row(
                        Column(
                            Field("create_emergency_contact"),
                            css_class="form-check form-switch safari-switch-row",
                        ),
                        css_class="col-md",
                    ),
                ),
                Row(
                    Column(Field("emergency_first_name"), css_class="col-md-3"),
                    Column(Field("emergency_last_name"), css_class="col-md-3"),
                    Column(Field("emergency_contact_number"), css_class="col-md-3"),
                    Column(Field("emergency_relationship"), css_class="col-md-3"),
                ),
                Row(
                    Field("emergency_is_authorized"),
                    css_class="form-check form-switch safari-switch-row",
                ),
                Field("emergency_verification_notes"),
            ),
        )

    def clean_parent_email(self):
        email = self.cleaned_data["parent_email"].strip().lower()
        User = get_user_model()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("has_allergy"):
            required_allergy_fields = {
                "allergy_allergen": "Allergen is required when adding an allergy.",
                "allergy_severity": "Severity is required when adding an allergy.",
                "allergy_instructions": "Instructions are required when adding an allergy.",
            }
            self._require_optional_group_fields(cleaned_data, required_allergy_fields)

        if cleaned_data.get("has_medical_note") and not cleaned_data.get(
            "medical_note"
        ):
            self.add_error(
                "medical_note",
                "Medical note is required when adding a medical note.",
            )

        if cleaned_data.get("has_custody_restriction") and not cleaned_data.get(
            "custody_restriction_notes"
        ):
            self.add_error(
                "custody_restriction_notes",
                "Restriction notes are required when adding a custody restriction.",
            )

        if cleaned_data.get("create_emergency_contact"):
            required_emergency_fields = {
                "emergency_first_name": "Emergency contact first name is required.",
                "emergency_last_name": "Emergency contact last name is required.",
                "emergency_contact_number": "Emergency contact number is required.",
                "emergency_relationship": "Emergency contact relationship is required.",
            }
            self._require_optional_group_fields(cleaned_data, required_emergency_fields)

        start_date = cleaned_data.get("enrollment_start_date")
        end_date = cleaned_data.get("enrollment_end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error(
                "enrollment_end_date",
                "Enrollment end date cannot be before the start date.",
            )

        start_time = cleaned_data.get("schedule_start_time")
        end_time = cleaned_data.get("schedule_end_time")
        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "schedule_end_time",
                "Schedule end time must be after the start time.",
            )

        return cleaned_data

    def save(self, commit=True):
        """
        Creates all records for the enrollment intake workflow.

        Returns a dictionary containing the created model instances so the view
        can redirect, message, or log without spelunking through the database
        like a raccoon in a filing cabinet.
        """
        if not self.is_valid():
            raise ValueError("Cannot save an invalid EnrollmentIntakeForm.")

        if not commit:
            raise ValueError("EnrollmentIntakeForm does not support commit=False.")

        data = self.cleaned_data
        User = get_user_model()

        with transaction.atomic():
            parent_user = User.objects.create_user(
                username=data["parent_email"],
                email=data["parent_email"],
                first_name=data["parent_first_name"],
                last_name=data["parent_last_name"],
            )

            guardian_role, _ = Role.objects.get_or_create(
                name=ROLES.GUARDIAN,
                defaults={"description": "Guardian"},
            )

            child = Child.objects.create(
                first_name=data["child_first_name"],
                last_name=data["child_last_name"],
                date_of_birth=data["child_date_of_birth"],
                status=data["child_status"],
            )

            role_assignment = RoleAssignment.objects.create(
                user=parent_user,
                role=guardian_role,
                child=child,
            )

            guardian_profile = GuardianProfile.objects.create(
                user=parent_user,
                contact_number=data["parent_contact_number"],
                is_primary_contact=data["parent_is_primary_contact"],
            )

            child_guardian_relationship = ChildGuardianRelationship.objects.create(
                child=child,
                guardian=guardian_profile,
                relationship=data["parent_relationship"],
                is_primary=data["parent_is_primary_contact"],
                has_custody_rights=data["parent_has_custody_rights"],
                can_pickup=data["parent_can_pickup"],
            )

            authorized_pickup_profile = AuthorizedPickupProfile.objects.create(
                child=child,
                user=parent_user,
                relationship=data["parent_relationship"],
                is_authorized=data["parent_can_pickup"],
                pickup_pin=data["parent_pickup_pin"],
                verification_notes=data["parent_verification_notes"],
            )

            allergy = None
            if data.get("has_allergy"):
                allergy = Allergy.objects.create(
                    child=child,
                    allergen=data["allergy_allergen"],
                    severity=data["allergy_severity"],
                    instructions=data["allergy_instructions"],
                )

            medical_note = None
            if data.get("has_medical_note"):
                medical_note = MedicalNote.objects.create(
                    child=child,
                    note=data["medical_note"],
                )

            custody_restriction = None
            if data.get("has_custody_restriction"):
                custody_restriction = CustodyRestriction.objects.create(
                    child=child,
                    notes=data["custody_restriction_notes"],
                )

            enrollment = Enrollment.objects.create(
                child=child,
                program=data["program"],
                start_date=data["enrollment_start_date"],
                end_date=data["enrollment_end_date"],
                status=data["enrollment_status"],
            )

            child_schedule = ChildSchedule.objects.create(
                child=child,
                program=data["program"],
                enrollment=enrollment,
                instructor=data["instructor"],
                days_of_week=self._build_days_of_week(),
                start_time=data["schedule_start_time"],
                end_time=data["schedule_end_time"],
            )

            emergency_contact = None
            if data.get("create_emergency_contact"):
                emergency_contact = EmergencyContact.objects.create(
                    child=child,
                    first_name=data["emergency_first_name"],
                    last_name=data["emergency_last_name"],
                    contact_number=data["emergency_contact_number"],
                    relationship=data["emergency_relationship"],
                    is_authorized=data["emergency_is_authorized"],
                    verification_notes=data["emergency_verification_notes"],
                )

        return {
            "parent_user": parent_user,
            "guardian_role": guardian_role,
            "role_assignment": role_assignment,
            "guardian_profile": guardian_profile,
            "child_guardian_relationship": child_guardian_relationship,
            "authorized_pickup_profile": authorized_pickup_profile,
            "child": child,
            "allergy": allergy,
            "medical_note": medical_note,
            "custody_restriction": custody_restriction,
            "enrollment": enrollment,
            "child_schedule": child_schedule,
            "emergency_contact": emergency_contact,
        }

    def _build_days_of_week(self):
        return {
            "sunday": self.cleaned_data["schedule_sunday"],
            "monday": self.cleaned_data["schedule_monday"],
            "tuesday": self.cleaned_data["schedule_tuesday"],
            "wednesday": self.cleaned_data["schedule_wednesday"],
            "thursday": self.cleaned_data["schedule_thursday"],
            "friday": self.cleaned_data["schedule_friday"],
            "saturday": self.cleaned_data["schedule_saturday"],
        }

    def _require_optional_group_fields(self, cleaned_data, required_fields):
        for field_name, error_message in required_fields.items():
            if not cleaned_data.get(field_name):
                self.add_error(field_name, error_message)
