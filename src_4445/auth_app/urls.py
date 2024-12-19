from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    # path('api/hello/', HelloView.as_view(), name='hello'),
    path('refresh-token/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('generate/', GenerateCaptchaView.as_view(), name='text-data'),
    path('validate/', ValidateCaptchaView.as_view(), name='text-data'),
]



