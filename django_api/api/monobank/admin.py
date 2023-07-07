from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    Category,
    CategoryMSO,
    Currency,
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


class MonoTransactionModelAdmin(admin.ModelAdmin):
    list_display = ["id", "time", "amount", "description", "balance"]

    class Meta:
        model = MonoTransaction


admin.site.register(MonoTransaction, MonoTransactionModelAdmin)

# admin.site.register(MonoCardTransaction)
# admin.site.register(MonoJarTransaction)
