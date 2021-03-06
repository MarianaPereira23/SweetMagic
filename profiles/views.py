from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import ProfileForm


@login_required
def profile(request):
    """A view to display user profile"""
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. \
                                     Please double check the form.')
    else:
        form = ProfileForm(instance=profile)

    orders = profile.orders.all()

    template = "profiles/profile.html"
    context = {
        'form': form,
        'orders': orders,
    }

    return render(request, template, context)
