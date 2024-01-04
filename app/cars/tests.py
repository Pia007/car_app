from django.test import TestCase
from django.urls import reverse
import pytest
from cars.models import Car

# Create your tests here.
#Unit Test
def test_homepage_access():
    url = reverse('home')
    assert url == "/"

def test_car_list_access():
    url = reverse('car_list')
    assert url == "/cars/"

def test_car_detail_access():
    url = reverse('car_detail', args=[1])
    assert url == "/cars/1/"

def test_car_new_access():
    url = reverse('car_new')
    assert url == "/cars/new/"




