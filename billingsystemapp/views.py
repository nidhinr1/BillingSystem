from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import authenticate, login,logout
from django.http import JsonResponse,HttpResponse,FileResponse
from datetime import datetime,timedelta
from django.contrib import messages
from django.db.models import Q,Sum
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
import io,uuid
from django.utils import timezone
from django.views.decorators.http import require_POST

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
    types = Category.objects.all().values()
    if request.method == 'POST':
        name = request.POST['pdtname']
        brand = request.POST['brand']
        price = float(request.POST['pdtprice'])
        stock_quantity = request.POST['pdtstock']
        category_name = request.POST['pdtcategory']
        manufacturing = request.POST['pdtmanu']

        category = get_object_or_404(Category, name=category_name)

        # Create Product instance
        product = Product(
            product_name=name,
            brand=brand,
            price=price,
            quantity=stock_quantity,
            category=category,
            manufacturingdate=manufacturing
        )
        product.save()

        # Create Stock instance
        stock_entry = stock(
            product_name=product,  # Link to the Product instance
            category=category,
            stock=stock_quantity,
            price = round(price * 0.95, 2)
        )
        stock_entry.save()

        return render(request, 'addproduct.html', {'msg': 'Product and Stock submitted', 'type': types})
    else:
        return render(request, 'addproduct.html', {'type': types})


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

def generate_pdf_bill(sale_number, cart, purchasetime):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{sale_number}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=72, leftMargin=72)  # Added margins
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    company_title_style = ParagraphStyle(name='CompanyTitle', fontSize=18, alignment=1)
    normal_style = styles['Normal']

    # Add company name
    company_name = "Your Company Name"
    company_title = Paragraph(company_name, company_title_style)
    elements.append(company_title)
    elements.append(Spacer(1, 12))

    # Add main title
    main_title = Paragraph("Purchase Bill", title_style)
    elements.append(main_title)
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph(f"Purchase Time: {purchasetime.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 12))

    # Table data
    data = [
        ["Product Name", "Qty", "Original Price", "Discounted Price", "Total Price"]
    ]

    for item in cart.values():
        total_price = item['discounted_price'] * item['quantity']
        data.append([item['name'], item['quantity'], f"Rs {item['original_price']}", 
                     f"Rs {item['discounted_price']}", f"Rs {total_price}"])

    final_total_price = sum(item['discounted_price'] * item['quantity'] for item in cart.values())
    data.append([])
    data.append(["", "", "", "Final Amount:", f"Rs {final_total_price}"])

    table = Table(data, colWidths=[1.5 * inch, 1.0 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])

    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),  # Increase height of each row
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Add thank you message
    thank_you_message = Paragraph("Thank you for your purchase! Have a great day!", normal_style)
    elements.append(Spacer(1, 24))
    elements.append(thank_you_message)

    doc.build(elements)

    return response

def billing(request):
    products = Product.objects.all()
    search_query = request.GET.get('search', '')

    if search_query:
        products = products.filter(Q(product_name__icontains=search_query))

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        sale_number = request.session.get('sale_number', None)

        if sale_number is None:
            sale_number = str(uuid.uuid4())
            request.session['sale_number'] = sale_number

        if 'add_product' in request.POST:
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')
            product = get_object_or_404(Product, pk=product_id)
            
            if product.quantity == 0:
                return render(request, 'billing.html', {
                    'msg': f'{product.product_name} is out of stock.',
                    'products': products,
                    'cart': cart,
                    'total_price': round_to_two_decimal_places(sum(item['discounted_price'] * item['quantity'] for item in cart.values())),
                    'search_query': search_query
                })
            
            try:
                quantity = int(quantity)
                if product_id in cart:
                    new_quantity = cart[product_id]['quantity'] + quantity
                else:
                    new_quantity = quantity
                
                if new_quantity > product.quantity:
                    return render(request, 'billing.html', {
                        'msg': f'Quantity requested for {product.product_name} exceeds stock available ({product.quantity}).',
                        'products': products,
                        'cart': cart,
                        'total_price': round_to_two_decimal_places(sum(item['discounted_price'] * item['quantity'] for item in cart.values())),
                        'search_query': search_query
                    })

                # Calculate the discounted price
                discounted_price = round_to_two_decimal_places(float(product.price) * (1 - (float(product.discount) / 100)))
                
                if product_id in cart:
                    cart[product_id]['quantity'] += quantity
                else:
                    cart[product_id] = {
                        'name': product.product_name,
                        'original_price': round_to_two_decimal_places(float(product.price)),
                        'discounted_price': discounted_price,
                        'quantity': quantity
                    }
                request.session['cart'] = cart
            except (ValueError, Product.DoesNotExist):
                pass

        if 'remove_product' in request.POST:
            product_id = request.POST.get('product_id')
            if product_id in cart:
                del cart[product_id]
            request.session['cart'] = cart

        if 'submit_bill' in request.POST:
            if cart:
                purchasetime = datetime.now()
                try:
                    for product_id, item in cart.items():
                        product = get_object_or_404(Product, pk=product_id)
                        if item['quantity'] > product.quantity:
                            error_message = f"Quantity for {product.product_name} exceeds available stock ({product.quantity})."
                            return render(request, 'billing.html', {
                                'products': products,
                                'cart': cart,
                                'total_price': round_to_two_decimal_places(sum(item['discounted_price'] * item['quantity'] for item in cart.values())),
                                'search_query': search_query,
                                'error_message': error_message
                            })

                        Billing.objects.create(
                            sale_number=sale_number,
                            product_id=product,
                            quantity=item['quantity'],
                            price=item['discounted_price'],  # Final discounted price
                            purchasetime=purchasetime
                        )
                        product.quantity -= item['quantity']
                        product.save()

                    response = generate_pdf_bill(sale_number, cart, purchasetime)
                    request.session['cart'] = {}  
                    request.session['sale_number'] = None
                    return response
                except IntegrityError:
                    error_message = "You cannot add the same product twice in the same bill."
                    return render(request, 'billing.html', {
                        'products': products,
                        'cart': cart,
                        'total_price': round_to_two_decimal_places(sum(item['discounted_price'] * item['quantity'] for item in cart.values())),
                        'search_query': search_query,
                        'error_message': error_message
                    })

    cart = request.session.get('cart', {})
    total_price = round_to_two_decimal_places(sum(item['discounted_price'] * item['quantity'] for item in cart.values()))

    return render(request, 'billing.html', {
        'products': products,
        'cart': cart,
        'total_price': total_price,
        'search_query': search_query
    })

def round_to_two_decimal_places(value):
    """Rounds a decimal value to two decimal places."""
    return round(value, 2)

def product_list(request):
    now = timezone.now().date()
    products = Product.objects.all()

    # Calculate cutoff date for new stock
    six_months_ago = now - timezone.timedelta(days=6*30)  # Approximate 6 months

    # Pass products and cutoff date to template
    return render(request, 'products.html', {
        'products': products,
        'six_months_ago': six_months_ago,
    })

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
        # Update Product details
        product.product_name = request.POST.get('product_name')
        product.brand = request.POST.get('brand')
        product.price = float(request.POST.get('price'))
        product.discount = request.POST.get('discount')
        product.quantity = request.POST.get('quantity')
        product.manufacturingdate = request.POST.get('pdtmanu')
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, pk=category_id)
        product.save()

        # Update Stock details
        stock_item = get_object_or_404(stock, product_name=product)
        stock_item.price = round(product.price * 0.95, 2)  # Sync stock price with product price
        stock_item.stock = product.quantity  # Sync stock quantity with product quantity
        stock_item.save()

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

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('billing')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  

def user_list(request):
    users = User.objects.exclude(is_superuser=True)
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_name):
    user = get_object_or_404(User, username=user_name)
    if request.method == "POST":
        user.delete()
        messages.success(request, f'User {user_name} has been deleted.')
        return redirect('user_list')
    return render(request, 'user_delete.html', {'user': user})

def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)
    else:
        products = Product.objects.all()
    
    return render(request, 'products.html', {'products': products, 'query': query})

def products_search_by_category(request):
    category_query = request.GET.get('category')
    products = []

    if category_query:
        try:
            category = Category.objects.get(name__iexact=category_query)
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            products = Product.objects.none()
    else:
        products = Product.objects.all()
        
    return render(request, 'products.html', {'products': products, 'category_query': category_query})

@require_POST
def update_discounts_view(request):
    products = Product.objects.all()
    for product in products:
        product.update_discount()
    
    return redirect('product')

def filter_products(request, stock_type):
    six_months_ago = date.today() - timedelta(days=6*30)  # Approximate 6 months

    if stock_type == 'new':
        products = Product.objects.filter(manufacturingdate__gte=six_months_ago)
    elif stock_type == 'old':
        products = Product.objects.filter(manufacturingdate__lt=six_months_ago)
    else:
        products = Product.objects.all()

    return render(request, 'products.html', {'products': products, 'stock_type': stock_type})

def sales_summary(request):
    sales = Billing.objects.all()
    total_products_sold = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_money_earned = sales.aggregate(Sum('price'))['price__sum'] or 0
    context = {
        'sales': sales,
        'total_products_sold': total_products_sold,
        'total_money_earned': total_money_earned,
    }
    return render(request, 'sales_summary.html', context)

def sales_today(request):
    today = datetime.now().date()
    sales = Billing.objects.filter(purchasetime__date=today)
    total_products_sold = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_money_earned = sales.aggregate(Sum('price'))['price__sum'] or 0
    context = {
        'sales': sales,
        'total_products_sold': total_products_sold,
        'total_money_earned': total_money_earned,
    }
    return render(request, 'sales_summary.html', context)

def sales_this_week(request):
    start_of_week = datetime.now().date() - timedelta(days=datetime.now().weekday())
    sales = Billing.objects.filter(purchasetime__date__gte=start_of_week)
    total_products_sold = sales.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_money_earned = sales.aggregate(Sum('price'))['price__sum'] or 0
    context = {
        'sales': sales,
        'total_products_sold': total_products_sold,
        'total_money_earned': total_money_earned,
    }
    return render(request, 'sales_summary.html', context)


def product_stock_view(request):
    products = Product.objects.all()
    product_details = []
    total_unsold_products = 0
    total_sold_products = 0
    total_stock = 0

    for product in products:
        try:
            stock_item = stock.objects.get(product_name=product)
            products_sold = stock_item.stock - product.quantity  # Updated calculation
            
            stock_type = 'New Stock' if product.manufacturingdate and product.manufacturingdate > timezone.now().date() - timedelta(days=180) else 'Old Stock'
            
            # Update totals
            total_unsold_products += product.quantity
            total_sold_products += products_sold
            total_stock += stock_item.stock

            product_details.append({
                'product': product,
                'stock': stock_item,
                'products_sold': products_sold,
                'stock_type': stock_type,
            })

        except stock.DoesNotExist:
            # Handle the case where no stock item exists for the product
            product_details.append({
                'product': product,
                'stock': None,  # No stock information available
                'products_sold': None,  # No products sold information available
                'stock_type': 'Unknown',  # Or any default value you prefer
            })

    context = {
        'product_details': product_details,
        'total_unsold_products': total_unsold_products,
        'total_sold_products': total_sold_products,
        'total_stock': total_stock,
    }

    return render(request, 'product_stock.html', context)



def profit_loss_view(request):
    billings = Billing.objects.select_related('product_id')
    profit_loss_details = []
    total_profit_or_loss = 0

    for billing in billings:
        stock_item = stock.objects.get(product_name=billing.product_id)
        profit_or_loss = (billing.price - stock_item.price) * billing.quantity
        total_profit_or_loss += profit_or_loss

        profit_loss_details.append({
            'product': billing.product_id,
            'billing_price': billing.price,
            'stock_price': stock_item.price,
            'profit_or_loss': profit_or_loss,
        })

    context = {
        'profit_loss_details': profit_loss_details,
        'total_profit_or_loss': total_profit_or_loss,
    }

    return render(request, 'profit_loss.html', context)

