from rest_framework import serializers

class AnalyzeSerializer(serializers.Serializer):
    lang = serializers.CharField(required=True)  
    text = serializers.CharField(required=True)  

