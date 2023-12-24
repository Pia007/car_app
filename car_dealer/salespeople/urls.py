from django.urls import path
from .views import (
    SalespeopleListView, 
    SalespeopleDetailView, 
    SalespeopleCreateView, 
    SalespeopleUpdateView, 
    SalespeopleDeleteView
)

urlpatterns = [
    path('salespeople/', SalespeopleListView.as_view(), name='salespeople_list'),
    path('salespeople/<int:pk>/', SalespeopleDetailView.as_view(), name='salespeople_detail'),
    path('salespeople/new/', SalespeopleCreateView.as_view(), name='salespeople_new'),
    path('salespeople/<int:pk>/edit/', SalespeopleUpdateView.as_view(), name='salespeople_edit'),
    path('salespeople/<int:pk>/delete/', SalespeopleDeleteView.as_view(), name='salespeople_delete'),
]
