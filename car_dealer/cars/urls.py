from django.urls import path
from cars import views as cars_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', cars_views.index.as_view(), name='home'),
    path('api/cars/', cars_views.car_list),
    path('api/cars/<int:pk>/', cars_views.car_detail),
    path('api/cars/sold/', cars_views.car_list_sold),
    path('api/cars/notsold/', cars_views.car_list_not_sold),
    # path('api/cars/<int:pk>/sold/', cars_views.car_detail_sold),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)