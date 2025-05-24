from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Weather API",
        default_version='v1',
        description="API documentation for Weather project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="azimjonovislomjon77@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('weather.api_urls')),
    path('', include('weather.urls', namespace='weather')),
    path('users/', include('users.urls', namespace='users')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-docs'),
]