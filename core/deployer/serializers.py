# deployer/serializers.py
from rest_framework import serializers
from .models import DjangoProject

class DjangoProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjangoProject
        fields = '__all__'
