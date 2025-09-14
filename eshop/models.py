from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Categories(models.Model):
  categories_name = models.CharField(max_length=50,)

  def __str__(self):
    return self.categories_name


class SubCategories(models.Model):
  subcategories_name = models.CharField(max_length=50)
  categories = models.ForeignKey(Categories,on_delete=models.CASCADE,default='')

  def __str__(self):
    return self.subcategories_name

class Product(models.Model):
  product_id = models.AutoField
  name = models.CharField(max_length=50)
  price = models.IntegerField()
  desc = models.CharField(max_length=300)
  image = models.ImageField(upload_to=("cart/image"))
  pub_date = models.DateField(default=timezone.now)

  categary = models.ForeignKey(Categories,on_delete=models.CASCADE)
  subCategary = models.ForeignKey(SubCategories,on_delete=models.CASCADE)

  
  def __str__(self):
    return self.name
      
class Order(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  firstname = models.CharField(max_length=25)
  lastname = models.CharField(max_length=25)
  address = models.TextField(max_length=200)
  city = models.CharField(max_length=50)
  zipcode = models.IntegerField()
  phone = models.IntegerField()
  email = models.EmailField(max_length=50)
  amount = models.CharField(max_length=50)
  payment_id = models.CharField(max_length=200,null=True)
  paid = models.BooleanField(default=False,null=True)
  date = models.DateField(auto_now=True)

  def __str__(self):
    return self.user.username

class OrderItem(models.Model):
  Order = models.ForeignKey(Order,on_delete=models.CASCADE)
  product = models.CharField(max_length=200)
  image = models.ImageField(upload_to="cart/Oreder_Img")
  quantity = models.CharField(max_length=25)
  price = models.CharField(max_length=50)
  total = models.CharField(max_length=100)
  
  def __str__(self):
    return self.Order.user.username

class Contact(models.Model):
  name = models.CharField(max_length=50)
  email = models.EmailField(max_length=50)
  contact_no = models.IntegerField()
  message = models.CharField(max_length=200)

  def __str__(self):
    return self.name
