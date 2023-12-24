from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response

from customers.models import Customer
from customers.serializers import CustomerSerializer

# Function-based view for listing all customers
@csrf_exempt
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return JsonResponse(serializer.data, safe=False)

# Function-based view for creating a new customer
@csrf_exempt
def customer_create(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Function-based view for retrieving, updating, or deleting a specific customer
@csrf_exempt
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = CustomerSerializer(customer, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        customer.delete()
        return JsonResponse({'message': 'Customer deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
