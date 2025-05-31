# deployer/serializers.py
from rest_framework import serializers
from .models import DjangoProject,ReactProject

class DjangoProjectSerializer(serializers.ModelSerializer):
    pem_file = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = DjangoProject
        fields = '__all__'



class ReactProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReactProject
        fields = '__all__'
