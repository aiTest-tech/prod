from django.urls import path
from .views import *

urlpatterns = [
    path("speech-to-text2/", ProcessAudioView.as_view(), name="process_audio"),
    path("speech-to-text-base-input/", ProcessAudioViewBase64Input.as_view(), name="process_audio"),
    path("submit-audio/", SubmitAudioView.as_view(), name=""),
    path("show/", FetchAllAudioRecordsView.as_view(), name="show"),
]   