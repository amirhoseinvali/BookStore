import os
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
# Create your models here.


@receiver(post_save, sender=User)
def create_user_inventory(sender, instance, created, **kwargs):
    try:
       if created:
          UserInventory.objects.create(user=instance).save()
    except Exception as err:
       print(f'Error creating user inventory!\n{err}')


def update_cover_filename(instance, filename):

    path = "images/books_cover/"
    format = instance.book_name + "_" + instance.author + '.jpg'
    return os.path.join(path + format)


def update_book_filename(instance, filename):
    path = "pdf/"
    format = instance.book_name + "_" + instance.author + '.pdf'
    return os.path.join(path + format)


class UserInventory(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    inventory = models.IntegerField(default=0 ,verbose_name="موجودی کاربر")
    class Meta:
        verbose_name = "موجودی کاربران"
        verbose_name_plural = "موجودی کاربران"

    def __str__(self):
        return "%s" % self.user


class Category(models.Model):
    category_name = models.CharField(max_length=20, verbose_name="نام دسته بندی")

    class Meta:
        verbose_name = "دسته بندی ها"
        verbose_name_plural = "دسته بندی ها"

    def __str__(self):
        return "%s" % self.category_name
    

class Books(models.Model):
    book_name = models.CharField(max_length=50, verbose_name="نام کتاب")
    author = models.CharField(max_length=30, verbose_name="نویسنده")
    isbn_code = models.CharField(max_length=25, verbose_name="شماره شابک")
    category = models.ManyToManyField(Category, verbose_name="دسته بندی")
    cover_image = models.ImageField(upload_to=update_cover_filename, default='default_cover.jpg', null=True, blank=True, verbose_name="تصویر کتاب")
    pdf_file = models.FileField(upload_to=update_book_filename, blank=True, verbose_name="فایل کتاب")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد موجود")
    price = models.PositiveIntegerField(verbose_name="قیمت کتاب")
    is_forbidden = models.BooleanField(default=False, verbose_name="کتاب ممنوعه")

    class Meta:
        verbose_name = "کتاب ها"
        verbose_name_plural = "کتاب ها"

    def __str__(self):
        return "%s" % self.book_name


class ChargeTokens(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING, verbose_name="کاربر")
    amount = models.PositiveIntegerField(verbose_name="مبلغ شارژ")
    otp_token = models.CharField(max_length=30, unique=True, verbose_name="توکن شارژ")
    created_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="زمان ساخت توکن")
    apply_time = models.DateTimeField(blank=True, null=True, verbose_name="زمان اعمال شدن توکن")
    is_used = models.BooleanField(default=False, verbose_name="توکن استفاده شده")

    class Meta:
        verbose_name = "توکن ها"
        verbose_name_plural = "توکن ها"

    def __str__(self):
        return "%s" % self.user


class BookOrders(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="کاربر")
    book = models.ForeignKey(Books,on_delete=models.CASCADE, verbose_name="کتاب")
    price = models.PositiveIntegerField(verbose_name="قیمت کتاب")
    order_time = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="زمان ثبت سفارش")
    is_canceled = models.BooleanField(default=False, verbose_name="سفارش کنسل شده")
    canceled_time = models.DateTimeField(blank=True, null=True, verbose_name="زمان کنسل شدن سفارش")

    class Meta:
        verbose_name = "سفارش ها"
        verbose_name_plural = "سفارش ها"

    def __str__(self):
        return "%s" % self.book