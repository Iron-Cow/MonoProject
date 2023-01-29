from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Category, Currency, CategoryMSO, MonoAccount

User = get_user_model()

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(CategoryMSO)
admin.site.register(MonoAccount)
