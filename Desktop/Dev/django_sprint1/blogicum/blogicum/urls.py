from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),  # маршруты блога
    path('pages/', include('pages.urls')),  # маршруты страниц
]
