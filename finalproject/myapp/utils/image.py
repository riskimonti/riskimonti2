from django.core.paginator import Paginator

# models import
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import transaction

# cv2 import
import cv2

# numpy import
import numpy as np
from PIL import Image as PILImage

# PILImageEnhance
from PIL import ImageEnhance as PILImageEnhance
from django.core.files.base import ContentFile
import io
import uuid
import scipy.ndimage.filters as filters

# datetime import
from datetime import datetime


def apply_spatial_filter(image, filter_type, filter_size):
    image_array = np.array(image)

    if filter_type == "mean_filter":
        filtered_image = filters.uniform_filter(
            image_array, size=filter_size, mode="constant"
        )
    elif filter_type == "median_filter":
        filtered_image = filters.median_filter(
            image_array, size=filter_size, mode="constant"
        )
    elif filter_type == "gaussian_filter":
        sigma = filter_size / 6
        filtered_image = filters.gaussian_filter(
            image_array, sigma=sigma, mode="constant"
        )
    else:
        raise ValueError("Invalid filter type")

    filtered_image = PILImage.fromarray(filtered_image)
    return filtered_image


def get_user_image_count():
    user_image_count = []
    users = User.objects.all()
    for user in users:
        image_count = Image.objects.filter(uploader=user).count()
        user_image_count.append((user.username, image_count))
    return user_image_count


def process_and_save_image_preprocessing(image_obj, image_array, parameters):
    original_image = PILImage.fromarray(cv2.imdecode(image_array, cv2.COLOR_BGR2RGB))
    counter = 0
    for param in parameters:
        scale = param["scale"]
        brightness = param["brightness"]
        contrast = param["contrast"]
        spatial_filter = param["spatial_filter"]

        preprocessing_instance = ImagePreprocessing()
        preprocessing_instance.image = image_obj

        # Resize
        resized_image = original_image.resize(
            (int(original_image.width * scale), int(original_image.height * scale))
        )
        # print shape

        preprocessing_instance.resize = True
        preprocessing_instance.resize_width = resized_image.width
        preprocessing_instance.resize_height = resized_image.height
        preprocessing_instance.resize_percent = scale * 100

        # Adjust brightness
        enhanced_image = PILImageEnhance.Brightness(resized_image).enhance(brightness)
        # print("enhanced_image.shape brightness", enhanced_image.size, counter)

        preprocessing_instance.brightness = True
        preprocessing_instance.brightness_percent = brightness * 100

        # Adjust contrast
        enhanced_image = PILImageEnhance.Contrast(enhanced_image).enhance(contrast)
        # print("enhanced_image.shape contrast", enhanced_image.size, counter)

        preprocessing_instance.contrast = True
        preprocessing_instance.contrast_percent = contrast * 100

        # Convert to grayscale
        enhanced_image_gray = np.array(enhanced_image.convert("L"))
        enhanced_image_color = np.array(enhanced_image)

        # Apply spatial filter
        filtered_image_gray = None
        filtered_image_color = None
        filter_type, filter_size = spatial_filter

        if filter_type == "mean_filter":
            filtered_image_gray = filters.uniform_filter(
                enhanced_image_gray, size=filter_size, mode="constant"
            )
            filtered_image_color = filters.uniform_filter(
                enhanced_image_color, size=filter_size, mode="constant"
            )
            # print( "filtered_image_gray.shape mean_filter",filtered_image_gray.shape, counter,)
            # print("filtered_image_color.shape mean_filter", filtered_image_color.shape, counter,)
            preprocessing_instance.mean_filter = True
            preprocessing_instance.mean_filter_size = filter_size
            preprocessing_instance.median_filter = False
            preprocessing_instance.gaussian_filter = False

        elif filter_type == "median_filter":
            filtered_image_gray = filters.median_filter(
                enhanced_image_gray, size=filter_size, mode="constant"
            )
            filtered_image_color = filters.median_filter(
                enhanced_image_color, size=filter_size, mode="constant"
            )
            # print("filtered_image_gray.shape median_filter",filtered_image_gray.shape,counter,)
            # print("filtered_image_color.shape median_filter",filtered_image_color.shape,counter,)
            preprocessing_instance.median_filter = True
            preprocessing_instance.median_filter_size = filter_size
            preprocessing_instance.mean_filter = False
            preprocessing_instance.gaussian_filter = False

        elif filter_type == "gaussian_filter":
            sigma = filter_size / 6
            filtered_image_gray = filters.gaussian_filter(
                enhanced_image_gray, sigma=sigma, mode="constant"
            )
            filtered_image_color = filters.gaussian_filter(
                enhanced_image_color, sigma=sigma, mode="constant"
            )
            # print("filtered_image_gray.shape gaussian_filter",filtered_image_gray.shape, counter,)
            # print("filtered_image_color.shape gaussian_filter",filtered_image_color.shape,counter,)
            preprocessing_instance.gaussian_filter = True
            preprocessing_instance.gaussian_filter_size = filter_size
            preprocessing_instance.mean_filter = False
            preprocessing_instance.median_filter = False

        filtered_image_gray = PILImage.fromarray(filtered_image_gray)
        filtered_image_color = PILImage.fromarray(filtered_image_color)

        # if filtered_image_color is to bright or to dark, skip it and use the resized image
        if filtered_image_color.getextrema()[0] == filtered_image_color.getextrema()[1]:
            filtered_image_color = resized_image

        # print("filtered_image_gray.shape", filtered_image_gray.size, counter)
        # print("filtered_image_color.shape", filtered_image_color.size, counter)

        # Save the processed image
        processed_image_gray_stream = io.BytesIO()
        filtered_image_gray.save(processed_image_gray_stream, format="JPEG")
        processed_image_gray_stream.seek(0)

        processed_image_color_stream = io.BytesIO()
        filtered_image_color.save(processed_image_color_stream, format="JPEG")
        processed_image_color_stream.seek(0)

        preprocessing_instance.image_preprocessing_color.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(processed_image_color_stream.getvalue()),
            save=False,
        )

        preprocessing_instance.image_preprocessing_gray.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(processed_image_gray_stream.getvalue()),
            save=False,
        )

        # created_at and updated_at
        preprocessing_instance.created_at = datetime.now()
        preprocessing_instance.updated_at = datetime.now()

        # ground truth image
        # Create a blank ground truth image
        filtered_image_to_array = np.array(filtered_image_gray)
        ground_truth = np.zeros_like(filtered_image_to_array)

        # set black areas as foreground (255) and white areas as background (0) with the threshold adaptative
        _, thresholded_image = cv2.threshold(
            filtered_image_to_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        ground_truth[thresholded_image > ground_truth] = 255

        # Remove small black areas
        contours, _ = cv2.findContours(
            ground_truth.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        min_area_threshold = 100
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area_threshold:
                cv2.drawContours(
                    ground_truth, [contour], -1, (0, 0, 0), thickness=cv2.FILLED
                )

        # set black area is the background, inverse of the image and background is the biggest area
        if np.sum(ground_truth) < np.sum(255 - ground_truth):
            ground_truth = 255 - ground_truth

        # Save the processed image
        ground_truth = PILImage.fromarray(ground_truth)
        # print("ground_truth.shape", ground_truth.size, counter)
        ground_truth_image_stream = io.BytesIO()
        ground_truth.save(ground_truth_image_stream, format="JPEG")
        ground_truth_image_stream.seek(0)

        preprocessing_instance.image_ground_truth.save(
            uuid.uuid4().hex + ".jpg",
            ContentFile(ground_truth_image_stream.read()),
            save=False,
        )

        counter += 1
        preprocessing_instance.save()
