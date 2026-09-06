from django.urls import path

from .views import (
    dashboard,
    disagreement_list,
    disagreement_summary,
)


urlpatterns = [

    # Dashboard
    path(
        "",
        dashboard,
        name="dashboard",
    ),

    # API: all disagreements
    path(
        "disagreements/",
        disagreement_list,
        name="disagreement-list",
    ),

    # API: reconciliation summary
    path(
        "summary/",
        disagreement_summary,
        name="disagreement-summary",
    ),
]