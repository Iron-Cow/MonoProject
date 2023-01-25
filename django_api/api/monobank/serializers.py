from .models import Category
from rest_framework import serializers



class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'symbol']
        extra_kwargs = {'user_defined': {'write_only': True}}




