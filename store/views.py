from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required

# 🟢 Product Listing
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

# 🟢 Product Details
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# 🟢 Add to Cart
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('product_detail', pk=pk)

# 🟢 View Cart
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for pk, qty in cart.items():
        product = Product.objects.get(pk=pk)
        items.append({'product': product, 'quantity': qty, 'subtotal': product.price * qty})
        total += product.price * qty
    return render(request, 'store/cart.html', {'items': items, 'total': total})

# 🟢 Checkout
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')
    order = Order.objects.create(user=request.user, total=0)
    total = 0
    for pk, qty in cart.items():
        product = Product.objects.get(pk=pk)
        OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
        total += product.price * qty
    order.total = total
    order.save()
    request.session['cart'] = {}  # Clear cart
    return render(request, 'store/order_success.html', {'order': order})

# 🟢 Register User
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

# 🟢 Login User
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('product_list')
