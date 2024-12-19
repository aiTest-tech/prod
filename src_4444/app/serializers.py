from rest_framework import serializers
from .models import *

class ASRDataSerializer(serializers.Serializer):
    file = serializers.FileField(required = True)
    lang = serializers.CharField(required = True)

class SubmitAudioSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    text = serializers.CharField(required=True)
    
