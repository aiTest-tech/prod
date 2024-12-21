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