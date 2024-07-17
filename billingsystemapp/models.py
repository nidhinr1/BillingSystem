from django.db import models
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    purchase_date = models.DateField()

    def __str__(self):
        return str(self.customer_name)

class Sales(models.Model):
    sales_id = models.AutoField(primary_key=True)
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return str(self.sales_id)
    
class Billing(models.Model):
    id = models.AutoField(primary_key=True)
    sale_number=models.IntegerField(null=True)
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.id)

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username

