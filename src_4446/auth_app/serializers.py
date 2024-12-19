from rest_framework import serializers
from django.contrib.auth import get_user_model

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'project', 'username']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            project=validated_data['project'],
            username=validated_data['username']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class CaptchaGenerateSerializer(serializers.Serializer):
    text_length = serializers.IntegerField(default=5)
    width = serializers.IntegerField(default=200)
    height = serializers.IntegerField(default=70)
    font_size = serializers.IntegerField(default=40)

class CaptchaValidateSerializer(serializers.Serializer):
    encrypted_text = serializers.CharField()
    user_input = serializers.CharField()
