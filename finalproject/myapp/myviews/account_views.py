from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

# models UserProfile
from myapp.models import UserProfile

# models User
from django.contrib.auth.models import User
from myapp.forms import UserForm, UserChangePasswordForm
from django.urls import reverse_lazy
from django.contrib.auth import password_validation
from django.contrib.auth import update_session_auth_hash, login


class BaseAccountView(View):
    template_name = "myapp/account/base.html"
    context = {
        "title": "Account",
        "content": "Welcome to TOKTIK! Account",
        "contributor": "TOKTIK Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }

    def get_object(self):
        username = self.kwargs.get("username")
        user = User.objects.get(username=username)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.context)
        set_user_menus(self.request, context)
        user = self.get_object()
        context["account"] = user
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)


class AccountUpdateClassView(BaseAccountView, UpdateView):
    model = User
    template_name = "myapp/account/account_update.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse_lazy(
            "myapp:account", kwargs={"username": self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Account Update"
        return context

    def form_invalid(self, form):
        # print("form_invalid", form.cleaned_data)
        # print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # print("form_valid", form.cleaned_data)
        data = form.cleaned_data
        user = self.get_object()

        # Update user
        username = data.get("username")
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            form.add_error("username", "Username already exists")
            return super().form_invalid(form)

        first_name = data.get("first_name")
        if not first_name:
            first_name = user.first_name
        last_name = data.get("last_name")
        if not last_name:
            last_name = user.last_name
        email = data.get("email")
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            form.add_error("email", "Email already exists")
            return self.form_invalid(form)

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


class AccountClassView(BaseAccountView, DetailView):
    model = User
    template_name = "myapp/account/account.html"
    context_object_name = "account"
    success_url = reverse_lazy("myapp:account")
    failure_url = "/account/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Account"
        return context


class AccountProfileClassView(BaseAccountView):
    template_name = "myapp/account/profile.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            context = self.context
            context["title"] = "Account Profile"
            set_user_menus(request, context)
            return render(request, self.template_name, context)


class AccountChangePasswordClassView(BaseAccountView, UpdateView):
    template_name = "myapp/account/account_change_password.html"
    form_class = UserChangePasswordForm

    def get_success_url(self):
        username = self.kwargs["username"]
        return reverse_lazy(
            "myapp:account_change_password", kwargs={"username": username}
        )

    def get(self, request, username):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            context = self.context
            context["title"] = "Account Change Password"
            set_user_menus(request, context)
            return render(request, self.template_name, context)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.POST, initial=self.get_initial())

    def form_invalid(self, form):
        # print("form_invalid", form.cleaned_data)
        # print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        # print("form_valid", form.cleaned_data)
        #  check old password
        old_password = form.cleaned_data.get("old_password")
        user = self.get_object()
        if not user.check_password(old_password):
            form.add_error("old_password", "Old password is incorrect")
            return super().form_invalid(form)
        # check new password and confirm password
        new_password = form.cleaned_data.get("new_password")
        confirm_password = form.cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            form.add_error("confirm_password", "Confirm password is incorrect")
            return super().form_invalid(form)

        # Validate the new password
        try:
            password_validation.validate_password(new_password, user=user)
        except ValidationError as error:
            form.add_error("new_password", error)
            return super().form_invalid(form)

        # If all validations pass, proceed with saving the new password
        user.set_password(new_password)
        user.save()
        # Reset session with the new password
        update_session_auth_hash(self.request, user)

        # Re-authenticate the user if they have changed their own password
        if user == self.request.user:
            login(self.request, user)

        return redirect(self.get_success_url())
