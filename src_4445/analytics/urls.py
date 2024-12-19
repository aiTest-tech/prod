
from django.urls import path
from .views import *

urlpatterns = [
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]