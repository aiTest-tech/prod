from rest_framework import serializers

class ScrutinyRequestSerializer(serializers.Serializer):
    lang = serializers.CharField(required=True)
    text = serializers.CharField(required=True, max_length=1000)  # The audio transcription text
    # id = serializers.IntegerField(required=True)  # Ensure 'id' is included for ASRData lookup
