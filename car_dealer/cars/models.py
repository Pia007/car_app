from django.db import models

# Create your models here.
class Car(models.Model):
    make = models.CharField(max_length=50, blank=False, null=False)
    model = models.CharField(max_length=50, blank=False, null=False)
    year = models.IntegerField(blank=False, null=False)
    color = models.CharField(max_length=20, blank=False, null=False)
    price = models.IntegerField(blank=False, null=False)
    mileage = models.IntegerField( blank=True, null=True)
    sold = models.BooleanField(default=False)
    date_sold = models.DateField(blank=True, null=True)
    salespeople = models.ManyToManyField('salespeople.Salespeople', blank=True, related_name='cars_sold_by') 




    def __str__(self):
        return f'{self.year} {self.make} {self.model}'