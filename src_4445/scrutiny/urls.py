from django.urls import path
from .views import ScrutinyDepartmentRoutingView

urlpatterns = [
    path('scrutiny/', ScrutinyDepartmentRoutingView.as_view(), name='scrutiny-routing'),
]
