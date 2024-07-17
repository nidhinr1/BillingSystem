from . import views
from django.urls import path
urlpatterns = [
    path('addcategory/', views.addcategory, name='addcategory'),
    path('adduser/', views.adduser, name='adduser'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('addcustomer/', views.addcustomer, name='addcustomer'),
    path('billing/', views.billing, name='billing'),
    path('product/', views.product_list, name='product'),
    path('product/search/', views.product_search, name='product_search'),
    path('product/<int:product_id>/update/', views.product_update, name='product_update'),
    path('product/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('customers/<int:customer_id>/update/', views.update_customer, name='update_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    path('customers/', views.customer_list, name='customers'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user_list/', views.user_list, name='user_list'),
    path('user_list/<str:user_name>/delete/', views.user_delete, name='user_delete'),
]