from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUpClassView.as_view(), name="signup"),
    path("signout/", views.SignOutClassView.as_view(), name="signout"),
    path("signin/", views.SignInClassView.as_view(), name="signin"),
    path(
        "segmentation/summary/",
        views.SegmentationSummaryClassView.as_view(),
        name="segmentation_summary",
    ),
    path(
        "segmentation/delete/<int:pk>/",
        views.SegmentationDeleteClassView.as_view(),
        name="segmentation_delete",
    ),
    path(
        "segmentation/detail/<int:pk>/",
        views.SegmentationDetailClassView.as_view(),
        name="segmentation_detail",
    ),
    path("segmentation/", views.SegmentationClassView.as_view(), name="segmentation"),
    path("setting/", views.SettingClassView.as_view(), name="setting"),
    path(
        "report/summary/", views.ReportSummaryClassView.as_view(), name="report_summary"
    ),
    path(
        "report/segmentation/",
        views.ReportSegmentationClassView.as_view(),
        name="report_segmentation",
    ),
    path(
        "report/export/report/",
        views.ReportExportReportClassView.as_view(),
        name="report_export_report",
    ),
    path(
        "report/export/image/<int:pk>/",
        views.ReportExportImageClassView.as_view(),
        name="report_export_image",
    ),
    path("report/", views.ReportClassView.as_view(), name="report"),
    path(
        "preference/setting/",
        views.PreferenceSettingClassView.as_view(),
        name="preference_setting",
    ),
    path("preference/", views.PreferenceClassView.as_view(), name="preference"),
    path(
        "manage/user/reset-password/<int:pk>/",
        views.ManageUserResetPasswordClassView.as_view(),
        name="manage_user_reset_password",
    ),
    path(
        "manage/user/group/edit/<int:pk>/",
        views.ManageUserGroupEditClassView.as_view(),
        name="manage_user_group_edit",
    ),
    path(
        "manage/user/edit/<int:pk>/",
        views.ManageUserEditClassView.as_view(),
        name="manage_user_edit",
    ),
    path(
        "manage/user/detail/<int:pk>/",
        views.ManageUserDetailClassView.as_view(),
        name="manage_user_detail",
    ),
    path(
        "manage/user/delete/<int:pk>/",
        views.ManageUserDeleteClassView.as_view(),
        name="manage_user_delete",
    ),
    path(
        "manage/user/add/",
        views.ManageUserAddClassView.as_view(),
        name="manage_user_add",
    ),
    path("manage/user/", views.ManageUsersClassView.as_view(), name="manage_user"),
    path(
        "image/uploader/<str:uploader>/",
        views.ImageUploaderView.as_view(),
        name="image_uploader",
    ),
    path("image/upload/", views.ImageUploadView.as_view(), name="image_upload"),
    path(
        "image/update/<int:pk>/", views.ImageUpdateView.as_view(), name="image_update"
    ),
    path("image/summary/", views.ImageSummaryView.as_view(), name="image_summary"),
    path(
        "image/table/color/",
        views.ImageTableColorClassView.as_view(),
        name="image_table_color",
    ),
    path(
        "image/graph/color/",
        views.ImageGraphColorClassView.as_view(),
        name="image_graph_color",
    ),
    path("image/graph/", views.ImageGraphClassView.as_view(), name="image_graph"),
    path(
        "image/delete/<int:pk>/", views.ImageDeleteView.as_view(), name="image_delete"
    ),
    path(
        "image/detail/<int:pk>/", views.ImageDetailView.as_view(), name="image_detail"
    ),
    path("image/", views.ImageListView.as_view(), name="image_list"),
    path("help/", views.HelpClassView.as_view(), name="help"),
    path("docs/", views.DocsClassView.as_view(), name="docs"),
    path("dashboard/", views.DashboardClassView.as_view(), name="dashboard"),
    path("contact/", views.ContactClassView.as_view(), name="contact"),
    path("blog/", views.BlogClassView.as_view(), name="blog"),
    path(
        "account/profile/",
        views.AccountProfileClassView.as_view(),
        name="account_profile",
    ),
    path(
        "account/<str:username>/update/",
        views.AccountUpdateClassView.as_view(),
        name="account_update",
    ),
    path(
        "account/<str:username>/change-password/",
        views.AccountChangePasswordClassView.as_view(),
        name="account_change_password",
    ),
    path("account/<str:username>/", views.AccountClassView.as_view(), name="account"),
    path("about/", views.AboutClassView.as_view(), name="about"),
    path("", views.IndexClassView.as_view(), name="index"),
]
