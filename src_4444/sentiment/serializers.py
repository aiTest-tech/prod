from rest_framework import serializers

class AnalyzeSerializer(serializers.Serializer):
    lang = serializers.CharField(required=True)  
    data = serializers.CharField(required=True)  

