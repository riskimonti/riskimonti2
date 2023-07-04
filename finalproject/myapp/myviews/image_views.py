import json
import os
import random
from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)

from django.core.paginator import Paginator

# models import
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.contrib.auth.models import User
from django.db.models import Count, Q


# forms import
from myapp.forms import ImageForm

from django.urls import reverse_lazy

# cv2 import
import cv2

# numpy import
import numpy as np

from myapp.utils.image import (
    apply_spatial_filter,
    process_and_save_image_preprocessing,
    get_user_image_count,
)


class ImageUpdateView(UpdateView):
    model = Image
    template_name = "myapp/image/image_update.html"
    form_class = ImageForm
    success_url = reverse_lazy("myapp:image_list")
    failure_url = "/image/update/"

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Update"
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice! Update Image"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        return context

    # invalid form
    def form_invalid(self, form):
        # print(form.cleaned_data)
        return super().form_invalid(form)

    def form_valid(self, form):
        # Get the Image instance being deleted
        image = self.get_object()
        # print("image", image)

        imagePreprocessing = ImagePreprocessing.objects.filter(image=image)

        # delete ImagePreprocessing records related to the Image
        for image_preprocessing in imagePreprocessing:
            # print("image_preprocessing", image_preprocessing)
            # delete Segmentation records related to the ImagePreprocessing
            segmentations = Segmentation.objects.filter(
                image_preprocessing=image_preprocessing
            )
            for segmentation in segmentations:
                # print("segmentation", segmentation)
                # delete SegmentationResult records related to the Segmentation
                segmentation_results = SegmentationResult.objects.filter(
                    segment=segmentation
                )
                for segmentation_result in segmentation_results:
                    segmentation_result.delete()
                image_seg = segmentation.image_segmented.url
                # print("image_seg", image_seg)
                if os.path.exists(image_seg):
                    os.remove(image_seg)
                segmentation.delete()
            image_precolor = image_preprocessing.image_preprocessing_color.url
            # print("image_precolor", image_precolor)
            if os.path.exists(image_precolor):
                # print("image_precolor", os.path.exists(image_precolor), "deleted")
                os.remove(image_precolor)
            image_pregray = image_preprocessing.image_preprocessing_gray.url
            # print("image_pregray", image_pregray)
            if os.path.exists(image_pregray):
                # print("image_pregray", os.path.exists(image_pregray), "deleted")
                os.remove(image_pregray)
            image_ground = image_preprocessing.image_ground_truth.url
            # print("image_ground", image_ground)
            if os.path.exists(image_ground):
                # print("image_ground", os.path.exists(image_ground), "deleted")
                os.remove(image_ground)
            image_preprocessing.delete()

        # delete Image instance

        # image.delete()
        # print("image", image, "deleted")
        image_old = image.image.url
        # print("image_old klaaaaaaaaaaaaaa", image_old)
        if os.path.exists(image_old):
            print("image_old", os.path.exists(image_old), "deleted")
            os.remove(image_old)

        image_data = form.cleaned_data["image"].read()
        image_array = np.frombuffer(image_data, np.uint8)
        image_channel = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[2]
        image_dpi = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[0]
        form.instance.dpi = image_dpi
        form.instance.channel = image_channel
        form.instance.image = form.cleaned_data["image"]
        image_obj = form.instance
        # delete old image
        image_old = image.image.url
        # print("image_obj", image_obj)

        parameters = [
            {
                "scale": scale,
                "brightness": brightness,
                "contrast": contrast,
                "spatial_filter": spatial_filter,
            }
            for scale in [0.5, 0.75, 1.0, 1.25, 1.5]
            for brightness in [0.5, 0.75, 1.0, 1.25, 1.5]
            for contrast in [0.5, 0.75, 1.0, 1.25, 1.5]
            for spatial_filter in [
                ("mean_filter", 3),
                ("median_filter", 3),
                ("gaussian_filter", 3),
            ]
        ]

        total_combinations = len(parameters)
        target_count = 50
        step = total_combinations // target_count

        selected_parameters = []

        for i in range(0, total_combinations, step):
            selected_parameters.append(parameters[i])

        random.shuffle(selected_parameters)

        # print("selected_parameters", selected_parameters)

        process_and_save_image_preprocessing(
            image_obj, image_array, selected_parameters
        )
        return super().form_valid(form)

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageDeleteView(DeleteView):
    model = Image
    template_name = "myapp/image/image_delete.html"
    success_url = reverse_lazy("myapp:image_list")

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Delete"
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice! Delete Image"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

    # override post method
    def post(self, request, *args, **kwargs):
        # Get the Image instance being deleted
        image = self.get_object()
        # print("image", image)

        imagePreprocessing = ImagePreprocessing.objects.filter(image=image)

        # delete ImagePreprocessing records related to the Image
        for image_preprocessing in imagePreprocessing:
            # print("image_preprocessing", image_preprocessing)
            # delete Segmentation records related to the ImagePreprocessing
            segmentations = Segmentation.objects.filter(
                image_preprocessing=image_preprocessing
            )
            for segmentation in segmentations:
                # print("segmentation", segmentation)
                # delete SegmentationResult records related to the Segmentation
                segmentation_results = SegmentationResult.objects.filter(
                    segment=segmentation
                )
                for segmentation_result in segmentation_results:
                    segmentation_result.delete()
                image_seg = segmentation.image_segmented.url
                # print("image_seg", image_seg)
                if os.path.exists(image_seg):
                    os.remove(image_seg)
                segmentation.delete()
            image_precolor = image_preprocessing.image_preprocessing_color.url
            # print("image_precolor", image_precolor)
            if os.path.exists(image_precolor):
                # print("image_precolor", os.path.exists(image_precolor), "deleted")
                os.remove(image_precolor)
            image_pregray = image_preprocessing.image_preprocessing_gray.url
            # print("image_pregray", image_pregray)
            if os.path.exists(image_pregray):
                # print("image_pregray", os.path.exists(image_pregray), "deleted")
                os.remove(image_pregray)
            image_ground = image_preprocessing.image_ground_truth.url
            # print("image_ground", image_ground)
            if os.path.exists(image_ground):
                # print("image_ground", os.path.exists(image_ground), "deleted")
                os.remove(image_ground)
            image_preprocessing.delete()

        # delete the Image record and its associated image file
        image_paths = [image.image.url]

        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)

        # delete Image instance
        image.delete()

        # return to the image list page
        return redirect("myapp:image_list")


class ImageUploadView(CreateView):
    form_class = ImageForm
    template_name = "myapp/image/image_upload.html"
    failure_url = "/image/upload/"
    # success_url = reverse_lazy('image_list')  # Assuming you have a URL name for the image list view

    # invalid form
    def form_invalid(self, form):
        # print(form.cleaned_data)
        return super().form_invalid(form)

    def form_valid(self, form):
        image_data = form.cleaned_data["image"].read()
        image_array = np.frombuffer(image_data, np.uint8)
        image_channel = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[2]
        image_dpi = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED).shape[0]
        form.instance.dpi = image_dpi
        form.instance.channel = image_channel
        image_obj = form.save()

        parameters = [
            {
                "scale": scale,
                "brightness": brightness,
                "contrast": contrast,
                "spatial_filter": spatial_filter,
            }
            for scale in [0.5, 0.75, 1.0, 1.25, 1.5]
            for brightness in [0.5, 0.75, 1.0, 1.25, 1.5]
            for contrast in [0.5, 0.75, 1.0, 1.25, 1.5]
            for spatial_filter in [
                ("mean_filter", 3),
                ("median_filter", 3),
                ("gaussian_filter", 3),
            ]
        ]

        total_combinations = len(parameters)
        target_count = 50
        step = total_combinations // target_count

        selected_parameters = []

        for i in range(0, total_combinations, step):
            selected_parameters.append(parameters[i])

        random.shuffle(selected_parameters)

        # print("selected_parameters", selected_parameters)

        process_and_save_image_preprocessing(
            image_obj, image_array, selected_parameters
        )
        return redirect("myapp:image_list")

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Upload"
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice! Create Image"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


def hitung_total():
    # Menghitung total Image
    total_image = Image.objects.count()

    # Menghitung total Image yang Di ImagePreprocessing
    total_image_preprocessing = ImagePreprocessing.objects.count()

    # Menghitung total Image yang Di ImagePreprocessing yang sudah Di Segmentation
    total_segmented_image = Segmentation.objects.count()

    return total_image, total_image_preprocessing, total_segmented_image


def hitung_jumlah_segmentation_type():
    # Mengambil semua objek Segmentation
    segmentations = Segmentation.objects.all()

    # Menghitung jumlah tipe segmentasi yang unik
    jumlah_segmentation_type = (
        segmentations.values("segmentation_type").distinct().count()
    )

    return jumlah_segmentation_type


class ImageSummaryView(ListView):
    model = Image
    template_name = "myapp/image/image_summary.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 10

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Summary"
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice! Image Summary"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False).values("username").distinct()
        )
        context["uploaders_name"] = uploaders_name

        # Panggil fungsi hitung_total()
        total_image, total_image_preprocessing, total_segmented_image = hitung_total()

        context["total_image"] = total_image
        context["total_image_preprocessing"] = total_image_preprocessing
        context["total_segmented_image"] = total_segmented_image
        jumlah_segmentation_type = hitung_jumlah_segmentation_type()
        context["total_segmentation_type"] = jumlah_segmentation_type

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

        chartjs_data = {
            "labels_user": json.dumps(list(labels_user)),
            "data_user": json.dumps(list(data_user)),
            "num_labels_user": num_labels_user,
            "labels_color": json.dumps(labels_color),
            "data_color": json.dumps(data_color),
            "num_labels_color": len(labels_color),
        }
        context["chartjs"] = chartjs_data

        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageListView(ListView):
    model = Image
    template_name = "myapp/image/image_list.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 10

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image List"
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice!"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)

        # Prepare uploaders data as a list of dictionaries
        uploaders = []
        user_image_count = get_user_image_count()
        for name, count in user_image_count:
            if count > 0:
                uploaders.append({"name": name, "count": count})
        context["uploaders"] = uploaders
        # categories color name
        context["colors"] = self.model.objects.values_list(
            "color", flat=True
        ).distinct()
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = super().get_queryset()

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

        return queryset


class ImageUploaderView(ListView):
    model = Image
    template_name = "myapp/image/image_by_uploader.html"
    context_object_name = "images"
    ordering = ["-created_at"]
    paginate_by = 10

    # get queryset
    def get_queryset(self):
        uploader = self.kwargs["uploader"]
        search_query = self.request.GET.get("search")
        queryset = super().get_queryset()

        if search_query:
            queryset = Image.objects.filter(
                Q(uploader__username=uploader)
                & (
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
            )
        return queryset

    # update context
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Capitalize first letter of uploader
        context["title"] = "Image Uploader " + self.kwargs["uploader"].capitalize()
        context["kwargs_uploader"] = self.kwargs["uploader"]
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice!"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader name with name of uploader in User model
        uploaders_name = (
            User.objects.filter(image__isnull=False)
            .distinct()
            .values_list("username", flat=True)
        )
        # count Image by uploader
        uploaders_count = (
            Image.objects.values("uploader")
            .distinct()
            .annotate(count=Count("uploader"))
            .values_list("count", flat=True)
            .order_by("-count")
        )
        # context['uploaders'] = {'name': uploaders_name, 'count': uploaders_count}
        uploaders = []
        for name, count in zip(uploaders_name, uploaders_count):
            uploaders.append({"name": name, "count": count})
        context["uploaders"] = uploaders
        # categories color name
        context["colors"] = self.model.objects.values_list(
            "color", flat=True
        ).distinct()
        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)


class ImageDetailView(DetailView):
    model = Image
    template_name = "myapp/image/image_detail.html"
    context_object_name = "image"
    paginate_by = 54  # Menampilkan 10 gambar per halaman

    def get_segmentation_data(self, segmentation_type):
        image_preprocessing = ImagePreprocessing.objects.filter(image=self.object)
        if segmentation_type == "all":
            segmentation = Segmentation.objects.filter(
                image_preprocessing__in=image_preprocessing,
            )
        else:
            segmentation = Segmentation.objects.filter(
                image_preprocessing__in=image_preprocessing,
                segmentation_type=segmentation_type,
            )

        segmentation = segmentation.order_by(
            "-f1_score",
            "-rand_score",
            "-jaccard_score",
        )
        # Urutkan dari terendah ke tertinggi
        segmentation = sorted(
            segmentation,
            key=lambda x: (
                x.f1_score,
                x.rand_score,
                x.jaccard_score,
            ),
        )

        labels = [seg.segmentation_type for seg in segmentation]
        f1_score = [seg.f1_score for seg in segmentation]
        rand_score = [seg.rand_score for seg in segmentation]
        jaccard_score = [seg.jaccard_score for seg in segmentation]

        # get 1st segmentation data as best
        data_length = len(labels)
        best = segmentation[data_length - 1]

        return {
            "labels": json.dumps(list(labels)),
            "data_f1_score": json.dumps(list(f1_score)),
            "data_rand_score": json.dumps(list(rand_score)),
            "data_jaccard_score": json.dumps(list(jaccard_score)),
            "best": best,
        }

    # update context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Image Detail"
        context["contributor"] = "VisionSlice Team"
        context["content"] = "Welcome to VisionSlice!"
        context["app_css"] = "myapp/css/styles.css"
        context["app_js"] = "myapp/js/scripts.js"
        context["logo"] = "myapp/images/Logo.png"
        context["menus"] = menus
        set_user_menus(self.request, context)
        # categories uploader by uploader name in Image model uploader_id
        context["uploader"] = User.objects.get(id=self.object.uploader_id)
        # get 5 image by uploader lastest
        context["images"] = Image.objects.filter(
            uploader_id=self.object.uploader_id
        ).order_by("-created_at")[:5]

        # Get all images by image id
        image_list = ImagePreprocessing.objects.filter(image=self.object)
        # get segmentation by imagepreprocessing id and add related imagepreprocessing to image_list
        color_query = self.request.GET.get("color")
        segmentation_type_query = self.request.GET.get("type")
        segmentation = (
            Segmentation.objects.filter(image_preprocessing__in=image_list)
            .prefetch_related("image_preprocessing")
            .order_by("-created_at")
        )
        type_dict = segmentation.values_list("segmentation_type", flat=True).distinct()
        type_dict = list(set(type_dict))
        context["segmentation_type_dict"] = type_dict
        # print(segmentation_type_query)
        if segmentation_type_query is None or segmentation_type_query == "all":
            segmentation = (
                Segmentation.objects.filter(image_preprocessing__in=image_list)
                .prefetch_related("image_preprocessing")
                .order_by("-created_at")
            )
        else:
            segmentation = (
                Segmentation.objects.filter(
                    image_preprocessing__in=image_list,
                    segmentation_type=segmentation_type_query,
                )
                .prefetch_related("image_preprocessing")
                .order_by("-created_at")
            )

        # Create paginator object
        paginator = Paginator(segmentation, self.paginate_by)

        # Get the current page number from the request's GET parameters
        page_number = self.request.GET.get("page")

        # Get the page object for the current page number
        page_obj = paginator.get_page(page_number)

        # Add the paginated images to the context and add image_list and paginator
        # to the context as well
        context["image_list"] = page_obj.object_list
        context["page_obj"] = page_obj
        # if page_obj is_paginated
        context["is_paginated"] = page_obj.has_other_pages()

        chartjs_data = {}

        if segmentation_type_query is None or segmentation_type_query == "all":
            # if model Segmentation is not empty
            if segmentation:
                chartjs_data = self.get_segmentation_data("all")
            else:
                chartjs_data = ""
            # get 1st segmentation chartjs data
        else:
            chartjs_data = self.get_segmentation_data(segmentation_type_query)

        context["chartjs"] = chartjs_data

        return context

    # override get method
    def get(self, request, *args, **kwargs):
        # codition request user is oot authenticated
        if not request.user.is_authenticated:
            return redirect("myapp:signin")
        # condition request user is authenticated
        else:
            return super().get(request, *args, **kwargs)
