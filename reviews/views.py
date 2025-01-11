from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import HttpResponseForbidden
from django.db.models import Avg
from .models import Product, Review
from .forms import ProductForm, ReviewForm

def product_list(request):
    products = Product.objects.all()
    products_with_reviews = []

    for product in products:
        reviews = product.reviews.filter(is_moderated=True)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        products_with_reviews.append({
            'product': product,
            'has_reviews': reviews.exists(),
            'avg_rating': round(avg_rating, 1),
        })

    return render(request, 'reviews/product_list.html', {'products_with_reviews': products_with_reviews})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'reviews/product_detail.html', {'product': product})

@login_required
@permission_required('reviews.add_product', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'reviews/product_form.html', {'form': form})

@login_required
@permission_required('reviews.change_product', raise_exception=True)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'reviews/product_form.html', {'form': form})

@login_required
@permission_required('reviews.delete_product', raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_list')

def review_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product, is_moderated=True)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    return render(request, 'reviews/review_list.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': round(average_rating, 1)
    })

@login_required
def review_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.product = product
            review.save()
            return redirect('review_list', product_id=product_id)
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'product': product})

@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user == review.author or request.user.has_perm('reviews.change_review'):
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('review_list', product_id=review.product.id)
        else:
            form = ReviewForm(instance=review)
        return render(request, 'reviews/review_form.html', {'form': form, 'product': review.product})
    else:
        return HttpResponseForbidden()

@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user == review.author or request.user.has_perm('reviews.delete_review'):
        review.delete()
        return redirect('review_list', product_id=review.product.id)
    else:
        return HttpResponseForbidden()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    user_reviews = request.user.review_set.all()
    return render(request, 'accounts/profile.html', {'user': request.user, 'reviews': user_reviews})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=request.user.pk)
    else:
        form = UserCreationForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})

@user_passes_test(lambda u: u.groups.filter(name='Модераторы').exists())
def unmoderated_reviews(request):
    reviews = Review.objects.filter(is_moderated=False).order_by('-updated_at')
    return render(request, 'reviews/unmoderated_reviews.html', {'reviews': reviews})
