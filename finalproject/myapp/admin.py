from django.contrib import admin

# Register your models here.
from .models import (
    Image,
    UserProfile,
    ImagePreprocessing,
    Segmentation,
    SegmentationResult,
)


class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ("slug", "created_at", "updated_at")


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "user")


class ImagePreprocessingAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "image", "created_at", "updated_at")


admin.site.register(UserProfile)

admin.site.register(ImagePreprocessing)

admin.site.register(Segmentation)

admin.site.register(SegmentationResult)

admin.site.register(Image)
