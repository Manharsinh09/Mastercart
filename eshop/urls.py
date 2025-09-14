from django.urls import path
from . import views

urlpatterns = [
    
    path('',views.index,name="index"),
    path('index/',views.index,name="index"),
    path('shop/',views.shop,name="shop"),
    path('contact/',views.contact,name="contact"),
    path('product-detail/',views.Product_Detail,name="product-detail"),
    path('login/',views.userlogin,name="userlogin"),
    path('singup/',views.usersingup,name="usersingup"),
    path('logout/',views.userlogout,name="userlogout"),
    path('cart/placeorder/',views.placeOrder,name="placeOreder"),
    path('cart/success',views.success),
    path('search',views.search,name="search"),
    path('blog-details/',views.blog,name="blog"),


    path('image-search/',views.image_search,name="image_search"),
    # cart path
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),
    path('cart/checkout/',views.checkout,name='checkout'),


]
