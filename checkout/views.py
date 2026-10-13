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
    cart_total = _cart_total(cart)
    discount = request.session.get('discount', 0)
    final_total = max(0, round(cart_total - discount, 2))

    return render(request, 'checkout/cart.html', {
        'cart': cart,
        'cart_total': cart_total,
        'discount': discount,
        'points_used': request.session.get('points_used', 0),
        'final_total': final_total,
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


def logout_view(request):
    """Log out the rewards customer (clear session customer, keep cart)."""
    request.session.pop('customer', None)
    messages.success(request, "You've been logged out of rewards.")
    return redirect('menu')


def redeem_points(request):
    """Let a logged-in customer apply points as a discount on the current cart."""
    customer = request.session.get('customer')
    if not customer:
        messages.error(request, "Please log in to redeem points.")
        return redirect('rewards_login')

    balance = customer.get('pointsBalance', 0)

    if request.method == 'POST':
        try:
            points = int(request.POST.get('points', 0))
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid number.")
            return redirect('redeem_points')

        if points < POINTS_PER_REDEMPTION:
            messages.error(
                request,
                f"Minimum {POINTS_PER_REDEMPTION} points required to redeem."
            )
        elif points > balance:
            messages.error(request, "You don't have enough points.")
        else:
            dollars_off = (points // POINTS_PER_REDEMPTION) * DOLLARS_PER_REDEMPTION
            request.session['discount'] = dollars_off
            request.session['points_used'] = points
            request.session.modified = True
            print(f"DEBUG: discount = {dollars_off}, points_used = {points}")
            messages.success(
                request,
                f"${dollars_off:.2f} off applied! ({points} points)"
            )

        return redirect('cart')

    context = {
        'customer': customer,
        'balance': balance,
        'points_per_redemption': POINTS_PER_REDEMPTION,
        'dollars_per_redemption': DOLLARS_PER_REDEMPTION,
        'current_discount': request.session.get('discount', 0),
        'current_points_used': request.session.get('points_used', 0),
    }
    return render(request, 'checkout/redeem.html', context)


def checkout_view(request):
    """Create order, add items, record payment, calculate points."""
    cart = _get_cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('menu')

    customer = request.session.get('customer')
    customer_id = customer['customerId'] if customer else None

    # Cart total and discount
    cart_total = _cart_total(cart)
    discount = request.session.get('discount', 0)
    points_used = request.session.get('points_used', 0)
    final_total = max(0, round(cart_total - discount, 2))

    # 1. Create order
    order_id = db.create_order(customer_id)
    if not order_id:
        messages.error(request, "Could not create order. Please try again.")
        return redirect('cart')

    # 2. Add items to the order
    for item_id_str, info in cart.items():
        db.add_order_item(
            order_id=order_id,
            item_id=int(item_id_str),
            quantity=info['qty'],
            price=info['price'],
        )

    # 3. Override order total with the discounted total
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE "Order" SET total = ? WHERE orderId = ?',
                (final_total, order_id)
            )
            conn.commit()
    except Exception as e:
        print(f"Error updating order total: {e}")

    # 4. Record payment on the discounted total
    db.record_payment(order_id, final_total, 'Card')

    # 5. Calculate points earned on the discounted total
    points_earned = int(final_total * POINTS_PER_DOLLAR)

    # 6. Update customer balance in session (DB update comes later)
    new_balance = None
    if customer:
        new_balance = customer['pointsBalance'] - points_used + points_earned
        request.session['customer']['pointsBalance'] = new_balance
        request.session.modified = True
        # Uncomment when Kaelin adds this function to db.py:
        # db.update_rewards_balance(customer_id, new_balance)

    # 7. Store confirmation info
    request.session['last_order'] = {
        'order_id': order_id,
        'items': list(cart.values()),
        'subtotal': cart_total,
        'discount': discount,
        'points_used': points_used,
        'total': final_total,
        'points_earned': points_earned,
        'customer_name': customer['fullName'] if customer else 'Guest',
        'new_balance': new_balance,
    }

    # 8. Clear cart and discount
    request.session['cart'] = {}
    request.session['discount'] = 0
    request.session['points_used'] = 0
    request.session.modified = True

    return redirect('confirmation', order_id=order_id)


def confirmation_view(request, order_id):
    """Show the order summary."""
    last = request.session.get('last_order', {})
    return render(request, 'checkout/confirmation.html', {
        'order_id': order_id,
        'items': last.get('items', []),
        'subtotal': last.get('subtotal', 0),
        'discount': last.get('discount', 0),
        'points_used': last.get('points_used', 0),
        'total': last.get('total', 0),
        'points_earned': last.get('points_earned', 0),
        'customer_name': last.get('customer_name', 'Guest'),
        'new_balance': last.get('new_balance'),
    })
