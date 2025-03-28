from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from ShopSphere.models import Page
from ShopSphere.models import Category
from ShopSphere.forms import CategoryForm
from django.shortcuts import redirect
from ShopSphere.forms import PageForm
from django.urls import reverse
from ShopSphere.forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

from .models import Product, Cart, CartItem
from .cart import Cart

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    product_list = Product.objects.all()

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    context_dict['products'] = product_list
    
    response = render(request, 'ShopSphere/index.html', context=context_dict)
    return response


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'ShopSphere/product_detail.html', {'product': product})

def cart_detail(request):
   """View the cart"""
   cart = Cart(request)
   return render(request, 'ShopSphere/cart_detail.html', {'cart': cart})

def add_to_cart(request, product_id):
   """Add a product to the cart"""
   product = get_object_or_404(Product, id=product_id)
   cart = Cart(request)
   cart.add(product)
   return redirect('ShopSphere:cart_detail')

def remove_from_cart(request, product_id):
   """Remove product from the cart"""
   product = get_object_or_404(Product, id=product_id)
   cart = Cart(request)
   cart.remove(product)
   return redirect('ShopSphere:cart_detail')

def clear_cart(request):
   """Clear all items from the cart"""
   cart = Cart(request)
   cart.clear()
   return redirect('ShopSphere:cart_detail')

def about(request):
    return render(request, 'ShopSphere/about.html')

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the client.
    return render(request, 'ShopSphere/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
        # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect('/ShopSphere/')
        else:
            # The supplied form contained errors -
            # just print them to the terminal.
            print(form.errors)
            # Will handle the bad form, new form, or no form supplied cases.
            # Render the form with error messages (if any).
    return render(request, 'ShopSphere/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/ShopSphere/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('ShopSphere:show_category',
                                kwargs={'category_name_slug':
                                category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'ShopSphere/add_page.html', context=context_dict)

def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
    # Attempt to grab information from the raw form information.
    # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
        # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
           
    # Update our variable to indicate that the template
    # registration was successful.
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
    

    # Render the template depending on the context.
    return render(request,
            'ShopSphere/register.html',
            context = {'user_form': user_form,
                        'registered': registered})

def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
        # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('ShopSphere:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your ShopSphere account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
            # The request is not a HTTP POST, so display the login form.

    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'ShopSphere/login.html')

@login_required
def recommended(request):
    return render(request, 'ShopSphere/recommended.html')

# Use the login_required() decorator to ensure only those logged in can
# access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('ShopSphere:index'))
