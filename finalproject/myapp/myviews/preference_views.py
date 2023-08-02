import json
from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import (
    Q,
    Prefetch,
    Count,
    Subquery,
    OuterRef,
    F,
    Avg,
    Max,
    Min,
    Sum,
)


class IndexClassView(View):
    template_name = "myapp/index.html"
    context = {
        "title": "Home",
        "contributor": "REDUNION Team",
        "content": "Welcome to REDUNION!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "logo": "myapp/images/Logo.png",
        "menus": menus,
    }

    def get(self, request):
        # codition request user is authenticated
        if request.user.is_authenticated:
            return redirect("myapp:dashboard")
        else:
            return render(request, self.template_name, self.context)


class DashboardClassView(ListView):
    template_name = "myapp/dashboard.html"
    model = Image
    context_object_name = "segmentation"
    ordering = ["-created_at"]
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object_list = self.get_queryset()
            context = self.get_context_data(**kwargs)
            self.customize_context(context)  # Call the customize_context method
            return render(request, self.template_name, context)

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("segmentation_results")

        # Get categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # Count Image by uploader
        uploaders_count = Image.objects.filter(uploader__isnull=False)
        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        color_query = self.request.GET.get("color")
        segmentation_type_query = self.request.GET.get("type")
        segmentation_types = SegmentationResult.objects.values(
            "segmentation_type"
        ).distinct()

        # Retrieve all ImagePreprocessing objects that have segmentation results
        image_preprocessings = ImagePreprocessing.objects.filter(
            segmentations__segmentation_type__in=segmentation_types
        ).distinct()
        # Get the corresponding Image objects
        images = Image.objects.filter(
            imagepreprocessing__in=image_preprocessings
        ).distinct()
        queryset = SegmentationResult.objects.filter(
            image__in=images,
            segmentation_type__in=segmentation_types,
            rank=1,
        ).order_by("image", "rank")
        ccolor_dict = queryset.values_list("image__color", flat=True).distinct()
        ccolor_dict = list(ccolor_dict)
        # ambil semua nilai unik color dari list color_dict
        ccolor_dict = list(set(ccolor_dict))
        print(ccolor_dict)
        csegmentation_type_dict = queryset.values_list(
            "segmentation_type", flat=True
        ).distinct()
        csegmentation_type_dict = list(csegmentation_type_dict)
        csegmentation_type_dict = list(set(csegmentation_type_dict))
        if color_query and color_query != "all":
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi color
            queryset = queryset.filter(image__color=color_query)

        if segmentation_type_query and segmentation_type_query != "all":
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi segmentation_type
            queryset = queryset.filter(segmentation_type=segmentation_type_query)

        # total image from queryset dibagi dengan segmentation type
        total_image_seg = queryset.count() / len(csegmentation_type_dict)
        # jadikan integer
        total_image_seg = int(total_image_seg)

        # Calculate the average of jaccard_score, rand_score, and f1_score
        average_scores = queryset.aggregate(
            avg_mse=Avg("segment__mse"),
            avg_psnr=Avg("segment__psnr"),
        )
        avg_mse = average_scores["avg_mse"]
        avg_psnr = average_scores["avg_psnr"]

        self.extra_context = {
            "color_dict": ccolor_dict,
            "segmentation_type_dict": csegmentation_type_dict,
            "uploaders": uploaders,
            "title": "Dashboard",
            "contributor": "REDUNION Team",
            "content": "Dashboard, a place to see the overview of the data in REDUNION. You can see the number of data uploaded by each user, the number of segmented and unsegmented data, the color distribution of the images, and the number of segmentations for each segmentation type.",
            "app_css": "myapp/css/styles.css",
            "app_js": "myapp/js/scripts.js",
            "logo": "myapp/images/Logo.png",
            "avg_mse": avg_mse,
            "avg_psnr": avg_psnr,
            "total_image_seg": total_image_seg,
        }

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        set_user_menus(request, context)
        context.update(self.extra_context)
        return context

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass


class AboutClassView(View):
    context = {
        "title": "About",
        "contributor": "REDUNION Team",
        "content": "Welcome to REDUNION!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/about.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class BlogClassView(View):
    context = {
        "title": "Blog",
        "contributor": "REDUNION Team",
        "content": "Welcome to REDUNION!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "posts": [
            {
                "title": "Blog Post 1",
                "url": "/blog/post1/",
                "content": "Welcome to REDUNION!",
                "author": "REDUNION Team",
                "date_posted": "August 27, 2018",
            },
            {
                "title": "Blog Post 2",
                "url": "/blog/post2/",
                "content": "Welcome to REDUNION!",
                "author": "REDUNION Team",
                "date_posted": "August 28, 2018",
            },
            {
                "title": "Blog Post 3",
                "url": "/blog/post3/",
                "content": "Welcome to REDUNION!",
                "author": "REDUNION Team",
                "date_posted": "August 29, 2018",
            },
        ],
    }
    template_name = "myapp/blog.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class ContactClassView(View):
    context = {
        "title": "Contact",
        "content": "Welcome to REDUNION!",
        "contributor": "REDUNION Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/contact.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class DocsClassView(View):
    context = {
        "title": "Docs",
        "content": "Welcome to REDUNION!",
        "contributor": "REDUNION Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/docs.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class HelpClassView(View):
    context = {
        "title": "Help",
        "contributor": "REDUNION Team",
        "content": "Welcome to REDUNION!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/help.html"

    # override method get
    def get(self, request):
        return render(request, self.template_name, self.context)


class PreferenceSettingClassView(View):
    context = {
        "title": "Setting",
        "content": "Welcome to REDUNION!",
        "contributor": "REDUNION Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/preference/preferenceSetting.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class PreferenceClassView(View):
    context = {
        "title": "Preferences",
        "content": "Welcome to REDUNION!",
        "contributor": "REDUNION Team",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/preference/preference.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)


class SettingClassView(View):
    context = {
        "title": "Settings",
        "contributor": "REDUNION Team",
        "content": "Welcome to REDUNION!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
    }
    template_name = "myapp/preference/preference_setting.html"

    # override method get
    def get(self, request):
        # condition request user is not authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            set_user_menus(request, self.context)
            return render(request, self.template_name, self.context)
