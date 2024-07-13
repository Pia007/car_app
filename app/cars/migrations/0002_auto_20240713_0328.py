# Generated by Django 3.2.2 on 2024-07-13 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='car',
            name='color',
        ),
        migrations.AddField(
            model_name='car',
            name='car_color',
            field=models.CharField(choices=[('Black', 'Black'), ('Blue', 'Blue'), ('Brown', 'Brown'), ('Gold', 'Gold'), ('Green', 'Green'), ('Grey', 'Grey'), ('Orange', 'Orange'), ('Red', 'Red'), ('Silver', 'Silver'), ('White', 'White')], default='Black', max_length=10),
        ),
    ]