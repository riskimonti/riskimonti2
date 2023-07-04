from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from .utils.generate import generate_unique_image_name
from django.urls import reverse


# Create your models here.
class Image(models.Model):
    id = models.AutoField(primary_key=True)
    # multiple images
    image = models.ImageField(
        upload_to="static/images/uploads/", blank=False, null=False
    )
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.IntegerField()
    channel = models.CharField(max_length=10)
    format = models.CharField(max_length=10)
    dpi = models.IntegerField()
    distance = models.IntegerField()
    COLOR_CHOICES = [
        ("red", "Red"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("yellow", "Yellow"),
        ("orange", "Orange"),
        ("purple", "Purple"),
        ("pink", "Pink"),
        ("brown", "Brown"),
        ("black", "Black"),
        ("white", "White"),
        ("dark-white", "Dark White"),
        ("gray", "Gray"),
        ("cyan", "Cyan"),
        ("magenta", "Magenta"),
        ("lime", "Lime"),
        ("olive", "Olive"),
        ("maroon", "Maroon"),
        ("navy", "Navy"),
        ("teal", "Teal"),
        ("aqua", "Aqua"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("bronze", "Bronze"),
        ("beige", "Beige"),
        ("azure", "Azure"),
        ("ivory", "Ivory"),
        ("lavender", "Lavender"),
        ("coral", "Coral"),
        ("salmon", "Salmon"),
        ("tan", "Tan"),
        ("turquoise", "Turquoise"),
        ("violet", "Violet"),
        ("indigo", "Indigo"),
        ("crimson", "Crimson"),
        ("fuchsia", "Fuchsia"),
        ("orchid", "Orchid"),
        ("plum", "Plum"),
        ("khaki", "Khaki"),
        ("chocolate", "Chocolate"),
        ("tomato", "Tomato"),
        ("wheat", "Wheat"),
        ("snow", "Snow"),
        ("seashell", "Seashell"),
        ("salmon", "Salmon"),
        ("mud-brown", "Mud Brown"),
        ("dark-mud-brown", "Dark Mud Brown"),
        ("random", "Random"),
    ]
    color = models.CharField(
        max_length=20, choices=COLOR_CHOICES, default="white", blank=False, null=False
    )
    segmented = models.BooleanField(default=False)

    # override delete method
    def delete(self, *args, **kwargs):
        # delete image
        self.image.delete(False)  # False means don't save model
        super().delete(*args, **kwargs)

    # override update method
    def update(self, *args, **kwargs):
        # # hash image name to make it unique
        # unique_name = generate_unique_image_name(self.image.name)
        # # width, height, size, channel, format, dpi, distance, color
        # self.width = self.image.width
        # self.height = self.image.height
        # self.size = self.image.size
        # # shape to get channel
        # self.format = self.image.name.split(".")[-1]
        # # get dpi from image
        # # set file format
        # self.slug = slugify(unique_name + "." + self.image.name.split(".")[-1])
        # self.image.name = unique_name + "." + self.image.name.split(".")[-1]

        super(Image, self).save(*args, **kwargs)

    # override save method
    def save(self, *args, **kwargs):
        # hash image name to make it unique
        unique_name = generate_unique_image_name(self.image.name)
        # width, height, size, channel, format, dpi, distance, color
        self.width = self.image.width
        self.height = self.image.height
        self.size = self.image.size
        # shape to get channel
        self.format = self.image.name.split(".")[-1]
        # get dpi from image
        # set file format
        self.slug = slugify(unique_name + "." + self.image.name.split(".")[-1])
        self.image.name = unique_name + "." + self.image.name.split(".")[-1]
        super(Image, self).save(*args, **kwargs)

    def get_absolute_url(self, *args, **kwargs):
        return reverse("myapp:image_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return "{}. {}".format(self.id, self.uploader.username)


class ImagePreprocessing(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    image_preprocessing_gray = models.ImageField(
        upload_to="static/images/preprocessing/gray/",
        blank=False,
        null=False,
        default="/static/images/preprocessing/gray/gray.jpg",
    )
    image_preprocessing_color = models.ImageField(
        upload_to="static/images/preprocessing/color/",
        blank=False,
        null=False,
        default="/static/images/preprocessing/color/color.jpg",
    )
    image_ground_truth = models.ImageField(
        upload_to="static/images/ground_truth/", blank=False, null=False
    )
    # column to store image preprocessing parameters
    # preprocessing
    # 1. resize
    resize = models.BooleanField(default=False)
    resize_percent = models.IntegerField(blank=True, null=True)
    resize_width = models.IntegerField(blank=True, null=True)
    resize_height = models.IntegerField(blank=True, null=True)
    # 2. brightness
    brightness = models.BooleanField(default=False)
    brightness_percent = models.IntegerField(blank=True, null=True)
    # 3. contrast
    contrast = models.BooleanField(default=False)
    contrast_percent = models.IntegerField(blank=True, null=True)
    # 4. spartial filtering
    mean_filter = models.BooleanField(default=False)
    mean_filter_size = models.IntegerField(blank=True, null=True)
    median_filter = models.BooleanField(default=False)
    median_filter_size = models.IntegerField(blank=True, null=True)
    gaussian_filter = models.BooleanField(default=False)
    gaussian_filter_size = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # override delete method
    def delete(self, *args, **kwargs):
        # delete image
        self.image_preprocessing_gray.delete(False)
        self.image_preprocessing_color.delete(False)
        self.image_ground_truth.delete(False)

        # Delete the ImagePreprocessing object
        super().delete(*args, **kwargs)

    def __str__(self):
        return "{}. {}".format(
            self.id,
            self.image.uploader.username,
            self.image.image.name,
        )


class Segmentation(models.Model):
    id = models.AutoField(primary_key=True)
    image_preprocessing = models.ForeignKey(
        "ImagePreprocessing", on_delete=models.CASCADE, related_name="segmentations"
    )
    image_segmented = models.ImageField(
        upload_to="static/images/segmented/", blank=False, null=False
    )
    # additional fields
    segmentation_type = models.CharField(max_length=255, blank=True, null=True)
    # other fields related to segmentation
    f1_score = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)
    precision = models.FloatField(blank=True, null=True)
    recall = models.FloatField(blank=True, null=True)
    rand_score = models.FloatField(blank=True, null=True)
    jaccard_score = models.FloatField(blank=True, null=True)
    mse = models.FloatField(blank=True, null=True)
    psnr = models.FloatField(blank=True, null=True)
    mae = models.FloatField(blank=True, null=True)
    rmse = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # override delete method
    def delete(self, *args, **kwargs):
        # delete image
        self.image_segmented.delete(False)

        super().delete(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.image_preprocessing.id, self.id)


class SegmentationResult(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ForeignKey(
        "Image", on_delete=models.CASCADE, related_name="segmentation_results"
    )
    segment = models.ForeignKey(
        "Segmentation",
        on_delete=models.CASCADE,
        related_name="segmentation_results",
        null=True,
    )
    preprocessing = models.ForeignKey(
        "ImagePreprocessing",
        on_delete=models.CASCADE,
        related_name="segmentation_results",
        null=True,
    )
    # additional fields
    segmentation_type = models.CharField(max_length=255, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)  # Add the rank field
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # override delete method
    def delete(self, *args, **kwargs):
        # Delete the SegmentationResult object
        super().delete(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.image.id, self.id)


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # additional fields
    profile_pic = models.ImageField(
        upload_to="static/images/profile_pics/", blank=True, null=True
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # override delete method
    def delete(self, *args, **kwargs):
        # delete image
        self.profile_pic.delete(False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return "{}. {}".format(self.id, self.user.username)
