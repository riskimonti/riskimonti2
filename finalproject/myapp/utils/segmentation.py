# import
import cv2
import numpy as np
import uuid
import io
from PIL import Image as PILImage
from django.core.files.base import ContentFile
from myapp.models import Image, ImagePreprocessing, Segmentation, SegmentationResult
from django.db.models import Count, Q, F
from sklearn.metrics import (
    adjusted_rand_score,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    rand_score,
    jaccard_score,
    mean_squared_error,
    mean_absolute_error,
)


def get_segmentation_results_data(image):
    segmentation_types = ["kmeans", "adaptive", "otsu", "sobel", "prewitt", "canny"]

    segmentation_results = Segmentation.objects.filter(
        image_preprocessing__image=image, segmentation_type__in=segmentation_types
    )

    segmentation_count = {
        segmentation_type: 0 for segmentation_type in segmentation_types
    }

    for segmentation_result in segmentation_results:
        segmentation_type = segmentation_result.segmentation_type
        if segmentation_type in segmentation_count:
            segmentation_count[segmentation_type] += 1

    segmentation_results_data = {
        segmentation_type: {
            "available": segmentation_count[segmentation_type] > 0,
            "count": segmentation_count[segmentation_type],
        }
        for segmentation_type in segmentation_types
    }

    return segmentation_results_data


def perform_k_means_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessings.count()
    # print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform kmeans segmentation using the Image and ImagePreprocessing objects
        img = preprocessing.image_preprocessing_color
        img_file = cv2.imread(img.path)
        # conver image to RGB
        img_rgb = cv2.cvtColor(img_file, cv2.COLOR_BGR2RGB)
        img_2d = img_rgb.astype(np.float32)

        # Print the shape of img_2d to check its dimensions
        counter += 1
        # print("img_2d shape:", img_2d.shape, "-->", counter)

        img_2d = img_2d.reshape(img_2d.shape[0] * img_2d.shape[1], img_2d.shape[2])

        # Verify the value of cluster is valid
        cluster = 3
        if cluster <= 0:
            raise ValueError("The number of clusters should be greater than zero.")

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(
            img_2d, cluster, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )

        center = np.uint8(center)

        segmented_data = center[label.flatten()]
        segmented_image = segmented_data.reshape(img_rgb.shape)

        # Dapatkan jalur file gambar
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth_array = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth_array)
        segmented_array = np.array(segmented_image)

        # Flatten array gambar
        ground_truth_flatten = ground_truth_array.flatten()
        segmented_flatten = segmented_array.flatten()

        type = "kmeans"
        average = "weighted"
        zero_division = 1
        # Call the calculate_scores function
        scores = calculate_scores(
            ground_truth_flatten,
            segmented_flatten,
            type,
            average=average,
            zero_division=zero_division,
        )
        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "kmeans"
        segmented_image = PILImage.fromarray(segmented_image)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )

        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()


def get_top_segmentations(Image, segmentation_type):
    top_segmentations = (
        Segmentation.objects.select_related("image_preprocessing__image")
        .filter(image_preprocessing__image=Image, segmentation_type=segmentation_type)
        .order_by(
            F("f1_score").desc(),
            F("rand_score").desc(),
            F("jaccard_score").desc(),
            F("mse").desc(),
            F("psnr").desc(),
            F("mae").desc(),
            F("rmse").desc(),
        )[:15]
    )

    segmentation_instances = []
    rank = 1  # Start with rank 1

    # Iterate over each segmentation result
    for segmentation in top_segmentations:
        segmentation_instance = SegmentationResult.objects.create(
            image=Image,
            segmentation_type=segmentation_type,
            segment=segmentation,
            preprocessing=segmentation.image_preprocessing,
            rank=rank,
        )

        segmentation_instance.save()
        rank += 1

    return segmentation_instances


def calculate_scores(ground_truth, segmented, type, average="binary", zero_division=1):
    scores = {}
    scores["type"] = type
    average = "weighted" if type == "kmeans" else average

    # convert ground_truth and segmented to numpy array
    segmented = np.array(segmented)
    ground_truth = np.array(ground_truth)

    segmented = np.where(segmented > 0, 1, segmented)
    ground_truth = np.where(ground_truth > 0, 1, ground_truth)

    scores["f1_score"] = str(
        round(
            f1_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["f1_score"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["f1_score"] = str(
            round(
                f1_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    scores["precision"] = str(
        round(
            precision_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["precision"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["precision"] = str(
            round(
                precision_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    scores["recall"] = str(
        round(
            recall_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["recall"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["recall"] = str(
            round(
                recall_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    scores["accuracy"] = str(round(accuracy_score(ground_truth, segmented), 4))
    if scores["accuracy"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["accuracy"] = str(
            round(accuracy_score(ground_truth, reverse_segmented), 4)
        )

    scores["rand_score"] = str(round(rand_score(ground_truth, segmented), 4))
    if scores["rand_score"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["rand_score"] = str(
            round(rand_score(ground_truth, reverse_segmented), 4)
        )

    scores["jaccard_score"] = str(
        round(
            jaccard_score(
                ground_truth,
                segmented,
                average=average,
                zero_division=zero_division,
            ),
            4,
        )
    )
    if scores["jaccard_score"] in ["nan", "inf", "-inf", "None", "0.0", "0"]:
        reverse_segmented = np.where(segmented == 0, 1, 0)
        scores["jaccard_score"] = str(
            round(
                jaccard_score(
                    ground_truth,
                    reverse_segmented,
                    average=average,
                    zero_division=zero_division,
                ),
                4,
            )
        )

    mse = np.mean((ground_truth - segmented) ** 2)
    scores["mse"] = str(round(mse, 4))
    scores["mae"] = str(round(mean_absolute_error(ground_truth, segmented), 4))
    scores["rmse"] = str(
        round(
            mean_squared_error(ground_truth, segmented, squared=False),
            4,
        )
    )
    scores["psnr"] = (
        "inf"
        if mse == 0
        else str(
            round(
                10 * np.log10((255**2) / np.mean((ground_truth - segmented) ** 4)), 4
            )
        )
    )
    # print(scores)
    return scores


def perform_adaptive_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessings.count()
    # print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform kmeans segmentation using the Image and ImagePreprocessing objects
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        block_size = 11
        constant = 2

        # Convert the image to grayscale
        img_file = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        segmented = np.zeros_like(img_file)

        # Adaptive thresholding
        thresholded_image = cv2.adaptiveThreshold(
            img_file,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            constant,
        )

        # Remove small black areas
        contours, _ = cv2.findContours(
            thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        min_area_threshold = 100
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area_threshold:
                cv2.drawContours(
                    segmented, [contour], -1, (255, 255, 255), thickness=cv2.FILLED
                )

        # Combine the original image with the edges image
        segmented = cv2.bitwise_and(thresholded_image, segmented)

        # set black area is the background, inverse of the image and background is the biggest area
        if np.sum(segmented) < np.sum(255 - segmented):
            segmented = 255 - segmented

        # Get image file path
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        # print("ground_truth:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        # print("ground_truth_array:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "adaptive"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "adaptive"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        counter += 1

        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()


def perform_otsu_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # count Preprocessing objects
    preprocessing_count = preprocessings.count()
    # print("preprocessing_count:", preprocessing_count)
    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform otsu segmentation on the image
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        block_size = 11
        constant = 2

        # Convert the image to grayscale
        img_file = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        segmented = np.zeros_like(img_file)

        # Otsu's thresholding
        _, thresholded_image = cv2.threshold(
            img_file, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Remove small black areas
        contours, _ = cv2.findContours(
            thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        min_area_threshold = 100
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= min_area_threshold:
                cv2.drawContours(
                    segmented, [contour], -1, (255, 255, 255), thickness=cv2.FILLED
                )

        # Combine the original image with the edges image
        segmented = cv2.bitwise_and(img_file, segmented)

        # set black area is the background, inverse of the image and background is the biggest area
        if np.sum(segmented) < np.sum(255 - segmented):
            segmented = 255 - segmented

        # Get image file path
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        # print("ground_truth:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        # print("ground_truth_array:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "otsu"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "otsu"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        counter += 1

        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()


def perform_sobel_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # Count Preprocessing objects
    preprocessing_count = preprocessings.count()
    # print("preprocessing_count:", preprocessing_count)

    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform sobel segmentation on the image
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        # Convert the image to grayscale
        img_file = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        # print("img_file shape:", img_file.shape)

        # Apply Sobel operator
        sobel_x = cv2.Sobel(img_file, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(img_file, cv2.CV_64F, 0, 1, ksize=3)

        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        gradient_magnitude = cv2.normalize(
            gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U
        )

        # Perform thresholding to obtain binary image
        _, binary_image = cv2.threshold(
            gradient_magnitude, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Apply morphological operations to enhance the result
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        binary_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)

        segmented = binary_image

        # set black area is the background, inverse of the image and background is the biggest area
        if np.sum(segmented) < np.sum(255 - segmented):
            segmented = 255 - segmented

        segmented = binary_image

        # Get image file path
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        # print("ground_truth:", ground_truth_array.shape)
        # print("segmented:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        # print("ground_truth_array:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "sobel"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "sobel"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()

        # # Save the result to /static/images/dump/
        # image_path = os.path.join("static", "images", "dump", f"sobel_{counter}.jpg")
        # cv2.imwrite(image_path, binary_image)

        counter += 1


def perform_prewitt_segmentation(image):
    # Get the associated ImagePreprocessing object
    preprocessings = ImagePreprocessing.objects.filter(image=image)

    # Count Preprocessing objects
    preprocessing_count = preprocessings.count()
    # print("preprocessing_count:", preprocessing_count)

    # Iterate over each preprocessing object
    counter = 0
    for preprocessing in preprocessings:
        # Perform prewitt segmentation on the image
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        # Convert the image to grayscale
        img_file = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        # print("img_file shape:", img_file.shape)

        # Apply Prewitt operator
        # Filter Prewitt horizontal dan vertikal
        prewitt_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
        prewitt_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)

        # Konvolusi dengan filter Prewitt
        prewitt_x_result = cv2.filter2D(img_file, -1, prewitt_x)
        prewitt_y_result = cv2.filter2D(img_file, -1, prewitt_y)

        # Menggabungkan hasil Prewitt x dan y
        prewitt_combined = cv2.addWeighted(
            cv2.convertScaleAbs(prewitt_x_result),
            0.5,
            cv2.convertScaleAbs(prewitt_y_result),
            0.5,
            0,
        )

        # Melakukan segmentasi menggunakan thresholding
        _, segmented = cv2.threshold(
            prewitt_combined, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # set black area is the background, inverse of the image and background is the biggest area
        if np.sum(segmented) < np.sum(255 - segmented):
            segmented = 255 - segmented

        # Get image file path
        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        # print("ground_truth:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        # print("ground_truth_array:", ground_truth_array.shape)
        # print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "prewitt"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "prewitt"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()

        # Save the result to /static/images/dump/
        # image_path = os.path.join("static", "images", "dump", f"prewitt_{counter}.jpg")
        # cv2.imwrite(image_path, segmented)

        counter += 1


def perform_canny_segmentation(image):
    preprocessings = ImagePreprocessing.objects.filter(image=image)
    preprocessing_count = preprocessings.count()
    # print("preprocessing_count:", preprocessing_count)
    counter = 0
    for preprocessing in preprocessings:
        img = preprocessing.image_preprocessing_gray
        img_file = cv2.imread(img.path)

        # Apply Otsu's thresholding to get optimal threshold values
        img_gray = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
        threshold_value, _ = cv2.threshold(
            img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Calculate low and high threshold values
        low_threshold = 0.5 * threshold_value
        high_threshold = 1.5 * threshold_value

        # Apply Canny edge detection
        canny_edges = cv2.Canny(
            img_gray, low_threshold, high_threshold, L2gradient=True
        )

        # Perform dilation on the edges
        kernel_size = (int(img_file.shape[0] / 100), int(img_file.shape[1] / 100))
        kernel = np.ones(kernel_size, np.uint8)
        dilated_edges = cv2.dilate(canny_edges, kernel, iterations=1)

        # Perform erosion on the dilated edges
        eroded_edges = cv2.erode(dilated_edges, kernel, iterations=1)

        # Perform segmentation using the edges
        segmented = cv2.bitwise_and(dilated_edges, eroded_edges)

        # set black area as the background, inverse the image, and make the background the biggest area
        if np.sum(segmented) < np.sum(255 - segmented):
            segmented = 255 - segmented

        # Calculate the area of the image
        total_pixels = segmented.size
        white_pixels = np.sum(segmented == 255)
        white_area_ratio = white_pixels / total_pixels

        # If the white area ratio is greater than 95%, adjust the threshold values and perform Canny segmentation again
        if white_area_ratio > 0.97:
            # print("white_area_ratio:", white_area_ratio)
            low_threshold = 0.25 * threshold_value
            high_threshold = 1.75 * threshold_value

            canny_edges = cv2.Canny(
                img_gray, low_threshold, high_threshold, L2gradient=True
            )

            dilated_edges = cv2.dilate(canny_edges, kernel, iterations=1)
            eroded_edges = cv2.erode(dilated_edges, kernel, iterations=1)
            segmented = cv2.bitwise_and(dilated_edges, eroded_edges)

            if np.sum(segmented) < np.sum(255 - segmented):
                segmented = 255 - segmented

        ground_truth_path = preprocessing.image_ground_truth.path

        # Muat gambar sebagai array numerik
        ground_truth = cv2.imread(ground_truth_path)
        ground_truth_array = np.array(ground_truth)
        segmented_array = np.zeros((segmented.shape[0], segmented.shape[1], 3))
        segmented_array = np.array(segmented_array)

        # #print("ground_truth:", ground_truth_array.shape)
        # #print("segmented:", segmented_array.shape)
        # Flatten array of images
        ground_truth_array = ground_truth_array.flatten()
        segmented_array = segmented_array.flatten()

        # #print("ground_truth_array:", ground_truth_array.shape)
        # #print("segmented_array:", segmented_array.shape)

        # Call the calculate_scores function
        type = "canny"
        average = "binary"
        zero_division = 1
        scores = calculate_scores(
            ground_truth_array, segmented_array, type, average, zero_division
        )

        # Perform dilation on the segmented image to enhance the edges

        # Set the white pixels in the segmented image to have a higher intensity value
        segmented = cv2.bitwise_and(img_gray, segmented)
        segmented[segmented == 255] = 255

        # save to model Segmentation()
        # Create a new Segmentation object
        segmentation_instance = Segmentation()
        segmentation_instance.image_preprocessing = preprocessing
        segmentation_instance.segmentation_type = "canny"

        segmented_image = PILImage.fromarray(segmented)
        segmented_stream = io.BytesIO()
        segmented_image.save(segmented_stream, format="JPEG")
        segmented_stream.seek(0)

        # Set the segmented image
        segmentation_instance.image_segmented.save(
            str(counter) + "_" + uuid.uuid4().hex + ".jpg",
            ContentFile(segmented_stream.getvalue()),
            save=False,
        )
        # Set the scores
        segmentation_instance.f1_score = scores["f1_score"]
        segmentation_instance.accuracy = scores["accuracy"]
        segmentation_instance.precision = scores["precision"]
        segmentation_instance.recall = scores["recall"]
        segmentation_instance.rand_score = scores["rand_score"]
        segmentation_instance.jaccard_score = scores["jaccard_score"]
        segmentation_instance.mse = scores["mse"]
        segmentation_instance.psnr = scores["psnr"]
        segmentation_instance.mae = scores["mae"]
        segmentation_instance.rmse = scores["rmse"]

        # Save the Segmentation object
        segmentation_instance.save()

        # # Save the result to /static/images/dump/
        # image_path = os.path.join("static", "images", "dump", f"canny_{counter}.jpg")
        # cv2.imwrite(image_path, segmented)

        counter += 1
