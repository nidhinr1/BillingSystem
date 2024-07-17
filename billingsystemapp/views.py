from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .encoders import DecimalEncoder
import datetime


def addcategory(request):
    if request.method =='POST':
        category=request.POST['category']
        q=Category(name=category)
        q.save()
        return render(request,'addcategory.html',{'msg':'Category submitted'})
    else:
        return render(request,'addcategory.html')
    
def adduser(request):
    if request.method =='POST':
        username=request.POST['username']
        password=request.POST['password']
        if User.objects.filter(username = username).exists():
            return render(request,'adduser.html',{'msg':'username or email aready exist.'})
        else:
            q=User.objects.create_user(username=username,password=password)
            q.save()
        return render(request,'adduser.html',{'msg':'User Added'})
    else:
        return render(request,'adduser.html')

def addproduct(request):
    types=Category.objects.all().values
    if request.method =='POST':
        name=request.POST['pdtname']
        price=request.POST['pdtprice']
        stock=request.POST['pdtstock']
        category_name=request.POST['pdtcategory']    
        category = get_object_or_404(Category, name=category_name)
        q=Product(product_name=name,price=price,quantity=stock,category=category)
        q.save()
        return render(request,'addproduct.html',{'msg':'Product submitted','type':types})
    else:
        return render(request,'addproduct.html',{'type':types})

def addcustomer(request):
    if request.method == 'POST':
        customer_name = request.POST['customer_name']
        phone = request.POST['phone']
        purchase_date = request.POST['purchase_date']

        if Customer.objects.filter(customer_name=customer_name, phone=phone).exists():
            return render(request, 'addcustomers.html', {'msg': 'Customer already exists.'})
        else:
            customer = Customer(customer_name=customer_name, phone=phone, purchase_date=purchase_date)
            customer.save()
            return render(request, 'addcustomers.html', {'msg': 'Customer Added'})
    else:
        return render(request, 'addcustomers.html')
    
def billing(request):
    products = Product.objects.all()
    if request.method == 'POST':
        if 'add_product' in request.POST:
            product_id = request.POST['product_id']
            quantity = int(request.POST['quantity'])
            product = Product.objects.get(pk=product_id)
            
            cart = request.session.get('cart', {})
            if product_id in cart:
                cart[product_id]['quantity'] += quantity
            else:
                cart[product_id] = {'name': product.product_name, 'price': float(product.price), 'quantity': quantity}
            request.session['cart'] = cart

        if 'remove_product' in request.POST:
            product_id = request.POST['product_id']
            cart = request.session.get('cart', {})
            if product_id in cart:
                del cart[product_id]
            request.session['cart'] = cart

        if 'submit_bill' in request.POST:
            cart = request.session.get('cart', {})
            sale_number = int(datetime.datetime.now().timestamp())
            for product_id, item in cart.items():
                product = Product.objects.get(pk=product_id)
                Billing.objects.create(
                    sale_number=sale_number,
                    product_name=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
            request.session['cart'] = {}
            return redirect('billing')

    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    return render(request, 'billing.html', {'products': products, 'cart': cart, 'total_price': total_price})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def product_search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(product_name__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def product_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        category_id = request.POST.get('category')
        product.category = Category.objects.get(pk=category_id)
        product.save()
        return redirect('product')
    categories = Category.objects.all()
    return render(request, 'product_update.html', {'product': product, 'categories': categories})

def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product')
    return render(request, 'product_delete.html', {'product': product})

def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        customer.customer_name = request.POST.get('customer_name')
        customer.phone = request.POST.get('phone')
        customer.purchase_date = request.POST.get('purchase_date')
        customer.save()
        return redirect('customers')
    return render(request, 'customer_update.html', {'customer': customer})

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('customers')
    return render(request, 'customer_delete.html', {'customer': customer})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customers.html', {'customers': customers})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_delete.html', {'category': category})