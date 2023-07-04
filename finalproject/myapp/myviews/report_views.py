from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus

from django.views.generic import DetailView

from myapp.models import Image

from django.shortcuts import get_object_or_404


class ReportBaseView(View):
    base_context = {
        "content": "Welcome to VisionSlice!",
        "contributor": "VisionSlice Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.context = {**self.base_context}  # Add this line
            set_user_menus(request, self.context)
            self.context["title"] = self.title  # Add this line
            return render(
                request, self.template_name, self.context
            )  # Replace `context` with `self.context`


class ReportClassView(ReportBaseView):
    template_name = "myapp/report/report.html"
    context = {
        "title": "Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportSegmentationClassView(DetailView, ReportBaseView):
    template_name = "myapp/report/report_segmentation.html"
    context = {
        "title": "Segmentation Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request, *args, **kwargs):
        self.title = "Segmentation Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportBaseMixin:
    base_context = {
        "content": "Welcome to VisionSlice!",
        "contributor": "VisionSlice Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        context["title"] = self.title
        return context


class ReportExportImageClassView(DetailView, ReportBaseMixin):
    model = Image
    template_name = "myapp/report/report_export_image.html"
    title = "Export Image Report"

    def get_object(self, queryset=None):
        # Retrieve the object based on the requested URL
        pk = self.kwargs.get("pk")
        return get_object_or_404(Image, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        context["title"] = self.title
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            return super().get(request, *args, **kwargs)


class ReportExportReportClassView(ReportBaseView):
    template_name = "myapp/report/report_export_report.html"
    context = {
        "title": "Export Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Export Report"  # Add this line
        return super().get(request)  # Call the parent's get method


class ReportSummaryClassView(ReportBaseView):
    template_name = "myapp/report/report_summary.html"
    context = {
        "title": "Summary Report",
        **ReportBaseView.base_context,
    }

    # override get method
    def get(self, request):
        self.title = "Summary Report"  # Add this line
        return super().get(request)  # Call the parent's get method
