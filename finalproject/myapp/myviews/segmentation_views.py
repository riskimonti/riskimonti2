import json
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from myapp.utils.segmentation import (
    perform_k_means_segmentation,
    get_top_segmentations,
    calculate_scores,
    perform_adaptive_segmentation,
    perform_otsu_segmentation,
    perform_sobel_segmentation,
    perform_canny_segmentation,
    perform_prewitt_segmentation,
    get_segmentation_results_data,
)
import io
from django.core.files.base import ContentFile
from myapp.menus import menus, set_user_menus
from myapp.models import (
    Image,
    ImagePreprocessing,
    Segmentation,
    SegmentationResult,
    UserProfile,
)
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
import uuid
from django.contrib.auth.models import User
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Count, Q, F
import cv2
import numpy as np
from PIL import Image as PILImage
import os
from datetime import datetime


class SegmentationClassView(ListView):
    template_name = "myapp/segmentation/segmentation.html"
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
            set_user_menus(request, context)
            self.customize_context(context)  # Call the customize_context method
            return render(request, self.template_name, context)

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("segmentation_results")
        search_query = self.request.GET.get("search")

        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi yang diinginkan.
            queryset = queryset.filter(
                Q(image__icontains=search_query)
                | Q(uploader__username__icontains=search_query)
                | Q(color__icontains=search_query)
                | Q(width__icontains=search_query)
                | Q(height__icontains=search_query)
                | Q(distance__icontains=search_query)
                | Q(format__icontains=search_query)
                | Q(size__icontains=search_query)
                | Q(channel__icontains=search_query)
            )

        # Get categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # Count Image by uploader
        uploaders_count = Image.objects.filter(uploader__isnull=False)
        # print(uploaders_count)
        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        # print(uploaders)
        # Get categories color name
        colors = queryset.values_list("color", flat=True).distinct()

        self.extra_context = {
            "uploaders": uploaders,
            "colors": colors,
            "title": "Segmentation",
            "contributor": "VisionSlice Team",
            "content": "Welcome to VisionSlice! This is a website for image segmentation.",
            "app_css": "myapp/css/styles.css",
            "app_js": "myapp/js/scripts.js",
            "logo": "myapp/images/Logo.png",
        }

        # Iterate over the queryset and set the "segmented" column based on the segmentation types
        counter = 0
        for image in queryset:
            segmentation_types = [
                "kmeans",
                "adaptive",
                "otsu",
                "sobel",
                "prewitt",
                "canny",
            ]
            segmentation_count = image.segmentation_results.filter(
                segmentation_type__in=segmentation_types
            ).count()
            segmented = segmentation_count == 90
            image.segmented = segmented
            image.segmented_count = (
                segmentation_count  # Add the "segmented_count" variable
            )
            color = image.color
            # replace dash with space
            color = color.replace("-", " ")
            image.color = color
            counter += 1

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass


def perform_segmentation(segmentation_type, segmentation_results_data, image):
    segmentations = {
        "kmeans": {
            "perform": perform_k_means_segmentation,
            "top": get_top_segmentations,
        },
        "adaptive": {
            "perform": perform_adaptive_segmentation,
            "top": get_top_segmentations,
        },
        "otsu": {
            "perform": perform_otsu_segmentation,
            "top": get_top_segmentations,
        },
        "sobel": {
            "perform": perform_sobel_segmentation,
            "top": get_top_segmentations,
        },
        "prewitt": {
            "perform": perform_prewitt_segmentation,
            "top": get_top_segmentations,
        },
        "canny": {
            "perform": perform_canny_segmentation,
            "top": get_top_segmentations,
        },
    }

    if (
        segmentation_type in segmentations
        and not segmentation_results_data[segmentation_type]["available"]
    ):
        # print(f"Performing {segmentation_type} segmentation...")
        perform_func = segmentations[segmentation_type]["perform"]
        perform_func(image)
        top_func = segmentations[segmentation_type]["top"]
        if top_func:
            top_func(image, segmentation_type)


class SegmentationDetailClassView(DetailView):
    model = Image
    template_name = "myapp/segmentation/segmentation_detail.html"
    context_object_name = "segmentation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        self.customize_context(context)

        context["title"] = "Segmentation Detail"
        context["contributor"] = "VisionSlice Team"
        context[
            "content"
        ] = "Welcome to VisionSlice! This is a website for image segmentation."
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"

        image = self.get_object()
        segmentation_results_data = get_segmentation_results_data(image)
        context["segmentation_results_data"] = segmentation_results_data
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        image = self.get_object()
        selected_segmentation_types = request.POST.getlist("segmentation_types")
        segmentation_results_data = get_segmentation_results_data(image)
        # print("selected_segmentation_types:", selected_segmentation_types)

        for segmentation_type in selected_segmentation_types:
            if SegmentationResult.objects.filter(
                image=image, segmentation_type=segmentation_type
            ).exists():
                # print(f"Segmentation {segmentation_type} already exists.")
                continue

            perform_segmentation(segmentation_type, segmentation_results_data, image)

        return redirect("myapp:segmentation_detail", pk=image.pk)

    def customize_context(self, context):
        pass


class SegmentationDeleteClassView(DeleteView):
    model = Image
    template_name = "myapp/segmentation/segmentation_delete.html"
    context_object_name = "segmentation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        set_user_menus(self.request, context)
        self.customize_context(context)

        context["title"] = "Segmentation Delete"
        context["contributor"] = "VisionSlice Team"
        context[
            "content"
        ] = "Welcome to VisionSlice! This is a website for image segmentation."
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"

        image = self.get_object()
        segmentation_results_data = get_segmentation_results_data(image)
        context["segmentation_results_data"] = segmentation_results_data
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        else:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        image = self.get_object()
        segmentation_results_data = get_segmentation_results_data(image)
        segmentation_types = segmentation_results_data.keys()
        for segmentation_type in segmentation_types:
            ipre = ImagePreprocessing.objects.filter(
                image=image, segmentations__segmentation_type=segmentation_type
            )
            if ipre.exists():
                # delete ImagePreprocessing records related to the Image
                for ip in ipre:
                    # print("image_preprocessing", image_preprocessing)
                    # delete Segmentation records related to the ImagePreprocessing
                    seg = Segmentation.objects.filter(
                        image_preprocessing=ip, segmentation_type=segmentation_type
                    )
                    if seg.exists():
                        for s in seg:
                            seg_res = SegmentationResult.objects.filter(
                                segment=s,
                            )
                            for sr in seg_res:
                                sr.delete()
                            img_seg_url = s.image_segmented.url
                            if os.path.exists(img_seg_url):
                                os.remove(img_seg_url)
                            s.delete()
                count = ipre.count()
                print(f"Deleting {segmentation_type} segmentation...")
                print(f"Deleting {count} ImagePreprocessing objects...")

        return redirect("myapp:segmentation_detail", pk=image.pk)

    def customize_context(self, context):
        pass


class SegmentationSummaryClassView(ListView):
    template_name = "myapp/segmentation/segmentation_summary.html"
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
            set_user_menus(request, context)
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

        self.extra_context = {
            "uploaders": uploaders,
            "colors": colors,
            "title": "Segmentation Summary",
            "contributor": "VisionSlice Team",
            "content": "Welcome to VisionSlice! This is a website for image segmentation.",
            "app_css": "myapp/css/styles.css",
            "app_js": "myapp/js/scripts.js",
            "logo": "myapp/images/Logo.png",
            "chartjs": chartjs_data,
        }

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

    def customize_context(self, context):
        # Override this method in derived views to customize the context
        pass
