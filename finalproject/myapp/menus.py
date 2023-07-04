def set_user_menus(request, context):
    # get username from request
    username = request.user.username
    if request.user.groups.filter(name="it_admin").exists():
        context["menus"] = it_admin_menus
    if request.user.groups.filter(name="staff").exists():
        context["menus"] = staff_menus
    if request.user.groups.filter(name="researcher").exists():
        context["menus"] = researcher_menus

    # change context['menus'] submenus url for imageUploader
    # change context['menus'] submenus url for account_detail
    for menu in context["menus"]:
        if menu["name"] == "Images":
            for submenu in menu["submenus"]:
                if submenu["name"] == "Image by Uploader":
                    submenu["url"] = "/image/uploader/" + username + "/"
        if menu["name"] == "Account":
            for submenu in menu["submenus"]:
                if submenu["name"] == "Account Profile":
                    submenu["url"] = "/account/" + username + "/"
                if submenu["name"] == "Change Password":
                    submenu["url"] = "/account/" + username + "/change-password/"


def create_menu(name, url, icon, dropdown=False, id="", submenus=None):
    menu = {"name": name, "url": url, "icon": icon, "dropdown": dropdown, "id": id}
    if submenus:
        menu["submenus"] = submenus
    return menu


menus = []

# Membuat menu untuk it_admin_menus
it_admin_menus = [
    create_menu("Dashboard", "/dashboard/", "fas fa-tachometer-alt", id="dashboard"),
    create_menu(
        "Images",
        "",
        "fas fa-image",
        dropdown=True,
        id="image",
        submenus=[
            create_menu("Image Upload", "/image/upload/", "fas fa-upload", id="upload"),
            create_menu("Image All", "/image/", "fas fa-list", id="image_all"),
            create_menu(
                "Image Summary",
                "/image/summary/",
                "fas fa-chart-bar",
                id="image_summary",
            ),
        ],
    ),
    create_menu(
        "Segmentation",
        "",
        "fas fa-chart-pie",
        dropdown=True,
        id="segmentation",
        submenus=[
            create_menu(
                "Do Segmentation", "/segmentation/", "fas fa-play", id="segmentation"
            ),
            create_menu(
                "Segmentation by Color",
                "/image/graph/color/",
                "fas fa-palette",
                id="color",
            ),
            create_menu(
                "Segmentation Table",
                "/image/table/color/",
                "fas fa-table",
                id="table",
            ),
            create_menu(
                "Segmentation Summary",
                "/segmentation/summary/",
                "fas fa-chart-bar",
                id="segmentation_summary",
            ),
        ],
    ),
]

# Membuat menu untuk staff_menus
staff_menus = []
for menu in it_admin_menus:
    if (
        menu["name"] != "Images"
        and menu["name"] != "Reports"
        and menu["name"] != "Manage"
    ):
        staff_menus.append(menu)

# Membuat menu untuk researcher
researcher_menus = []
for menu in it_admin_menus:
    if menu["name"] != "Manage":
        researcher_menus.append(menu)
