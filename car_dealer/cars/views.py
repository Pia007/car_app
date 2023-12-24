from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from cars.models import Car
from cars.serializers import CarSerializer
from rest_framework.decorators import api_view

# Create your views here.
def index(request):
    print("--------------- PIA IS HERE")
    queryset = Car.objects.all()
    return render(request, "cars/index.html", {'cars': queryset})

class index(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'cars/index.html'

    def get(self, request):
        queryset = Car.objects.all()
        return Response({'cars': queryset})
    
class list_all_cars(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'cars/car_list.html'

    def get(self, request):
        queryset = Car.objects.all()
        return Response({'cars': queryset})
        # cars = Car.objects.all()
        # serializer = CarSerializer(cars, many=True)
        # return Response(serializer.data)

@api_view(['GET', 'POST', 'DELETE'])
def car_list(request):
    if request.method == 'GET':
        cars = Car.objects.all()

        make = request.GET.get('make', None)
        if make is not None:
            cars = cars.filter(make__icontains=make)

        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)

    elif request.method == 'POST':
        car_data = JSONParser().parse(request)
        car_serializer = CarSerializer(data=car_data)
        if cars_serializer.is_valid():
            car_serializer.save()
            return JsonResponse(car_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(car_serializer.erros, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Car.objects.all().delete()
        return JsonResponse(
            {
                'message': 
                '{} Cars were deleted successfully!'.format(count[0])
            }, 
            status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'PUT', 'DELETE'])
def car_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return JsonResponse({'message': 'The car does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        car_serializer = CarSerializer(car)
        return JsonResponse(car_serializer.data)

    elif request.method == 'PUT':
        car_data = JSONParser().parse(request)
        car_serializer = CarSerializer(car, data=car_data)
        if car_serializer.is_valid():
            car_serializer.save()
            return JsonResponse(car_serializer.data)
        return JsonResponse(car_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        car.delete()
        return JsonResponse({'message': 'Car was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
def car_list_sold(request):
    cars = Car.objects.filter(sold=True)

    if request.method == 'GET':
        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)
    
@api_view(['GET'])
def car_list_not_sold(request):
    cars = Car.objects.filter(sold=False)

    if request.method == 'GET':
        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)
    
#list the cars that are the most expensive
@api_view(['GET'])
def car_list_most_expensive(request):
    cars = Car.objects.order_by('-price')[:5]

    if request.method == 'GET':
        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)
    
#list the cars that are the least expensive
@api_view(['GET'])
def car_list_least_expensive(request):
    cars = Car.objects.order_by('price')[:5]

    if request.method == 'GET':
        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)
    
#list the cars that are older
@api_view(['GET'])
def car_list_older(request):
    cars = Car.objects.order_by('-year')[:5]

    if request.method == 'GET':
        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)

#list the cars that are newer
@api_view(['GET'])
def car_list_newer(request):
    cars = Car.objects.order_by('year')[:5]

    if request.method == 'GET':
        cars_serializer = CarSerializer(cars, many=True)
        return JsonResponse(cars_serializer.data, safe=False)
