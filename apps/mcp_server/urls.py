from django.urls import path

from . import views

urlpatterns = [
    path("mcp", views.mcp_view, name="mcp"),
]
