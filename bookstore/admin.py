from django.contrib import admin
from .models import Books, Category, UserInventory, ChargeTokens, BookOrders
# Register your models here.


@admin.register(Books)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(UserInventory)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(ChargeTokens)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(BookOrders)
class AuthorAdmin(admin.ModelAdmin):
    pass