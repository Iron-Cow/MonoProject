from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    Category,
    CategoryMSO,
    Currency,
    JarTransaction,
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


# admin.site.register(JarTransaction)


class MonoTransactionModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "formatted_time",
        "formatted_amount",
        "description",
        "formatted_balance",
    ]
    ordering = ["-time"]

    class Meta:
        model = MonoTransaction


admin.site.register(MonoTransaction, MonoTransactionModelAdmin)


class JarTransactionModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "owner_name",
        "jar_name",
        "formatted_time",
        "formatted_amount",
        "description",
        "formatted_balance",
    ]
    ordering = ["-time"]

    class Meta:
        model = JarTransaction


admin.site.register(JarTransaction, JarTransactionModelAdmin)
# admin.site.register(MonoCardTransaction)
# admin.site.register(MonoJarTransaction)
