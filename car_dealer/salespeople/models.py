from django.db import models

class Salespeople(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    cars_sold = models.ManyToManyField('cars.Car', blank=True, related_name='salespeople_who_sold')
    customers = models.ManyToManyField('customers.Customer', blank=True, related_name='salespeople_customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



