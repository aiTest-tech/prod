"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from app.views import *
from rest_framework_simplejwt.authentication import JWTAuthentication


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class Hello(APIView):
    # def get(self, request, *args, **kwargs):
    #     print(dir(request))
    #     return Response({"hii":"hello"},status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        filtered_headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    
        return JsonResponse({
            "message": "Hello, world!",
            "headers": filtered_headers,  # Include filtered headers for debugging
        })

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[JWTAuthentication],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("app.urls")),
    # path("api/", include("sentiment.urls")),
    # path("api/", include("scrutiny.urls")),
    # path("api/", include("wtc.urls")),
    # path("api/", include("analytics.urls")),
    # path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('api/auth/', include('auth_app.urls')),
    path("hello/", Hello.as_view(), name="hello")

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    path('', include('django_prometheus.urls')),
]