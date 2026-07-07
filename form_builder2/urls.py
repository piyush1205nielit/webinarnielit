from django.urls import path

from . import views

app_name = "form_builder2"

urlpatterns = [
    # ---- Admin side (staff only) ----
    path("manage/", views.form_list, name="form_list"),
    path("manage/create/", views.form_create, name="form_create"),
    path("manage/<int:pk>/edit/", views.form_edit, name="form_edit"),
    path("manage/<int:pk>/delete/", views.form_delete, name="form_delete"),
    path("manage/<int:pk>/publish/", views.form_toggle_publish, name="form_toggle_publish"),
    path("manage/<int:pk>/data/", views.form_data, name="form_data"),
    path("manage/<int:pk>/export/<str:fmt>/", views.form_export, name="form_export"),
    path(
        "manage/<int:pk>/data/<int:resp_pk>/delete/",
        views.response_delete,
        name="response_delete",
    ),
    # ---- Public side ----
    path("f/<slug:slug>/", views.form_fill, name="form_fill"),
    path("f/<slug:slug>/success/", views.form_success, name="form_success"),
]