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


class IndexClassView(View):
    template_name = "myapp/index.html"
    context = {
        "title": "Home",
        "contributor": "VisionSlice Team",
        "content": "Welcome to VisionSlice!",
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
        # Get categories color name
        colors = queryset.values_list("color", flat=True).distinct()

        # Mengambil data Image yang memiliki ImagePreprocessing dan minimal satu Segmentation
        images_segmented = Image.objects.filter(
            imagepreprocessing__isnull=False,
            imagepreprocessing__segmentations__isnull=False,
        ).distinct()

        # Menginisialisasi dictionary untuk menyimpan jumlah data berdasarkan pengguna
        data_count = {}

        # Menghitung jumlah data Image yang telah di-segmentasi berdasarkan pengguna
        for image in images_segmented:
            uploader = image.uploader.first_name + " " + image.uploader.last_name
            if uploader in data_count:
                data_count[uploader] += 1
            else:
                data_count[uploader] = 1

        # Menyusun label dan data
        labels_user = []
        data_user = []

        for uploader, count in data_count.items():
            labels_user.append(uploader)
            data_user.append(count)

        # Hitung label
        num_labels_user = len(labels_user)

        # Mengambil data Image yang belum memiliki segmentasi
        images_not_segmented = Image.objects.filter(
            imagepreprocessing__isnull=False,
            imagepreprocessing__segmentations__isnull=True,
        )

        # Menghitung jumlah data Image yang belum di-segmentasi
        num_images_not_segmented_user = images_not_segmented.count()

        # Menghitung jumlah data Image yang telah di-segmentasi berdasarkan pengguna
        for image in images_segmented:
            uploader = image.uploader.first_name + " " + image.uploader.last_name
            if uploader in data_count:
                data_count[uploader] += 1
            else:
                data_count[uploader] = 1

        # Menghitung jumlah data Image yang belum di-segmentasi
        num_images_not_segmented_user = images_not_segmented.count()

        # Mengambil data Image yang memiliki ImagePreprocessing
        images_with_preprocessing = Image.objects.filter(
            imagepreprocessing__isnull=False
        )

        # Menghitung distribusi warna gambar yang diunggah oleh pengguna
        color_distribution = {}

        for image in images_with_preprocessing:
            color = image.color
            if color in color_distribution:
                color_distribution[color] += 1
            else:
                color_distribution[color] = 1

        # Menyusun label dan data
        labels_color = list(color_distribution.keys())
        data_color = list(color_distribution.values())

        # bagi data_color dengan jumlah step preprocessing (54)
        data_color = [data / 54 for data in data_color]

        # ubah data dari dark-mud-brown menjadi Dark Mud Brown
        labels_color = [label.replace("-", " ").title() for label in labels_color]

        # Mengambil data Segmentation
        segmentations = Segmentation.objects.all()

        # Menghitung jumlah segmentasi untuk setiap jenis segmentasi
        segmentation_count = {}

        for segmentation in segmentations:
            segmentation_type = segmentation.segmentation_type
            if segmentation_type in segmentation_count:
                segmentation_count[segmentation_type] += 1
            else:
                segmentation_count[segmentation_type] = 1

        # Menyusun label dan data
        labels_segmentation_result = list(segmentation_count.keys())
        data_segmentation_result = list(segmentation_count.values())

        # bagi data_segmentation_result dengan jumlah step preprocessing (54)
        data_segmentation_result = [data / 54 for data in data_segmentation_result]

        # ubah data dari sobel menjadi Sobel
        labels_segmentation_result = [
            label.replace("-", " ").title() for label in labels_segmentation_result
        ]

        chartjs_data = {
            "labels_user": json.dumps(list(labels_user)),
            "data_user": json.dumps(list(data_user)),
            "num_labels_user": num_labels_user,
            "num_images_not_segmented_user": num_images_not_segmented_user,
            "labels_segmentation": json.dumps(["Segmented", "Not Segmented"]),
            "data_segmentation": json.dumps(
                [num_labels_user, num_images_not_segmented_user]
            ),
            "num_labels_segmentation": num_labels_user,
            "labels_color": json.dumps(labels_color),
            "data_color": json.dumps(data_color),
            "num_labels_color": len(labels_color),
            "labels_segmentation_result": json.dumps(labels_segmentation_result),
            "data_segmentation_result": json.dumps(data_segmentation_result),
            "num_labels_segmentation_result": len(labels_segmentation_result),
        }

        # #print("labels_segmentation_result", labels_segmentation_result)
        # #print("data_segmentation_result", data_segmentation_result)

        self.extra_context = {
            "uploaders": uploaders,
            "colors": colors,
            "title": "Dashboard",
            "contributor": "VisionSlice Team",
            "content": "Dashboard, a place to see the overview of the data in VisionSlice. You can see the number of data uploaded by each user, the number of segmented and unsegmented data, the color distribution of the images, and the number of segmentations for each segmentation type.",
            "app_css": "myapp/css/styles.css",
            "app_js": "myapp/js/scripts.js",
            "logo": "myapp/images/Logo.png",
            "chartjs": chartjs_data,
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
        "contributor": "VisionSlice Team",
        "content": "Welcome to VisionSlice!",
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
        "contributor": "VisionSlice Team",
        "content": "Welcome to VisionSlice!",
        "app_css": "myapp/css/styles.css",
        "app_js": "myapp/js/scripts.js",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "posts": [
            {
                "title": "Blog Post 1",
                "url": "/blog/post1/",
                "content": "Welcome to VisionSlice!",
                "author": "VisionSlice Team",
                "date_posted": "August 27, 2018",
            },
            {
                "title": "Blog Post 2",
                "url": "/blog/post2/",
                "content": "Welcome to VisionSlice!",
                "author": "VisionSlice Team",
                "date_posted": "August 28, 2018",
            },
            {
                "title": "Blog Post 3",
                "url": "/blog/post3/",
                "content": "Welcome to VisionSlice!",
                "author": "VisionSlice Team",
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
        "content": "Welcome to VisionSlice!",
        "contributor": "VisionSlice Team",
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
        "content": "Welcome to VisionSlice!",
        "contributor": "VisionSlice Team",
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
        "contributor": "VisionSlice Team",
        "content": "Welcome to VisionSlice!",
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
        "content": "Welcome to VisionSlice!",
        "contributor": "VisionSlice Team",
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
        "content": "Welcome to VisionSlice!",
        "contributor": "VisionSlice Team",
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
        "contributor": "VisionSlice Team",
        "content": "Welcome to VisionSlice!",
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
