from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect


class SystemBaseView(View):
    base_context = {
        "content": "Welcome to TOKTIK!",
        "contributor": "TOKTIK Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "logo": "myapp/images/Logo.png",
    }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        return render(request, self.template_name, self.context)


class SignInClassView(SystemBaseView):
    template_name = "myapp/system/signin.html"
    context = {
        "title": "Sign In",
        **SystemBaseView.base_context,
    }

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("myapp:dashboard")
        else:
            return super().get(request)

    def post(self, request):
        username_signin = request.POST.get("username")
        password_signin = request.POST.get("password")
        user = authenticate(request, username=username_signin, password=password_signin)
        if user is not None:
            login(request, user)
            return redirect("myapp:dashboard")
        else:
            self.context["error"] = "Username or Password is incorrect!"
            return super().post(request)


class SignUpClassView(SystemBaseView):
    template_name = "myapp/system/signup.html"
    context = {
        "title": "Sign Up",
        **SystemBaseView.base_context,
    }


class SignOutClassView(SystemBaseView):
    template_name = "myapp/system/signout.html"
    context = {
        "title": "Sign Out",
        **SystemBaseView.base_context,
    }

    def get(self, request):
        if request.user.is_authenticated:
            return super().get(request)
        else:
            return redirect("myapp:signin")

    def post(self, request):
        if request.POST.get("signout") == "signout":
            logout(request)
            self.context["message"] = "Sign Out Successfully!"
            return redirect("myapp:signin")
        else:
            self.context["error"] = "Sign Out Failed!"
            return redirect("myapp:dashboard")
