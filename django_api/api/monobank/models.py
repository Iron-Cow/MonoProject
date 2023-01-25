from django.db import models


class Currency(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=16)
    flag = models.CharField(max_length=4, default=None, null=True, blank=True)
    symbol = models.CharField(max_length=4, default=None, null=True, blank=True)

    def __str__(self):
        return f'{self.name} {self.flag}'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    symbol = models.CharField(max_length=4, default=None, blank=True, null=True)
    user_defined = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.symbol or ''}"

    @classmethod
    def create_custom_category(cls, name, symbol="🤝", *args, **kwargs):
        if cls.objects.filter(name=name).exists():
            raise ValueError("Category Exists")
        category = Category(name=name, symbol=symbol, user_defined=True)
        category.save()
        mso = CategoryMSO(category=category, mso=999000 + category.id)
        mso.save()
        return category


class CategoryMSO(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    mso = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.mso} ({self.category.name})"

