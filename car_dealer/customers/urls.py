from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_new'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_detail, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_detail, name='customer_delete'),
]
