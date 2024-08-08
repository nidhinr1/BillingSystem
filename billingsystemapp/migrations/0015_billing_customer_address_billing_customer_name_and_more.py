# Generated by Django 5.0.7 on 2024-08-08 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billingsystemapp', '0014_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='customer_address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='billing',
            name='customer_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='billing',
            name='customer_phone',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='billing',
            name='payment_method',
            field=models.CharField(max_length=200, null=True),
        ),
    ]