from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    Category,
    Currency,
    CategoryMSO,
    MonoAccount,
    MonoCard,
    MonoJar,
    MonoTransaction,
)

User = get_user_model()

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(CategoryMSO)
admin.site.register(MonoAccount)
admin.site.register(MonoCard)
admin.site.register(MonoJar)
admin.site.register(MonoTransaction)
# admin.site.register(MonoCardTransaction)
# admin.site.register(MonoJarTransaction)
