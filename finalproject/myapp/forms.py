from django import forms
from .models import Image
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

# models User
from django.contrib.auth.models import User, Group

# models UserProfile
from myapp.models import UserProfile


class ManageUserGroupEditForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = User
        fields = []


class UserResetPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]

        labels = {
            "username": "Username",
            "email": "Email",
        }


class UserForm(forms.ModelForm):
    bio = forms.CharField(label="Bio", required=False)
    phone_number = forms.CharField(label="Phone Number", required=False)
    address = forms.CharField(label="Address", required=False)
    date_of_birth = forms.DateField(label="Date of Birth", required=False)
    profile_pic = forms.ImageField(label="Profile Picture", required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

        labels = {
            "username": "Username",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
        }


class UserChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(
        label="Old Password", widget=forms.PasswordInput(), required=True
    )
    new_password = forms.CharField(
        label="New Password", widget=forms.PasswordInput(), required=True
    )
    confirm_password = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput(), required=True
    )

    class Meta:
        model = User
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        cleaned_data["password"] = old_password
        return cleaned_data


class VisibleMultipleHiddenInput(forms.widgets.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        attrs["type"] = "hidden"  # Change the input type to 'hidden'
        return mark_safe(super().render(name, value, attrs, renderer))


class ImageForm(forms.ModelForm):
    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise ValidationError(self.error_messages["image"])
        return image

    class Meta:
        model = Image
        fields = [
            "uploader",
            "image",
            "distance",
            "color",
        ]
        labels = {
            "uploader": "Uploader",
            "image": "Image",
            "distance": "Distance",
            "color": "Color",
        }
        widgets = {
            "uploader": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                    "placeholder": "Uploader",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    # tailwindcss
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                    "placeholder": "Image",
                    "id": "id_image",
                    "accept": "image/*",
                }
            ),
            "distance": forms.NumberInput(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                    "placeholder": "Distance",
                    "min": 0,
                    "max": 100,
                    "step": 1,
                }
            ),
            "color": forms.Select(
                attrs={
                    "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                    "placeholder": "Color",
                    "data-live-search": "true",
                    "data-size": "5",
                }
            ),
        }
        allow_empty_file = False
        error_messages = {
            "uploader": {
                "required": "Uploader is required but hidden",
            },
            "image": {
                "required": "Image is required but hidden",
            },
        }
