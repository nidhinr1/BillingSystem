from django.db import models,IntegrityError
import uuid
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    manufacturingdate = models.DateField(null=True)
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
    sale_number = models.UUIDField(default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchasetime = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('sale_number', 'product_id')
    def __str__(self):
        return str(self.sale_number)


