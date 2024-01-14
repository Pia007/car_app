from django.urls import path
from .views import HomePageView, CarListView, CarDetailView, CarCreateView, CarUpdateView, CarDeleteView, mark_car_as_not_sold

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),  # Add this line for the home page
    path('cars/', CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('cars/new/', CarCreateView.as_view(), name='car_new'),
    path('cars/<int:pk>/edit/', CarUpdateView.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', CarDeleteView.as_view(), name='car_delete'),
    path('cars/<int:car_id>/mark_not_sold/', mark_car_as_not_sold, name='mark_car_not_sold'),
]

