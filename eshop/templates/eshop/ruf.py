# views.py# views.py
import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from os.path import basename


# Function to extract features from an image
def extract_features(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    print("fethures :",img_array)
    return img_array

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

    image_features = np.array(image_features).reshape(len(image_features), -1)
    print("img fetures",image_features)
    # Compute cosine similarity between query image and all images
    similarities = cosine_similarity(query_image_features.reshape(1, -1), image_features)
    sorted_indices = np.argsort(similarities[0])[::-1]  # Sort indices in descending order of similarity

    # Get paths of top related images
    related_images = [image_paths[i] for i in sorted_indices]
    print("realated images:",related_images)
    return related_images

# Update the image_search view
# Update the image_search view

# def image_search(request):
    
#     if request.method == "POST" and request.FILES["query_image"]:
#         query_image = request.FILES["query_image"]
#         fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "cart\image"))  # Specify the location
#         filename = fs.save(query_image.name, query_image)  # Use the original filename
#         query_image_path = os.path.join(settings.MEDIA_ROOT, "cart\image", filename)  # Construct the file path
        
#         # Define the directory where images are stored
#         images_directory = os.path.join(settings.MEDIA_ROOT, "cart\image")

#         # Call the image search function
#         related_images = search_related_images(query_image_path, images_directory)

#         print("Related images:", related_images)  # Debugging statement

#         # Get top 5 related products based on image search
#         related_products = related_images[0:5]
#         print("Related products:", related_products[0])  # Debugging statement


#         context={
#             "related_products": related_products
#         }
#         return render(request, "eshop/imga.html",context)

#     return render(request, "eshop/imgq.html")

from django.db.models import Q

def image_search(request):
    context = {}

    if request.method == "POST" and request.FILES["query_image"]:
        products = Product.objects.all()
        matching_products = []

        query_image = request.FILES["query_image"]
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "searched-image"))
        filename = fs.save(query_image.name, query_image)
        query_image_path = os.path.join(settings.MEDIA_ROOT, "cart/image", filename)
        
        images_directory = os.path.join(settings.MEDIA_ROOT, "cart/image")

        # Call the image search function
        related_images = search_related_images(query_image_path, images_directory)
        print("**related Images",related_images)

        related_images_name=[]
        count =0 
        for i in related_images:
            if(count<5):
                name=os.path.basename(i)
                related_images_name.append(name)
                count += 1
        print("***Name: ",related_images_name)

        for prod in products:
            prod_image_name = basename(prod.image.path)
            print("588/*/*/prod image name",prod_image_name)
            for i in related_images_name:

                if i == prod_image_name:
                    print("000000product :",prod)
                    matching_products.append(prod)

        print("//*//*matching product ",matching_products)
            
        print("relatedproduct",related_products)
        
        context['matching_products'] = matching_products

        return render(request, "eshop/imga.html", context)

    return render(request, "eshop/imgq.html")





    {% comment %} ***  second method {% endcomment %}



    import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Product
from os.path import basename

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

    # Get paths of top related images with similarity less than 6
    threshold = 6
    filtered_indices = [i for i in sorted_indices if similarity_scores.ravel()[i] < threshold]
    related_images = [image_paths[i] for i in filtered_indices[:5]]  # Take only top 5 images

    return related_images

def image_search(request):
    context = {}

    if request.method == "POST" and request.FILES.get("query_image"):
        query_image = request.FILES["query_image"]
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "searched-image"))
        filename = fs.save(query_image.name, query_image)
        query_image_path = os.path.join(settings.MEDIA_ROOT, "cart/image", filename)
        
        images_directory = os.path.join(settings.MEDIA_ROOT, "cart/image")

        # Call the image search function
        related_images = search_related_images(query_image_path, images_directory)

        # Limit the number of related images to 6 or less
        related_images = related_images[:6]

        matching_products = []
        if related_images:
            for image_path in related_images:
                image_name = basename(image_path)
                # Filter products only if the image name is found in the database
                product = Product.objects.filter(image__contains=image_name).first()
                if product:
                    matching_products.append(product)
        else:
            context['message'] = "No related images found."

        context['matching_products'] = matching_products

        return render(request, "eshop/imga.html", context)

    return render(request, "eshop/imgq.html")
















    
# def search_related_images(query_image_path, images_directory):
#     # Extract features from the query image
#     query_image_features = extract_features(query_image_path)

#     # Load features of all images in the directory
#     image_features = []
#     image_paths = []
#     for filename in os.listdir(images_directory):
#         if filename.endswith(".jpg") or filename.endswith(".png"):
#             img_path = os.path.join(images_directory, filename)
#             img_features = extract_features(img_path)
#             image_features.append(img_features)
#             image_paths.append(img_path)

#     image_features = np.array(image_features)
    
#     # Compute cosine similarity between query image and all images
#     cosine_similarities = cosine_similarity(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))
#     euclidean_dists = euclidean_distances(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))

#     # Combine cosine similarity and Euclidean distance using a weighted sum
#     similarity_scores = 0.7 * cosine_similarities + 0.3 * (1 - euclidean_dists / np.max(euclidean_dists))

#     # Find the indices of top 5 images with highest similarity scores and lowest Euclidean distances
#     top_indices = np.argsort(similarity_scores.ravel())[::-1][:5]

#     # Get paths of top related images
#     related_images = [image_paths[i] for i in top_indices]
#     return related_images


# import os
# import numpy as np
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
# from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# from .models import Product
# from os.path import basename

# # Load ResNet50 model
# resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# # Function to extract features from an image using ResNet50
# def extract_features(image_path):
#     img = image.load_img(image_path, target_size=(224, 224))
#     img_array = image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#     img_array = preprocess_input(img_array)
#     features = resnet_model.predict(img_array)
#     return features

# # Function to search for related images
# def search_related_images(query_image_path, images_directory):
#     # Extract features from the query image
#     query_image_features = extract_features(query_image_path)

#     # Load features of all images in the directory
#     image_features = []
#     image_paths = []
#     for filename in os.listdir(images_directory):
#         if filename.endswith(".jpg") or filename.endswith(".png"):
#             img_path = os.path.join(images_directory, filename)
#             img_features = extract_features(img_path)
#             image_features.append(img_features)
#             image_paths.append(img_path)

#     image_features = np.array(image_features)
    
#     # Compute cosine similarity between query image and all images
#     cosine_similarities = cosine_similarity(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))
#     euclidean_dists = euclidean_distances(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))

#     # Combine cosine similarity and Euclidean distance using a weighted sum
#     similarity_scores = 0.7 * cosine_similarities + 0.3 * (1 - euclidean_dists / np.max(euclidean_dists))

#     # Sort indices in descending order of similarity
#     sorted_indices = np.argsort(similarity_scores.ravel())[::-1]

#     # Get paths of top related images with similarity less than 6
#     threshold = 6
#     filtered_indices = [i for i in sorted_indices if similarity_scores.ravel()[i] < threshold]
#     related_images = [image_paths[i] for i in filtered_indices[:5]]  # Take only top 5 images

#     return related_images



# from django.http import HttpResponseServerError
# from django.shortcuts import render
# import os
# import numpy as np
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
# from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# from .models import Product
# from os.path import basename

# # Load ResNet50 model
# resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# # Function to extract features from an image using ResNet50
# def extract_features(image_path):
#     img = image.load_img(image_path, target_size=(224, 224))
#     img_array = image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#     img_array = preprocess_input(img_array)
#     features = resnet_model.predict(img_array)
#     return features

# # Function to search for related images
# def search_related_images(query_image_path, images_directory):
#     # Extract features from the query image
#     query_image_features = extract_features(query_image_path)

#     # Load features of all images in the directory
#     image_features = []
#     image_paths = []
#     for filename in os.listdir(images_directory):
#         if filename.endswith(".jpg") or filename.endswith(".png"):
#             img_path = os.path.join(images_directory, filename)
#             img_features = extract_features(img_path)
#             image_features.append(img_features)
#             image_paths.append(img_path)

#     image_features = np.array(image_features)
    
#     # Compute cosine similarity between query image and all images
#     cosine_similarities = cosine_similarity(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))
#     euclidean_dists = euclidean_distances(query_image_features.reshape(1, -1), image_features.reshape(len(image_features), -1))

#     # Combine cosine similarity and Euclidean distance using a weighted sum
#     similarity_scores = 0.7 * cosine_similarities + 0.3 * (1 - euclidean_dists / np.max(euclidean_dists))

#     # Sort indices in descending order of similarity
#     sorted_indices = np.argsort(similarity_scores.ravel())[::-1]

#     # Get paths of top related images with similarity less than 6
#     threshold = 6
#     filtered_indices = [i for i in sorted_indices if similarity_scores.ravel()[i] < threshold]
#     related_images = [image_paths[i] for i in filtered_indices[:5]]  # Take only top 5 images

#     return related_images

# def image_search(request):
#     context = {}

#     if request.method == "POST" and request.FILES.get("query_image"):
#         query_image = request.FILES["query_image"]
#         fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "\searched-image"))
#         filename = fs.save(query_image.name, query_image)
#         query_image_path = os.path.join(settings.MEDIA_ROOT, "\searched-image", filename)
        
#         images_directory = os.path.join(settings.MEDIA_ROOT, "cart/image")

#         try:
#             # Call the image search function
#             related_images = search_related_images(query_image_path, images_directory)
#         except FileNotFoundError:
#             return HttpResponseServerError("Uploaded image not found. Please try again.")

#         # Limit the number of related images to 6 or less
#         related_images = related_images[:6]

#         matching_products = []
#         if related_images:
#             for image_path in related_images:
#                 image_name = basename(image_path)
#                 # Filter products only if the image name is found in the database
#                 product = Product.objects.filter(image__contains=image_name).first()
#                 if product:
#                     matching_products.append(product)
#             if not matching_products:
#                 context['message'] = "No matching products found for the uploaded image."
#         else:
#             context['message'] = "No related images found."

#         context['matching_products'] = matching_products

#         return render(request, "eshop/imga.html", context)

#     return render(request, "eshop/imgq.html")









<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <!-- image_search.html -->
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <input type="file" name="query_image" accept="image/*">
        <button type="submit">Search</button>
    </form>


    
    {% if related_products %}
    {% for product in related_products %}
        <div>
            <img src="{{ product.image.url }}" alt="{{ product.name }}">
            <h3>{{ product.name }}</h3>
            <p>{{ product.desc }}</p>
        </div>
    {% endfor %}
    {% else %}
        <p>No related products found.</p>
    {% endif %}

    
</body>
</html>