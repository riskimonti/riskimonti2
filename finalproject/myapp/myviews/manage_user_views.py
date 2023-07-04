import os
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
    FormView,
)
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator

from myapp.forms import UserForm, UserChangePasswordForm, ManageUserGroupEditForm
from django.contrib.auth import get_user_model
from myapp.models import (
    UserProfile,
    Image,
    ImagePreprocessing,
    Segmentation,
    SegmentationResult,
)

base_context = {
    "content": "Welcome to TOKTIK!",
    "contributor": "TOKTIK Team",
    "app_css": "myapp/css/styles.css",
    "app_js": "myapp/js/scripts.js",
    "menus": menus,
    "logo": "myapp/images/Logo.png",
}


class ManageUserAddClassView(CreateView):
    model = User
    template_name = "myapp/manage/manage_user_add.html"
    form_class = UserForm
    context_object_name = "data_user"
    extra_context = {
        "title": "Add User",
        **base_context,
    }

    def get_success_url(self):
        return reverse_lazy("myapp:manage_user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        # print("form_invalid", form.cleaned_data)
        # print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        # print("form_valid", form.cleaned_data)
        data = form.cleaned_data

        # Create user
        username = data.get("username")
        if User.objects.filter(username=username).exists():
            form.add_error("username", "Username already exists")
            return self.form_invalid(form)

        email = data.get("email")
        if User.objects.filter(email=email).exists():
            form.add_error("email", "Email already exists")
            return self.form_invalid(form)

        first_name = data.get("first_name")
        if not first_name:
            form.add_error("first_name", "First name is required")
            return self.form_invalid(form)
        last_name = data.get("last_name")
        if not last_name:
            form.add_error("last_name", "Last name is required")
            return self.form_invalid(form)

        user = form.save(commit=False)
        user.set_password("inipasswordmu")  # Auto-generated password
        user.save()

        # Create user profile
        user_profile = UserProfile()
        user_profile.user = user

        # Update user profile
        bio = data.get("bio")
        phone_number = data.get("phone_number")
        address = data.get("address")
        date_of_birth = data.get("date_of_birth")

        # Update profile picture
        if "profile_pic" in self.request.FILES:
            profile_pic = self.request.FILES["profile_pic"]
            user_profile.profile_pic = profile_pic

        user_profile.bio = bio
        user_profile.phone_number = phone_number
        user_profile.address = address
        user_profile.date_of_birth = date_of_birth
        user_profile.save()

        return redirect(self.get_success_url())


class ManageUserDeleteClassView(DeleteView):
    model = User
    template_name = "myapp/manage/manage_user_delete.html"
    context_object_name = "data_user"
    extra_context = {
        "title": "Delete User",
        **base_context,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        # user_profile = UserProfile.objects.get(user=user) none
        if hasattr(user, "userprofile"):
            user_profile = user.userprofile
        else:
            user_profile = None
        context["user_profile"] = user_profile
        set_user_menus(self.request, context)
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            # User cannot delete their own account
            return redirect("myapp:manage_user")

        # Delete associated UserProfile and related images
        user_profile = user.userprofile
        if user_profile:
            profile_pic = user_profile.profile_pic
            if profile_pic:
                # Delete profile picture file
                profile_pic_path = profile_pic.path
                if os.path.exists(profile_pic_path):
                    os.remove(profile_pic_path)

            user_profile.delete()

        # Delete associated Image, ImagePreprocessing, and SegmentationResult
        images = Image.objects.filter(uploader=user)
        for image in images:
            image.delete()

        image_preprocessings = ImagePreprocessing.objects.filter(image__uploader=user)
        for image_preprocessing in image_preprocessings:
            image_preprocessing.delete()

        segmentation_results = SegmentationResult.objects.filter(image__uploader=user)
        for segmentation_result in segmentation_results:
            segmentation_result.delete()

        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("myapp:manage_user")


class ManageUserGroupEditClassView(UpdateView):
    model = User
    template_name = "myapp/manage/manage_user_group_edit.html"
    context_object_name = "data_user"
    form_class = ManageUserGroupEditForm
    extra_context = {
        "title": "User Group Edit",
        **base_context,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        # user_profile = UserProfile.objects.get(user=user) none
        if hasattr(user, "userprofile"):
            user_profile = user.userprofile
        else:
            user_profile = None
        context["user_profile"] = user_profile

        # Get all groups
        groups = Group.objects.all()
        context["data_groups"] = groups
        set_user_menus(self.request, context)
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()  # Mendapatkan instance dari form
        if form.is_valid():  # Memvalidasi form
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Lakukan tindakan yang diinginkan ketika form valid
        # print(form.cleaned_data)
        user = self.get_object()
        groups = form.cleaned_data["groups"]
        if user.groups.all().count() > 0:
            user.groups.clear()
        for group in groups:
            user.groups.add(group)
        # is_staff and is_superuser and is_active
        # is_staff = form.cleaned_data["is_staff"]
        # is_superuser = form.cleaned_data["is_superuser"]
        # is_active = form.cleaned_data["is_active"]
        # user.is_staff = is_staff
        # user.is_superuser = is_superuser
        # user.is_active = is_active
        user.save()

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Lakukan tindakan yang diinginkan ketika form tidak valid
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("myapp:manage_user")


class ManageUserDetailClassView(DetailView):
    model = User
    template_name = "myapp/manage/manage_user_detail.html"
    context_object_name = "data_user"
    extra_context = {
        "title": "User Details",
        **base_context,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        # user_profile does not exist
        if hasattr(user, "userprofile"):
            user_profile = UserProfile.objects.get(user=user)
        else:
            user_profile = None
        context["user_profile"] = user_profile
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.extra_context)
            return super().get(request, *args, **kwargs)


class ManageUserEditClassView(UpdateView):
    model = User
    template_name = "myapp/manage/manage_user_edit.html"
    context_object_name = "data_user"
    form_class = UserForm
    extra_context = {
        "title": "Edit User",
        **base_context,
    }

    def get_success_url(self):
        return reverse_lazy("myapp:manage_user_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        # user_profile does not exist
        if hasattr(user, "userprofile"):
            user_profile = UserProfile.objects.get(user=user)
        else:
            user_profile = None
        context["user_profile"] = user_profile
        set_user_menus(self.request, context)
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        # print("form_invalid", form.cleaned_data)
        # print(form.errors)
        # return invalid form and got get and print form.errors
        return super().form_invalid(form)

    def form_valid(self, form):
        # print("form_valid", form.cleaned_data)
        data = form.cleaned_data
        user = self.get_object()

        # Update user
        username = data.get("username")
        if User.objects.filter(username=username).exists():
            if username != user.username:
                form.add_error("username", "Username already exists")
                return self.form_invalid(form)

        first_name = data.get("first_name")
        if not first_name:
            form.add_error("first_name", "First name is required")
            return self.form_invalid(form)
        last_name = data.get("last_name")
        if not last_name:
            form.add_error("last_name", "Last name is required")
            return self.form_invalid(form)
        email = data.get("email")
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Update password if changed
        new_password = data.get("password")
        if new_password and user.check_password(new_password):
            user.set_password(new_password)

        # Save user and print console
        user.save()
        # print(user)

        # Get user profile if exist or create new user profile by user
        if hasattr(user, "userprofile"):
            user_profile = user.userprofile
        else:
            user_profile = UserProfile()
            user_profile.user = user

        # Update user profile
        bio = data.get("bio")
        phone_number = data.get("phone_number")
        address = data.get("address")
        date_of_birth = data.get("date_of_birth")

        # Update profile picture
        if "profile_pic" in self.request.FILES:
            # delete old profile picture
            if user_profile.profile_pic:
                user_profile.profile_pic.delete(save=True)
            profile_pic = self.request.FILES["profile_pic"]
            user_profile.profile_pic = profile_pic
        user_profile.bio = bio
        user_profile.phone_number = phone_number
        user_profile.address = address
        user_profile.date_of_birth = date_of_birth
        user_profile.save()

        return redirect(self.get_success_url())


class ManageUserResetPasswordClassView(UpdateView):
    model = User
    template_name = "myapp/manage/manage_user_reset_password.html"
    form_class = UserForm
    context_object_name = "data_user"
    extra_context = {
        "title": "Reset Password User",
        **base_context,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        user_profile = UserProfile.objects.get(user=user)
        context["user_profile"] = user_profile
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.extra_context)
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # print(form.cleaned_data)
        username = form.cleaned_data["username"]
        user = User.objects.get(username=username)
        id = user.id
        user.set_password("inipasswordmu")
        user.save()
        return redirect(reverse_lazy("myapp:manage_user_detail", kwargs={"pk": id}))

    def form_invalid(self, form):
        # print(form.errors)
        set_user_menus(self.request, self.extra_context)
        return super().get(self.request)
