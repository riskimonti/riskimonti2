from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q


base_context = {
    "content": "Welcome to TOKTIK!",
    "contributor": "TOKTIK Team",
    "app_css": "myapp/css/styles.css",
    "app_js": "myapp/js/scripts.js",
    "menus": menus,
    "logo": "myapp/images/Logo.png",
}


class ManageClassView(View):
    template_name = "myapp/manage/manage.html"
    context = {
        "title": "Manage",
        **base_context,
    }

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)

    def post(self, request):
        return render(request, self.template_name, self.context)


class ManageUsersClassView(ListView):
    template_name = "myapp/manage/manage_users.html"
    context_object_name = "users"
    paginate_by = 10
    extra_context = {
        "title": "Manage Users",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "content": "Welcome to TOKTIK!",
        "contributor": "TOKTIK Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
    }

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.extra_context)
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = User.objects.all()

        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi yang diinginkan.
            queryset = queryset.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )
            # change the page_obj add the search_query
            self.extra_context["search"] = search_query

        return queryset
