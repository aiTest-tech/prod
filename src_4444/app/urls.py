from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("speech-to-text2/", ProcessAudioView.as_view(), name="process_audio"),
    path("speech-to-text-base-input/", ProcessAudioViewBase64Input.as_view(), name="process_audio"),
    path("submit-audio/", SubmitAudioView.as_view(), name=""),
    path("show/", FetchAllAudioRecordsView.as_view(), name="show"),
    path('generate/', GenerateCaptchaView.as_view(), name='text-data'),
    path('validate/', ValidateCaptchaView.as_view(), name='text-data'),
] 