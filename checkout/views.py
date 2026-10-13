from django.shortcuts import render, redirect
from django.contrib import messages
import db

POINTS_PER_DOLLAR = 10
POINTS_PER_REDEMPTION = 100
DOLLARS_PER_REDEMPTION = 1


def _get_cart(request):
    """Cart lives in the session as {item_id: {'qty': int, 'name': str, 'price': float}}."""
    return request.session.setdefault('cart', {})


def _cart_total(cart):
    return round(sum(v['qty'] * v['price'] for v in cart.values()), 2)


def menu_view(request):
    """Show all menu items. Entry point."""
    items = db.get_menu_items()
    cart = _get_cart(request)
    return render(request, 'checkout/menu.html', {
        'items': items,
        'cart_count': sum(v['qty'] for v in cart.values()),
        'cart_total': _cart_total(cart),
    })


def add_to_cart(request, item_id):
    """Add one item to the session cart."""
    items = db.get_menu_items()
    item = next((i for i in items if i['itemId'] == item_id), None)
    if not item:
        messages.error(request, "Item not found.")
        return redirect('menu')

    cart = _get_cart(request)
    key = str(item_id)
    if key in cart:
        cart[key]['qty'] += 1
    else:
        cart[key] = {
            'qty': 1,
            'name': item['name'],
            'price': float(item['price']),
        }
    request.session.modified = True
    return redirect('menu')


def cart_view(request):
    """Show cart and let customer adjust quantities."""
    if request.method == 'POST':
        cart = _get_cart(request)
        for key in list(cart.keys()):
            new_qty = int(request.POST.get(f'qty_{key}', cart[key]['qty']))
            if new_qty <= 0:
                del cart[key]
            else:
                cart[key]['qty'] = new_qty
        request.session.modified = True
        return redirect('cart')

    cart = _get_cart(request)
    return render(request, 'checkout/cart.html', {
        'cart': cart,
        'cart_total': _cart_total(cart),
    })


def rewards_login(request):
    """Look up a customer by email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        customer = db.get_customer_by_email(email)
        if customer:
            request.session['customer'] = {
                'customerId': customer['customerId'],
                'fullName': customer['fullName'],
                'pointsBalance': customer['pointsBalance'],
            }
            messages.success(request, f"Welcome back, {customer['fullName']}!")
        else:
            messages.error(request, "Email not found. You can still check out as a guest.")
            request.session.pop('customer', None)
        return redirect('menu')

    return render(request, 'checkout/rewards.html')


def checkout_view(request):
    """Create order, add items, record payment, calculate points."""
    cart = _get_cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('menu')

    customer = request.session.get('customer')
    customer_id = customer['customerId'] if customer else None
    total = _cart_total(cart)

    order_id = db.create_order(customer_id)
    if not order_id:
        messages.error(request, "Could not create order. Please try again.")
        return redirect('cart')

    for item_id_str, info in cart.items():
        db.add_order_item(
            order_id=order_id,
            item_id=int(item_id_str),
            quantity=info['qty'],
            price=info['price'],
        )

    db.record_payment(order_id, total, 'Card')

    points_earned = int(total * POINTS_PER_DOLLAR)

    new_balance = None
    if customer:
        new_balance = customer['pointsBalance'] + points_earned

    request.session['last_order'] = {
        'order_id': order_id,
        'items': list(cart.values()),
        'total': total,
        'points_earned': points_earned,
        'customer_name': customer['fullName'] if customer else 'Guest',
        'new_balance': new_balance,
    }
    request.session['cart'] = {}
    request.session.modified = True

    return redirect('confirmation', order_id=order_id)


def confirmation_view(request, order_id):
    """Show the order summary."""
    last = request.session.get('last_order', {})
    return render(request, 'checkout/confirmation.html', {
        'order_id': order_id,
        'items': last.get('items', []),
        'total': last.get('total', 0),
        'points_earned': last.get('points_earned', 0),
        'customer_name': last.get('customer_name', 'Guest'),
        'new_balance': last.get('new_balance'),
    })
def logout_view(request):
    """Log out the rewards customer (clear session customer, keep cart)."""
    request.session.pop('customer', None)
    messages.success(request, "You've been logged out of rewards.")
    return redirect('menu')