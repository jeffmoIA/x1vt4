from django.shortcuts import render, get_object_or_404
from .models import Producto, Categoria, Marca

def products_list(request):
    # Obtener todos los productos disponibles
    products = Producto.objects.filter(available=True)

    return render(request, 'catalogo/products_list.html', {'products': products})

def product_detail(request, product_id):
    # Obtener un producto específico por su ID
    product = get_object_or_404(Producto, id=product_id, available=True)

    return render(request, 'catalogo/product_detail.html', {'product': product})

def products_by_category(request, category_id):
    # Obtener la categoría o devolver un 404 si no existe
    category = get_object_or_404(Categoria, id=category_id)

    # Obtener todos los productos de esa categoría
    products = Producto.objects.filter(category=category, available=True)

    return render(request, 'catalogo/products_list.html', {'category': category, 'products': products})

def products_by_brand(request, brand_id):
    # Obtener la marca o devolver un 404 si no existe
    brand = get_object_or_404(Marca, id=brand_id)

    # Obtener todos los productos de esa marca
    products = Producto.objects.filter(brand=brand, available=True)

    return render(request, 'catalogo/products_list.html', {'brand': brand, 'products': products})