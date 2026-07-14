from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserCreateForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput, validators=[validate_password]
    )
    role = forms.ChoiceField(choices=[("staff", "Staff"), ("admin", "Admin")])

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self):
        data = self.cleaned_data
        is_staff = data["role"] == "admin"
        # Use email as username since allauth authenticates by email
        user = User.objects.create_user(
            username=data["email"].lower(),
            email=data["email"].lower(),
            password=data["password"],
            first_name=data["name"].split()[0],
            last_name=" ".join(data["name"].split()[1:]),
            is_staff=is_staff,
        )
        return user


class UserEditForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=[("staff", "Staff"), ("admin", "Admin")])

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        qs = User.objects.filter(email=email).exclude(pk=self._user.pk)
        if qs.exists():
            raise forms.ValidationError("That email is already in use.")
        return email

    def save(self):
        data = self.cleaned_data
        user = self._user
        name_parts = data["name"].split()
        user.first_name = name_parts[0]
        user.last_name = " ".join(name_parts[1:])
        user.email = data["email"].lower()
        user.username = data["email"].lower()
        user.is_staff = data["role"] == "admin"
        user.save()
        return user
