from django.shortcuts import redirect, render
from django.views import View
from myapp.menus import menus, set_user_menus
from django.views.generic import ListView
from django.contrib.auth.models import User
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
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


class ImageGraphClassView(ListView):
    model = Image
    template_name = "myapp/image/image_graph.html"
    context_object_name = "images"
    paginate_by = 10
    extra_context = {
        "title": "Image Graph",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "content": "Welcome to TOKSlice!",
        "contributor": "TOKSlice Team",
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
        queryset = Image.objects.all()

        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi yang diinginkan.
            queryset = queryset.filter(
                Q(color__icontains=search_query)
            ).prefetch_related(
                "imagepreprocessing_set",
                "imagepreprocessing_set__segmentation_set",
                "imagepreprocessing_set__segmentation_set__segmentationresult_set",
            )
            # change the page_obj add the search_query
            self.extra_context["search"] = search_query

        # print queryset 1 data saja tampilkan lengkap dengan relasi
        data = queryset.first()

        # Cetak informasi dari model Image
        # print("Image:")
        # print(f"ID: {data.id}")
        # print(f"Uploader: {data.uploader.username}")
        # Cetak informasi lainnya dari model Image

        # Cetak informasi dari model ImagePreprocessing
        image_preprocessing = data.imagepreprocessing_set.first()
        # print("\nImage Preprocessing:")
        # print(f"ID: {image_preprocessing.id}")
        # Cetak informasi lainnya dari model ImagePreprocessing

        # Cetak informasi dari model Segmentation
        segmentation = image_preprocessing.segmentations.first()
        # print("\nSegmentation:")
        # print(f"ID: {segmentation.id}")
        # Cetak informasi lainnya dari model Segmentation

        # Cetak informasi dari model SegmentationResult
        segmentation_result = segmentation.segmentationresult_set.first()
        # print("\nSegmentation Result:")
        # print(f"ID: {segmentation_result.id}")
        # Cetak informasi lainnya dari model SegmentationResult

        # Ambil semua nilai unik dari field color, width, height
        color_dict = queryset.values_list("color", flat=True).distinct()
        color_dict = list(color_dict)
        width_dict = queryset.values_list("width", flat=True).distinct()
        width_dict = list(width_dict)
        height_dict = queryset.values_list("height", flat=True).distinct()
        height_dict = list(height_dict)
        size_dict = queryset.values_list("size", flat=True).distinct()
        # convert size_dict to KB and MB
        size_dict = [size / 1024 if size > 1024 else size for size in size_dict]
        # size_dict float 2 digit
        size_dict = [round(size, 2) for size in size_dict]
        size_dict = list(size_dict)
        channel_dict = queryset.values_list("channel", flat=True).distinct()
        channel_dict = list(channel_dict)
        format_dict = queryset.values_list("format", flat=True).distinct()
        format_dict = list(format_dict)
        dpi_dict = queryset.values_list("dpi", flat=True).distinct()
        dpi_dict = list(dpi_dict)
        distance_dict = queryset.values_list("distance", flat=True).distinct()
        distance_dict = list(distance_dict)
        uploader_dict = queryset.values_list("uploader__username", flat=True).distinct()
        uploader_dict = list(uploader_dict)

        # Buat dictionary untuk memetakan nilai color, width, height menjadi angka
        color_mapping = {color: index for index, color in enumerate(color_dict)}
        width_mapping = {width: index for index, width in enumerate(width_dict)}
        height_mapping = {height: index for index, height in enumerate(height_dict)}
        size_mapping = {size: index for index, size in enumerate(size_dict)}
        channel_mapping = {channel: index for index, channel in enumerate(channel_dict)}
        format_mapping = {format: index for index, format in enumerate(format_dict)}
        dpi_mapping = {dpi: index for index, dpi in enumerate(dpi_dict)}
        distance_mapping = {
            distance: index for index, distance in enumerate(distance_dict)
        }
        uploader_mapping = {
            uploader: index for index, uploader in enumerate(uploader_dict)
        }

        # Ambil semua nilai dari field color, width, height
        color_data = queryset.values_list("color", flat=True)
        width_data = queryset.values_list("width", flat=True)
        height_data = queryset.values_list("height", flat=True)
        size_data = queryset.values_list("size", flat=True)
        size_data = [size / 1024 if size > 1024 else size for size in size_data]
        size_data = [round(size, 2) for size in size_data]
        channel_data = queryset.values_list("channel", flat=True)
        format_data = queryset.values_list("format", flat=True)
        dpi_data = queryset.values_list("dpi", flat=True)
        distance_data = queryset.values_list("distance", flat=True)
        uploader_data = queryset.values_list("uploader__username", flat=True)
        color_data = list(color_data)
        width_data = list(width_data)
        height_data = list(height_data)
        size_data = list(size_data)
        channel_data = list(channel_data)
        format_data = list(format_data)
        dpi_data = list(dpi_data)
        distance_data = list(distance_data)
        uploader_data = list(uploader_data)

        # Ubah color_data menjadi angka sesuai dengan color_mapping
        color_data_int = [color_mapping[color] for color in color_data]
        width_data_int = [width_mapping[width] for width in width_data]
        height_data_int = [height_mapping[height] for height in height_data]
        size_data_int = [size_mapping[size] for size in size_data]
        channel_data_int = [channel_mapping[channel] for channel in channel_data]
        format_data_int = [format_mapping[format] for format in format_data]
        dpi_data_int = [dpi_mapping[dpi] for dpi in dpi_data]
        distance_data_int = [distance_mapping[distance] for distance in distance_data]
        uploader_data_int = [uploader_mapping[uploader] for uploader in uploader_data]

        # Buat labels berdasarkan color_data_int
        labels = [
            "{} {}".format(color_dict[color_data_int[i]], i + 1)
            for i in range(len(color_data_int))
        ]

        # context chart_js
        self.extra_context["chartjs"] = {
            "data_color": color_data_int,
            "dict_color": color_dict,
            "data_width": width_data_int,
            "dict_width": width_dict,
            "data_height": height_data_int,
            "dict_height": height_dict,
            "data_size": size_data_int,
            "dict_size": size_dict,
            "data_channel": channel_data_int,
            "dict_channel": channel_dict,
            "data_format": format_data_int,
            "dict_format": format_dict,
            "data_dpi": dpi_data_int,
            "dict_dpi": dpi_dict,
            "data_distance": distance_data_int,
            "dict_distance": distance_dict,
            "data_uploader": uploader_data_int,
            "dict_uploader": uploader_dict,
            "labels": labels,
        }

        return queryset


class ImageTableColorClassView(ListView):
    model = Image
    template_name = "myapp/image/image_table_color.html"
    context_object_name = "images"
    paginate_by = 10
    extra_context = {
        "title": "Image Table Color",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "content": "Welcome to TOKSlice!",
        "contributor": "TOKSlice Team",
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

        # Query for segmentation results
        queryset = SegmentationResult.objects.filter(
            image__in=images,
            segmentation_type__in=segmentation_types,
            rank=1,
        ).order_by("image", "rank")
        ccolor_dict = queryset.values_list("image__color", flat=True).distinct()
        ccolor_dict = list(ccolor_dict)
        # ambil semua nilai unik color dari list color_dict
        ccolor_dict = list(set(ccolor_dict))
        self.extra_context["color_dict"] = ccolor_dict
        csegmentation_type_dict = queryset.values_list(
            "segmentation_type", flat=True
        ).distinct()
        csegmentation_type_dict = list(csegmentation_type_dict)
        csegmentation_type_dict = list(set(csegmentation_type_dict))
        self.extra_context["segmentation_type_dict"] = csegmentation_type_dict
        if color_query and color_query != "all":
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi color
            queryset = queryset.filter(image__color=color_query)

        if segmentation_type_query and segmentation_type_query != "all":
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi segmentation_type
            queryset = queryset.filter(segmentation_type=segmentation_type_query)

        # Calculate the average of jaccard_score, rand_score, and f1_score
        average_scores = queryset.aggregate(
            avg_mse=Avg("segment__mse"),
            avg_psnr=Avg("segment__psnr"),
        )

        avg_mse = average_scores["avg_mse"]
        self.extra_context["avg_mse"] = avg_mse
        avg_psnr = average_scores["avg_psnr"]
        self.extra_context["avg_psnr"] = avg_psnr

        return queryset


class ImageGraphColorClassView(ListView):
    model = Image
    template_name = "myapp/image/image_graph_color.html"
    context_object_name = "images"
    paginate_by = 10
    extra_context = {
        "title": "Image Graph Color",
        "menus": menus,
        "logo": "myapp/images/Logo.png",
        "content": "Welcome to TOKSlice!",
        "contributor": "TOKSlice Team",
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

        # Query for segmentation results
        queryset = SegmentationResult.objects.filter(
            image__in=images,
            segmentation_type__in=segmentation_types,
            rank=1,
        ).order_by("image", "rank")
        ccolor_dict = queryset.values_list("image__color", flat=True).distinct()
        ccolor_dict = list(ccolor_dict)
        ccolor_dict = list(set(ccolor_dict))
        self.extra_context["color_dict"] = ccolor_dict
        if search_query:
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi color
            # Query for segmentation results
            queryset = SegmentationResult.objects.filter(
                image__in=images,
                segmentation_type__in=segmentation_types,
                rank=1,
                image__color=search_query,
            ).order_by("image", "rank")

        if search_query == "all":
            # Jika ada parameter pencarian, filter queryset berdasarkan kondisi color
            # Query for segmentation results
            queryset = SegmentationResult.objects.filter(
                image__in=images,
                rank=1,
            ).order_by("image", "rank")

        # hitung jumlah data
        total_data = queryset.count()
        # print(total_data)

        # Ambil semua nilai unik dari field unik
        unique_fields = [
            "image__color",
            "segmentation_type",
            "image__width",
            "image__height",
            "image__size",
            "image__channel",
            "image__format",
            "image__dpi",
            "image__distance",
            "image__uploader__username",
            "preprocessing",
            "segment",
        ]

        field_data = {}
        field_mapping = {}

        for field in unique_fields:
            values = queryset.values_list(field, flat=True)
            values_list = list(values)
            field_data[field] = values_list
            field_mapping[field] = {
                value: index for index, value in enumerate(values_list)
            }

        size_data = [
            size / 1024 if size > 1024 else size for size in field_data["image__size"]
        ]
        size_data = [round(size, 2) for size in size_data]

        # Ubah data menjadi angka sesuai dengan mapping
        data_int = {}

        for field, values in field_data.items():
            data_int[field] = [field_mapping[field][value] for value in values]

        # Membuat label berdasarkan data_int
        labels = []
        cn = 0
        cc = 1

        for i in range(len(data_int["image__color"])):
            color_label = field_data["image__color"][data_int["image__color"][i]]
            segmentation_label = field_data["segmentation_type"][
                data_int["segmentation_type"][i]
            ]

            if cn == len(segmentation_types):
                cn = 0
                cc += 1

            if cn != len(segmentation_types):
                cn += 1

            label = "{} {} {}".format(color_label, segmentation_label, cc)
            labels.append(label)

        #  ambil semua data dari model Segmentation berdasarkan field_data["segment"]
        segment_data = Segmentation.objects.filter(id__in=field_data["segment"])

        f1_score_data = segment_data.values_list("f1_score", flat=True)
        f1_score_data = list(f1_score_data)
        rand_score_data = segment_data.values_list("rand_score", flat=True)
        rand_score_data = list(rand_score_data)
        jaccard_score_data = segment_data.values_list("jaccard_score", flat=True)
        jaccard_score_data = list(jaccard_score_data)
        mse_data = segment_data.values_list("mse", flat=True)
        mse_data = list(mse_data)
        psnr_data = segment_data.values_list("psnr", flat=True)
        psnr_data = list(psnr_data)

        unique_fields2 = [
            "f1_score",
            "mse",
            "psnr",
            "rand_score",
            "jaccard_score",
            "image_preprocessing__resize",
            "image_preprocessing__resize_width",
            "image_preprocessing__resize_height",
            "image_preprocessing__resize_percent",
            "image_preprocessing__gaussian_filter",
            "image_preprocessing__gaussian_filter_size",
            "image_preprocessing__median_filter",
            "image_preprocessing__median_filter_size",
            "image_preprocessing__mean_filter",
            "image_preprocessing__mean_filter_size",
            "image_preprocessing__brightness",
            "image_preprocessing__brightness_percent",
            "image_preprocessing__contrast",
            "image_preprocessing__contrast_percent",
            "image_preprocessing__image__image",
            "image_preprocessing__image_preprocessing_gray",
            "image_preprocessing__image_preprocessing_color",
            "image_preprocessing__image_ground_truth",
            "image_segmented",
            "segmentation_type",
        ]

        field_data2 = {}
        field_mapping2 = {}

        for field in unique_fields2:
            values = segment_data.values_list(field, flat=True)
            values_list = list(values)
            field_data2[field] = values_list
            field_mapping2[field] = {
                value: index for index, value in enumerate(values_list)
            }

        for field, values in field_data2.items():
            data_int[field] = [field_mapping2[field][value] for value in values]
        if segmentation_types:
            self.extra_context["total_data"] = len(queryset) / len(segmentation_types)
        else:
            self.extra_context["total_data"] = len(queryset)

        mse_terbaik = max(mse_data) if mse_data else 0
        mse_terjelek = min(mse_data) if mse_data else 0
        indeks_f1_terbaik = mse_data.index(mse_terbaik) if mse_data else 0
        indeks_mse_terjelek = mse_data.index(mse_terjelek) if mse_data else 0

        psnr_terbaik = max(psnr_data) if psnr_data else 0
        psnr_terjelek = min(psnr_data) if psnr_data else 0
        indeks_psnr_terbaik = psnr_data.index(psnr_terbaik) if psnr_data else 0
        indeks_psnr_terjelek = psnr_data.index(psnr_terjelek) if psnr_data else 0

        indeks_terbaik = (
            max(indeks_f1_terbaik, indeks_psnr_terbaik) if f1_score_data else 0
        )
        indeks_terjelek = (
            min(indeks_mse_terjelek, indeks_psnr_terjelek) if f1_score_data else 0
        )

        self.extra_context["best"] = {
            "index": indeks_terbaik,
            "color": field_data["image__color"][indeks_terbaik]
            if field_data["image__color"]
            else None,
            "segmentation": field_data2["segmentation_type"][indeks_terbaik]
            if field_data2["segmentation_type"]
            else None,
            "width": field_data["image__width"][indeks_terbaik]
            if field_data["image__width"]
            else None,
            "height": field_data["image__height"][indeks_terbaik]
            if field_data["image__height"]
            else None,
            "size": field_data["image__size"][indeks_terbaik]
            if field_data["image__size"]
            else None,
            "channel": field_data["image__channel"][indeks_terbaik]
            if field_data["image__channel"]
            else None,
            "format": field_data["image__format"][
                indeks_terbaik if field_data["image__format"] else None
            ]
            if field_data["image__format"]
            else None,
            "dpi": field_data["image__dpi"][indeks_terbaik]
            if field_data["image__dpi"]
            else None,
            "distance": field_data["image__distance"][indeks_terbaik]
            if field_data["image__distance"]
            else None,
            "uploader": field_data["image__uploader__username"][indeks_terbaik]
            if field_data["image__uploader__username"]
            else None,
            "f1_score": f1_score_data[indeks_terbaik] if f1_score_data else None,
            "mse": mse_data[indeks_terbaik] if mse_data else None,
            "psnr": psnr_data[indeks_terbaik] if psnr_data else None,
            "rand_score": rand_score_data[indeks_terbaik] if rand_score_data else None,
            "jaccard_score": jaccard_score_data[indeks_terbaik]
            if jaccard_score_data
            else None,
            "resize": field_data2["image_preprocessing__resize"][indeks_terbaik]
            if field_data2["image_preprocessing__resize"]
            else None,
            "resize_width": field_data2["image_preprocessing__resize_width"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__resize_width"]
            else None,
            "resize_height": field_data2["image_preprocessing__resize_height"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__resize_height"]
            else None,
            "resize_percent": field_data2["image_preprocessing__resize_percent"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__resize_percent"]
            else None,
            "gaussian_filter": field_data2["image_preprocessing__gaussian_filter"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__gaussian_filter"]
            else None,
            "gaussian_filter_size": field_data2[
                "image_preprocessing__gaussian_filter_size"
            ][indeks_terbaik]
            if field_data2["image_preprocessing__gaussian_filter_size"]
            else None,
            "median_filter": field_data2["image_preprocessing__median_filter"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__median_filter"]
            else None,
            "median_filter_size": field_data2[
                "image_preprocessing__median_filter_size"
            ][indeks_terbaik]
            if field_data2["image_preprocessing__median_filter_size"]
            else None,
            "mean_filter": field_data2["image_preprocessing__mean_filter"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__mean_filter"]
            else None,
            "mean_filter_size": field_data2["image_preprocessing__mean_filter_size"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__mean_filter_size"]
            else None,
            "brightness": field_data2["image_preprocessing__brightness"][indeks_terbaik]
            if field_data2["image_preprocessing__brightness"]
            else None,
            "brightness_percent": field_data2[
                "image_preprocessing__brightness_percent"
            ][indeks_terbaik]
            if field_data2["image_preprocessing__brightness"]
            else None,
            "contrast": field_data2["image_preprocessing__contrast"][indeks_terbaik]
            if field_data2["image_preprocessing__contrast"]
            else None,
            "contrast_percent": field_data2["image_preprocessing__contrast_percent"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__contrast_percent"]
            else None,
            "image_url": field_data2["image_preprocessing__image__image"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__image__image"]
            else None,
            "image_pre_gray_url": field_data2[
                "image_preprocessing__image_preprocessing_gray"
            ][indeks_terbaik]
            if field_data2["image_preprocessing__image_preprocessing_gray"]
            else None,
            "image_pre_color_url": field_data2[
                "image_preprocessing__image_preprocessing_color"
            ][indeks_terbaik]
            if field_data2["image_preprocessing__image_preprocessing_color"]
            else None,
            "image_seg": field_data2["image_segmented"][indeks_terbaik]
            if field_data2["image_segmented"]
            else None,
            "image_gt": field_data2["image_preprocessing__image_ground_truth"][
                indeks_terbaik
            ]
            if field_data2["image_preprocessing__image_ground_truth"]
            else None,
        }

        self.extra_context["worst"] = {
            "index": indeks_terjelek,
            "color": field_data["image__color"][indeks_terjelek]
            if field_data["image__color"]
            else None,
            "segmentation": field_data2["segmentation_type"][indeks_terjelek]
            if field_data2["segmentation_type"]
            else None,
            "width": field_data["image__width"][indeks_terjelek]
            if field_data["image__width"]
            else None,
            "height": field_data["image__height"][indeks_terjelek]
            if field_data["image__height"]
            else None,
            "size": field_data["image__size"][indeks_terjelek]
            if field_data["image__size"]
            else None,
            "channel": field_data["image__channel"][indeks_terjelek]
            if field_data["image__channel"]
            else None,
            "format": field_data["image__format"][indeks_terjelek]
            if field_data["image__format"]
            else None,
            "dpi": field_data["image__dpi"][indeks_terjelek]
            if field_data["image__dpi"]
            else None,
            "distance": field_data["image__distance"][indeks_terjelek]
            if field_data["image__distance"]
            else None,
            "uploader": field_data["image__uploader__username"][indeks_terjelek]
            if field_data["image__uploader__username"]
            else None,
            "f1_score": f1_score_data[indeks_terjelek] if f1_score_data else None,
            "mse": mse_data[indeks_terjelek] if mse_data else None,
            "psnr": psnr_data[indeks_terjelek] if psnr_data else None,
            "rand_score": rand_score_data[indeks_terjelek] if rand_score_data else None,
            "jaccard_score": jaccard_score_data[indeks_terjelek]
            if jaccard_score_data
            else None,
            "resize": field_data2["image_preprocessing__resize"][indeks_terjelek]
            if field_data2["image_preprocessing__resize"]
            else None,
            "resize_width": field_data2["image_preprocessing__resize_width"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__resize_width"]
            else None,
            "resize_height": field_data2["image_preprocessing__resize_height"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__resize_height"]
            else None,
            "resize_percent": field_data2["image_preprocessing__resize_percent"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__resize_percent"]
            else None,
            "gaussian_filter": field_data2["image_preprocessing__gaussian_filter"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__gaussian_filter"]
            else None,
            "gaussian_filter_size": field_data2[
                "image_preprocessing__gaussian_filter_size"
            ][indeks_terjelek]
            if field_data2["image_preprocessing__gaussian_filter_size"]
            else None,
            "median_filter": field_data2["image_preprocessing__median_filter"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__median_filter"]
            else None,
            "median_filter_size": field_data2[
                "image_preprocessing__median_filter_size"
            ][indeks_terjelek]
            if field_data2["image_preprocessing__median_filter_size"]
            else None,
            "mean_filter": field_data2["image_preprocessing__mean_filter"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__mean_filter"]
            else None,
            "mean_filter_size": field_data2["image_preprocessing__mean_filter_size"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__mean_filter_size"]
            else None,
            "brightness": field_data2["image_preprocessing__brightness"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__brightness"]
            else None,
            "brightness_percent": field_data2[
                "image_preprocessing__brightness_percent"
            ][indeks_terjelek]
            if field_data2["image_preprocessing__brightness_percent"]
            else None,
            "contrast": field_data2["image_preprocessing__contrast"][indeks_terjelek]
            if field_data2["image_preprocessing__contrast"]
            else None,
            "contrast_percent": field_data2["image_preprocessing__contrast_percent"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__contrast_percent"]
            else None,
            "image_url": field_data2["image_preprocessing__image__image"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__image__image"]
            else None,
            "image_pre_gray_url": field_data2[
                "image_preprocessing__image_preprocessing_gray"
            ][indeks_terjelek]
            if field_data2["image_preprocessing__image_preprocessing_gray"]
            else None,
            "image_pre_color_url": field_data2[
                "image_preprocessing__image_preprocessing_color"
            ][indeks_terjelek]
            if field_data2["image_preprocessing__image_preprocessing_color"]
            else None,
            "image_seg": field_data2["image_segmented"][indeks_terjelek]
            if field_data2["image_segmented"]
            else None,
            "image_gt": field_data2["image_preprocessing__image_ground_truth"][
                indeks_terjelek
            ]
            if field_data2["image_preprocessing__image_ground_truth"]
            else None,
        }

        # context chart_js
        self.extra_context["chartjs"] = {
            "data_color": data_int["image__color"],
            "dict_color": field_data["image__color"],
            "data_segmentation": data_int["segmentation_type"],
            "dict_segmentation": field_data["segmentation_type"],
            "data_width": data_int["image__width"],
            "dict_width": field_data["image__width"],
            "data_height": data_int["image__height"],
            "dict_height": field_data["image__height"],
            "data_size": data_int["image__size"],
            "dict_size": size_data,
            "data_channel": data_int["image__channel"],
            "dict_channel": field_data["image__channel"],
            "data_format": data_int["image__format"],
            "dict_format": field_data["image__format"],
            "data_dpi": data_int["image__dpi"],
            "dict_dpi": field_data["image__dpi"],
            "data_distance": data_int["image__distance"],
            "dict_distance": field_data["image__distance"],
            "data_uploader": data_int["image__uploader__username"],
            "dict_uploader": field_data["image__uploader__username"],
            "data_f1_score": f1_score_data,
            "data_jaccard_score": jaccard_score_data,
            "data_rand_score": rand_score_data,
            "data_psnr": psnr_data,
            "data_mse": mse_data,
            "labels": labels,
        }

        return queryset
