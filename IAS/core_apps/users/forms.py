from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model, login
from django.contrib.auth.hashers import make_password
from django.db import transaction

from IAS.core_apps.common.models import ROLE_URL_MAP, RoleType
from IAS.core_apps.institutes.models import Institute
from IAS.core_apps.users.models import Role

AUTH_USER = get_user_model()


class UserChangeForm(admin_forms.UserChangeForm):

    class Meta(admin_forms.UserChangeForm.Meta):
        model = AUTH_USER


class UserCreationForm(admin_forms.UserCreationForm):

    class Meta(admin_forms.UserCreationForm.Meta):
        model = AUTH_USER
        fields = ("first_name", "last_name", "email")


class RegistrationForm(forms.Form):
    institute_name = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'institute_name'
        })
    )
    institute_owner_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'institute_owner_name'
        })
    )
    institute_owner_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'institute_owner_email'
        })
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'Password'}))
    terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'acceptTerms'
        }), required=True
    )

    def save(self):
        owner_email = self.cleaned_data['institute_owner_email']
        check_email = AUTH_USER.objects.email_validator(email=owner_email)

        if not check_email:
            return False, "Email already exists!"

        try:
            with transaction.atomic():
                # Create the Institute
                institute = Institute.objects.create(institute_name=self.cleaned_data['institute_name'])

                # Split the owner name
                first_name, last_name = self.cleaned_data['institute_owner_name'].split(
                    ' ', 1
                ) if " " in self.cleaned_data["institute_owner_name"] else (
                    self.cleaned_data['institute_owner_name'], ""
                )

                # Create the User
                user = AUTH_USER.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=owner_email,
                    password=make_password(self.cleaned_data['password']),
                )

                # Create the Role
                Role.objects.create(user=user, institute=institute, role_type=RoleType.OWNER)

            return True, "Institute and user created successfully"

        except Exception as e:
            return False, f"An error occurred: {e}"


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'Email'}),)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'Password'}))

    def make_user_session(self, request) -> tuple:
        username = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        _message = None
        url_name = "Login"
        if user is not None:
            login(request, user)
            _message = f'Welcome {user.first_name} {user.last_name}!'
            try:
                role = Role.objects.get(user=user)
                url_name = ROLE_URL_MAP[role.role_type]
            except Role.DoesNotExist:
                _message = 'Not allowed to access!'
        else:
            _message = "Invalid Email or Password!"
        return user, url_name, _message
