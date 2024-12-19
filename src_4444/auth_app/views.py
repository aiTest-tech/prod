from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .serializers import RegisterSerializer, LoginSerializer, RefreshTokenSerializer, CaptchaGenerateSerializer, CaptchaValidateSerializer
from cryptography.fernet import Fernet
import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from .models import *
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
import hashlib

SECRET_KEY = b'FCLKZFCzV7p3i42jJIjEvFxqhem9pJJZgBdYrny17a8='
cipher = Fernet(SECRET_KEY)

# Adjusted RegisterView to handle project assignment
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Secret key (must match with React/Node.js)
SECRET_KEY2 = "OiLzQ5i0gRnslKw6Jzp3papf58xoo6jO"

def decode_password(encoded_password):
    try:
        # Decode the JWT token
        decoded_data = jwt.decode(encoded_password, SECRET_KEY2, algorithms=["HS256"])
        password = decoded_data.get("password")
        return {"success": True, "password": password}
    except ExpiredSignatureError:
        return {"success": False, "error": "Token has expired"}
    except InvalidTokenError:
        return {"success": False, "error": "Invalid token"}


SECRET_KEY3 = b'FCLKZFCzV7p3i42jJIjEvFxqhem9pJJZgBdYrny17a8='
cipher = Fernet(SECRET_KEY3)

# Adjusted LoginView to reflect the custom User model (using email for login)
class LoginView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request, *args, **kwargs):
        print("$$$$$$$$$$$$$$$$$$$$$$")
        print("brijesh request.data", request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # print("data from audit", request.user)
            # email = serializer.validated_data['email']
            # password = serializer.validated_data['password']
            print("brijesh ", request.POST)
            email  = request.data.get('email', '')
            password = request.data.get('password', '')
            text = request.data.get('captcha_text', '')
            en_text  = request.data.get('en_text', '') 
            
            print(email)
            print(password)
            print(text)
            print(en_text)

            decrypted_text = cipher.decrypt(en_text.encode()).decode()
            if decrypted_text != text:
                print("###########")
                return JsonResponse({"status": "fail", "message": "Validation failed"})
            # else:
            print("###########2222222222222222222")

            print("YYYYYYYYYYYYYY", password)
            print(">>>>>>>>>>>>>>>")
            result = decode_password(password)
            print(">>>>>>>>",result)
            print(">>>>>>>>>>>>>>>")
            if result["success"]:
                # print("$$$$$$$$$$$$")
                # print("Decoded Password:", result["password"])
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", result["password"])
                password = result["password"]


            user = get_user_model().objects.filter(email=email).first()
            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     permission_classes = [AllowAny]
#     throttle_classes = [AnonRateThrottle]

#     @swagger_auto_schema(request_body=LoginSerializer)
#     def post(self, request, *args, **kwargs):
#         print("Request Data:", request.data)
#         serializer = LoginSerializer(data=request.data)

#         if serializer.is_valid():
#             # Extract fields from request
#             email = request.data.get('email', '')
#             hashed_password = request.data.get('password', '')
#             captcha_text = request.data.get('captcha_text', '')
#             encrypted_captcha_text = request.data.get('en_text', '')

#             # Validate CAPTCHA
#             try:
#                 decrypted_captcha_text = cipher.decrypt(encrypted_captcha_text.encode()).decode()
#                 if decrypted_captcha_text != captcha_text:
#                     return JsonResponse({"status": "fail", "message": "CAPTCHA validation failed."}, status=400)
#             except Exception as e:
#                 return JsonResponse({"status": "fail", "message": "CAPTCHA decryption error."}, status=400)

#             # Find user by email
#             user = get_user_model().objects.filter(email=email).first()
#             if not user:
#                 return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

#             # Hash the database password using SHA-512
#             db_hashed_password = hashlib.sha512(user.password.encode()).hexdigest()

#             # Compare the hashes
#             if db_hashed_password == hashed_password:
#                 # Generate JWT tokens
#                 refresh = RefreshToken.for_user(user)
#                 return Response({
#                     'access': str(refresh.access_token),
#                     'refresh': str(refresh),
#                 })
#             else:
#                 return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom token refresh view, no changes needed, works with JWT
class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RefreshTokenSerializer)
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh']
            try:
                token = RefreshToken(refresh_token)
                new_access_token = str(token.access_token)
                return Response({'access': new_access_token})
            except Exception:
                return Response({"detail": "Invalid refresh token or expired."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Handle CAPTCHA generation (no changes necessary based on models)
@method_decorator(csrf_exempt, name='dispatch')
class GenerateCaptchaView(View):
    def post(self, request):
        serializer = CaptchaGenerateSerializer(data=request.POST)
        if serializer.is_valid():
            text_length = serializer.validated_data['text_length']
            width = serializer.validated_data['width']
            height = serializer.validated_data['height']
            font_size = serializer.validated_data['font_size']

            text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=text_length))

            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)

            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2

            draw.text((text_x, text_y), text, font=font, fill='black')

            for _ in range(10):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                draw.line(((x1, y1), (x2, y2)), fill="orange", width=1)

            for _ in range(100):
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.point((x, y), fill="orange")

            output_dir = "captchas"
            os.makedirs(output_dir, exist_ok=True)

            existing_files = os.listdir(output_dir)
            next_file_number = len(existing_files) + 1
            file_name = f"{next_file_number}.png"
            file_path = os.path.join(output_dir, file_name)

            image.save(file_path)

            encrypted_text = cipher.encrypt(text.encode()).decode()

            return JsonResponse({"image_path": file_path, "encrypted_text": encrypted_text})

# Handle CAPTCHA validation (no changes necessary based on models)
@method_decorator(csrf_exempt, name='dispatch')
class ValidateCaptchaView(View):
    def post(self, request):
        serializer = CaptchaValidateSerializer(data=request.POST)
        if serializer.is_valid():
            encrypted_text = serializer.validated_data['encrypted_text']
            user_input = serializer.validated_data['user_input']

            try:
                decrypted_text = cipher.decrypt(encrypted_text.encode()).decode()

                if decrypted_text == user_input:
                    return JsonResponse({"status": "success", "message": "Validation successful"})
                else:
                    return JsonResponse({"status": "fail", "message": "Validation failed"})
            except Exception as e:
                return JsonResponse({"status": "fail", "message": "Invalid encrypted_text or decryption failed", "error": str(e)}, status=400)
        return JsonResponse({"status": "fail", "message": "Invalid data"}, status=400)

from wtc.models import WTC  # Import your existing model

def project_summary(request):
    total_rec = WTC.objects.count()  # Get the total count of records
    return JsonResponse({'wtc': total_rec})  # Return as JSON response