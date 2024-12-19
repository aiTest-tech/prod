from rest_framework import serializers
from app.models import *  # Assuming AudioRecord is in your `audio` app

class ScrutinyRequestSerializer(serializers.Serializer):
    lang = serializers.CharField(required=True)
    text = serializers.CharField(required=True, max_length=1000)  # The audio transcription text
    