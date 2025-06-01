# deployer/serializers.py
from rest_framework import serializers
from .models import DjangoProject,ReactProject,Instance

class DjangoProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DjangoProject
        fields = '__all__'



class ReactProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReactProject
        fields = '__all__'

class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = '__all__'
