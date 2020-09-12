from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .forms import Order, OrderForm
from bag.contexts import bag_contents
from products.models import Product
from .models import OrderItem
import stripe


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'street_address': request.POST['street_address'],
            'post_code': request.POST['post_code'],
            'town_or_city': request.POST['town_or_city'],
            'country': request.POST['country'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()

            for item_id, item_data in bag.items():
                try:
                    product = get_object_or_404(Product, pk=item_id)
                    if isinstance(item_data, int):
                        order_item = OrderItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_item.save()
                    else:
                        for (flavour, quantity) in (
                                item_data['items_by_flavour'].items()):

                            order_item = OrderItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_flavour=flavour,
                            )
                            order_item.save()

                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products you were trying to \
                            buy was not found. "
                        "Please contact us for assistance."
                    ))
                    order.delete()
                    return redirect(reverse('view_bag'))

            request.session['save_delivery'] = 'save_delivery'
            return redirect(reverse('checkout_success',
                                    args=[order.order_number]))

        else:
            messages.error(request, "There was an error with your form. \
                Please double check your information.")

    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "There's nothing in your bag at \
                the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing.')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    save_delivery = request.session.get('save_delivery')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully made! \
        Your order number is {order_number}. A confirmation \
            email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)