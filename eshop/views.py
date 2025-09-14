from django.shortcuts import render,redirect
from .models import Categories,Product,Order,OrderItem,Contact
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from mastercart import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt

import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from os.path import basename


from django.core.files.storage import FileSystemStorage
client = razorpay.Client(auth=(settings.RAORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRECT))


# Create your views here.

def index(request):
    return render(request,"eshop/index.html")

def custom_error_view(request, exception=None):
    status_code = getattr(exception, 'status_code', 500)
    context = {
        'status_code': status_code,
    }
    return render(request, 'eshop/error-page.html', context, status=status_code)

# def contact(request):
#     return render(request,"eshop/contact.html")

def blog(request):
    return render(request,"eshop/blog.html")

def search(request):
    category = Categories.objects.all()
    product = Product.objects.all()
    query = request.GET.get('query')
    print("query :",query)
    product = Product.objects.filter(name__icontains = query)

    context={
        'category':category,
        'product':product
    }
    return render(request,"eshop/search.html",context)

def Product_Detail(request):
    product = Product.objects.all()
    context={
       'product':product
    }
    return render(request,"eshop/product-details.html",context)


def shop(request):

    category = Categories.objects.all()
    product = Product.objects.all()
    catagoryid = request.GET.get('catagory')
    prodid = request.GET.get('productid')
    print("product is =",prodid)

    if catagoryid:
        product = Product.objects.filter(subCategary_id = catagoryid)
    else:
        product = Product.objects.all()

    context={
        'category':category,
        'product':product
    }

    if prodid:
        selected_product = Product.objects.filter(id = prodid)
        prod_img = Product.objects.filter(id=prodid).first()  # Retrieve the first instance

        matching_products = related_product(prod_img)
        context={
            'category':category,
            'product':product,
            'selected_product':selected_product,
            'matching_products':matching_products

        }
        return render(request,'eshop/product-details.html',context)
    else:
        product = Product.objects.all()

    return render(request,'eshop/shop.html',context)

def usersingup(request):
    if request.method=='POST':
        
        first_name = request.POST.get('Firstname')
        last_name = request.POST.get('Lastname')
        uname = request.POST.get('Username')
        upass = request.POST.get('Password')
        email = request.POST.get('Email')
        print(uname,upass,email)

        new_user = User.objects.create_user(uname,email,upass)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        
        # return redirect('userlogin')

    return render(request,"eshop/demo.html")

def userlogin(request):
    if request.method=='POST':
        username = request.POST.get('Username')
        upass1 = request.POST.get('Password')
        
        user = authenticate(request,username=username,password=upass1)
        if user is not None:
            login(request,user)
            return redirect('shop')
        else:
            return redirect('userlogin')

    return render(request,"eshop/demo.html")


def userlogout(request):
    logout(request)
    return redirect('shop')


def checkout(request):
    amount_str = request.POST.get('amount')
    amount_float = float(amount_str)
    amount = int(amount_float)

    payment = client.order.create({
        "amount":amount,
        "currency":"INR",
        "payment_capture":"1"
    })

    order_id = payment['id']

    context ={
        'order_id':order_id, 
        'payment':payment,
    }
    print(payment)


    return render(request,'cart/checkout.html',context)


def placeOrder(request):
    if request.method=='POST':
        uid = request.session.get('_auth_user_id')
        user = User.objects.get(id=uid)       
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        amount = request.POST.get('amount')
        order_id = request.POST.get('order_id')
        payment = request.POST.get('payment')
        
        cart = request.session.get('cart')
        # print(order_id,payment,user,firstname,lastname,address,city,zipcode,phone,email,amount)
        print(cart)

        order = Order(
            user = user,
            firstname = firstname,
            lastname =  lastname,
            address = address,
            city =  city,
            zipcode = zipcode,
            phone = phone,
            email = email,
            amount = amount,
            payment_id = order_id
        )
        order.save()
        context = {
            'order_id' : order_id
        }

        for i in cart:

            qunt = cart[i]['quantity']
            prs = (int(cart[i]['price']))
            total = qunt * prs
            print(total)

            item = OrderItem(
                Order = order,
                product =cart[i]['name'],
                image = cart[i]['image'],
                quantity = cart[i]['quantity'],
                price = cart[i]['price'],
                total = total
            )

            item.save()

          

    return render(request,'cart/placeorder.html',context)


@csrf_exempt
def success(request):
    if request.method == "POST":
        a = request.POST
        order_id = ""
        
        for key,val in a.items():
            if key == 'razorpay_order_id':
                order_id = val
                break

        user = Order.objects.filter(payment_id = order_id).first()
        user.paid = True
        user.save()
    return render(request,'cart/thank-you.html')

    # ?**********************

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        con_no = request.POST.get('contact_no')
        msg = request.POST.get('message')

        print("name == ", name,email,con_no,msg)
        con = Contact(
            name = name,
            email = email,
            contact_no = con_no,
            message = msg

        )
        con.save()
    return render(request,'eshop/contact.html')

    
@login_required(login_url="/eshop/login/")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("shop")


@login_required(login_url="/eshop/login/")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/eshop/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/eshop/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/eshop/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/eshop/login/")
def cart_detail(request):
    return render(request, 'cart/cart_detail.html')




# Load ResNet50 model
resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# Function to extract features from an image using ResNet50
def extract_features(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = resnet_model.predict(img_array)
    return features

# Function to search for related images
def search_related_images(query_image_path, images_directory):
    # Extract features from the query image
    query_image_features = extract_features(query_image_path)

    # Load features of all images in the directory
    image_features = []
    image_paths = []
    for filename in os.listdir(images_directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(images_directory, filename)
            img_features = extract_features(img_path)
            image_features.append(img_features)
            image_paths.append(img_path)

    image_features = np.array(image_features)
    
    # Compute cosine similarity between query image and all images
    cosine_similarities = cosine_similarity(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))
    euclidean_dists = euclidean_distances(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))

    # Combine cosine similarity and Euclidean distance using a weighted sum
    similarity_scores = 0.7 * cosine_similarities + 0.3 * (1 - euclidean_dists / np.max(euclidean_dists))

    # Sort indices in descending order of similarity
    sorted_indices = np.argsort(similarity_scores.ravel())[::-1]

    # Get paths of top related images
    related_images = [image_paths[i] for i in sorted_indices[:5]]
    return related_images

def image_search(request):

    category = Categories.objects.all()
    context = {}

    if request.method == "POST" and request.FILES["query_image"]:
        query_image = request.FILES["query_image"]
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "searched-image"))
        filename = fs.save(query_image.name, query_image)
        query_image_path = os.path.join(settings.MEDIA_ROOT, "searched-image", filename)
        
        images_directory = os.path.join(settings.MEDIA_ROOT, "cart/image")

        # Call the image search function
        related_images = search_related_images(query_image_path, images_directory)

        matching_products = []
        for image_path in related_images:
            image_name = basename(image_path)
            product = Product.objects.filter(image__contains=image_name).first()
            if product:
                matching_products.append(product)

        context = {
            'category': category,
            'matching_products' : matching_products

        }
        return render(request, "eshop/imga.html", context)

    return render(request, "eshop/imgq.html")

def related_product(prod_img):
    query_image = prod_img.image
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "searched-image"))
    filename = fs.save(query_image.name, query_image)
    query_image_path = os.path.join(settings.MEDIA_ROOT, "searched-image", filename)
    
    images_directory = os.path.join(settings.MEDIA_ROOT, "cart/image")

    # Call the image search function
    related_images = search_related_images(query_image_path, images_directory)

    matching_products = []
    for image_path in related_images:
        image_name = basename(image_path)
        product = Product.objects.filter(image__contains=image_name).first()
        if product:
            matching_products.append(product)

    return matching_products



