from django.urls import path
from .views import ProductListView, AddProductView, EditProductView

urlpatterns = [
    path('productlist/', ProductListView.as_view(), name='productlist'),
    path('addproduct/', AddProductView.as_view(), name='addproduct'),
    path('editproduct/', EditProductView.as_view(), name='editproduct'),
]
