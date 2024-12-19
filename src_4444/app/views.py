from rest_framework.response import Response
from rest_framework import status
import random
import string
from PIL import Image, ImageDraw, ImageFont
from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
from cryptography.fernet import Fernet
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import os
import requests
# from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ASRData, Data
from .serializers import *
from django.core.files.storage import FileSystemStorage
from pydub import AudioSegment
from pydub.utils import mediainfo
from prometheus_client import Counter
from datetime import datetime, timedelta
import time
from rest_framework.parsers import JSONParser
import logging
# from django.conf import settings
from project  import  settings



# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Set the log file path to "log.txt" in the same directory
log_file_path = os.path.join(script_directory, "log.txt")

# Configure logging
logging.basicConfig(
    filename=log_file_path,  # Log file path
    filemode='a',            # Append mode; use 'w' for overwrite mode
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO      # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)


ASR_API_URL = "your_asr_api_url_here"  # Replace with actual URL
ASR_API_HEADERS = {"Authorization": "Bearer your_token_here"}

# REQUESTS = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint'])

ASR_API_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
ASR_API_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": os.getenv("BHASHINI_AUTHORIZATION")
}

class ProcessAudioView(APIView):
    parser_classes = [MultiPartParser]
    permissison_classes = [IsAuthenticated]  # Ensuring only authenticated users can access this view

    # def dispatch(self, request, *args, **kwargs):
    #     # Increment the counter for each request
    #     REQUESTS.labels(method=request.method, endpoint=request.path).inc()
    #     return super().dispatch(request, *args, **kwargs)

    # print(requests.headers)

    @swagger_auto_schema(request_body=ASRDataSerializer)
    def post(self, request):
        start_time = datetime.now()

        # print("111111111111 ", start_time)
        serializer = ASRDataSerializer(data=request.data)

        # Validate incoming data
        if not serializer.is_valid():
            missing_fields = []

            if 'file' not in request.FILES:
                missing_fields.append('file')
            if 'lang' not in request.data:
                missing_fields.append('lang')

            return Response(
                {"errors": serializer.errors, "missing_fields": missing_fields},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = serializer.validated_data['file']
        lang = serializer.validated_data['lang']

        # Save the audio file to the server
        fs = FileSystemStorage(location='audio_files/')
        filename = fs.save(file.name, file)
        audio_path = fs.path(filename)  # Get the full path to the file

        # Calculate duration in minutes
        try:
            audio = AudioSegment.from_file(audio_path)
            duration_in_minutes = len(audio) / 60000.0  # Convert milliseconds to minutes
        except Exception as e:
            return Response(
                {"error": "Failed to calculate audio duration", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Convert audio file to base64 for the API request
        with open(audio_path, "rb") as f:
            base64_audio = base64.b64encode(f.read()).decode('utf-8')

        service_id = (
            "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4"
            if lang != "en"
            else "ai4bharat/whisper-medium-en--gpu--t4"
        )

        payload = {
            "pipelineTasks": [{
                "taskType": "asr",  
                "config": {
                    "preProcessors": ["vad"],  
                    "language": {"sourceLanguage": lang},  
                    "serviceId": service_id,  
                    "audioFormat": "wav",  
                    "samplingRate": 16000,
                    "postProcessors": ["punctuation"],

                },
            }],
            "inputData": {
                "audio": [{"audioContent": base64_audio}],  
            },
        }

        # user = request.user
        # # Ensure a valid project is available
        # project = Project.objects.filter(user=user).first()
        # if not project:
        #     return Response(
        #         {"error": "No project found for this authenticated user"},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )

        # asr_data.user = 1
        # asr_data.project = 1

        # Call the ASR API
        start_time = time.time()
        print("222222222",start_time )
        response = requests.post(ASR_API_URL, headers=ASR_API_HEADERS, data=json.dumps(payload))



        end_time =   time.time()
        print("3333333",end_time-start_time )
        # Create the Data object and ASRData entry
        data = Data.objects.create(
            audio_path=audio_path,
            text='',  # Initially empty text, will be populated later if successful
            etext=''  # Translation can be added here if needed
        )

        # Create the ASRData record
        user_instance = User.objects.get(id=1)
        proj_inst = Project.objects.get(id=1)
        asr_data = ASRData.objects.create(
            data=data,
            user= user_instance,
            project= proj_inst,  # Ensure this is not None
            min=round(duration_in_minutes * 60, 2),  # Convert duration to seconds for storage
            is_succ=False,  # Default to False until we check the response
            api_hit=1  # First hit
        )

        # Process the API response
        is_succ = response.status_code == 200
        source_text = ""
        if is_succ:
            try:
                asr_data.is_succ = True
                response_data = response.json()
                source_text = response_data['pipelineResponse'][0]['output'][0]['source']
                asr_data.save()  # Mark as successful
            except (KeyError, IndexError, ValueError) as e:
                is_succ = False

        # Update Data object with source text if successful
        data.text = source_text if is_succ else ''
        data.save()

        if not is_succ:
            return Response(
                {"error": "Failed to process audio", "details": response.text},
                status=response.status_code,
            )

        return Response(
            {"text": source_text, "id": data.id, "duration_in_minutes": round(duration_in_minutes, 2)},
            status=status.HTTP_200_OK,
        )

class SubmitAudioView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=SubmitAudioSerializer)
    def post(self, request):

        serializer = SubmitAudioSerializer(data=request.data)

        # Validate the input data
        if not serializer.is_valid():
            return Response(
                {"status": "fail", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        record_id = serializer.validated_data['id']
        text = serializer.validated_data['text']


        print("$$$$$$$$$$$$$$$$$$$$$$$$$$")

        try:
            # Retrieve the ASRData record by its ID
            record = Data.objects.get(id=record_id)

            # Update the record with the new text (edit_source) and sentiment analysis status
            record.etext = text  # Assuming the text is linked to a Data instance
            # record.is_succ = False  # Sentiment analysis status, to be updated later
            # record.api_hit += 1  # Increment the API hit count
            record.save()

            return Response(
                {"status": "success", "message": "Record updated successfully"},
                status=status.HTTP_200_OK,
            )

        except ASRData.DoesNotExist:
            return Response(
                {"status": "fail", "message": "Record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class FetchAllAudioRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all ASRData records with required fields
        records = ASRData.objects.values(
            'id', 'data__text', 'is_succ', 'api_hit', 'created_at', 'updated_at'
        )

        total_count = ASRData.objects.all().count()

        response_data = {
            "total_number": total_count,
            "data": list(records),
        }

        return JsonResponse(
            response_data, safe=False, status=status.HTTP_200_OK
        )
    

class ProcessAudioViewBase64Input(APIView):
    parser_classes = [JSONParser]  # Expect JSON data
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

    def post(self, request):
        logging.info("Received POST request for speech-to-text processing")
        try:
            print("speech-to-text-base-input >>>>>> speech-to-text-base-input")
            raw_payload = request.body
            print(json.loads(raw_payload))
            audio_base64 = json.loads(raw_payload).get('audio_base64')
            lang = json.loads(raw_payload).get("lang")
            print("@@@@@@@@@@@@@@@")
            print(request.data.get)

            # Validate required fields
            if not audio_base64 or not lang:
                return Response(
                    {"error": "Both 'audioBase64' and 'lang' are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Determine the service ID based on the language
            service_id = (
                "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4"
                if lang != "en"
                else "ai4bharat/whisper-medium-en--gpu--t4"
            )

            # Construct the payload
            payload = {
                "pipelineTasks": [{
                    "taskType": "asr",
                    "config": {
                        "preProcessors": ["vad"],
                        "language": {"sourceLanguage": lang},
                        "serviceId": service_id,
                        "audioFormat": "wav",
                        "samplingRate": 16000,
                        "postProcessors": ["punctuation"],
                    },
                }],
                "inputData": {
                    "audio": [{"audioContent": audio_base64}],
                },
            }

            # Call the ASR API
            logging.info("Payload sent to bhashini... ")
            response = requests.post(ASR_API_URL, headers=ASR_API_HEADERS, data=json.dumps(payload))
            logging.info("Response from  bhashini... ")
            # Process the API response
            is_succ = response.status_code == 200
            source_text = ""
            if is_succ:
                try:
                    response_data = response.json()
                    source_text = response_data['pipelineResponse'][0]['output'][0]['source']
                except (KeyError, IndexError, ValueError) as e:
                    is_succ = False

            if not is_succ:
                return Response(
                    {"error": "Failed to process audio", "details": response.text},
                    status=response.status_code,
                )
            logging.info("Received Respnded -  for speech-to-text processing")
            return Response(
                {"text": source_text},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    #  parser_classes = [JSONParser]  # Parse JSON payload
    # permission_classes = [IsAuthenticated]  # Require authentication

    # def post(self, request):
    #     print("%%%%%%%%%%%%%%%")
    #     try:
    #         # Access raw payload data (bytes)
    #         raw_payload = request.body
    #         print("Raw Payload (bytes):", raw_payload)

    #         # Decode raw payload into a string (optional, for readability)
    #         raw_payload_str = raw_payload.decode("utf-8")
    #         print("Raw Payload (string):", raw_payload_str)

    #         # Parse JSON payload if it's a JSON request
    #         parsed_payload = json.loads(raw_payload)
    #         print("Parsed JSON Payload (dict):", parsed_payload)

    #         # Loop through and print all key-value pairs in the JSON payload
    #         print("---- All Payload Data ----")
    #         for key, value in parsed_payload.items():
    #             print(f"{key}: {value}")

    #         return Response({"message": "Payload printed successfully!"}, status=status.HTTP_200_OK)

    #     except json.JSONDecodeError:
    #         return Response(
    #             {"error": "Invalid JSON payload."},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #     except Exception as e:
    #         return Response(
    #             {"error": "An unexpected error occurred.", "details": str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )

SECRET_KEY = b'FCLKZFCzV7p3i42jJIjEvFxqhem9pJJZgBdYrny17a8='
cipher = Fernet(SECRET_KEY)
# from pathlib import Path

@method_decorator(csrf_exempt, name='dispatch')
class GenerateCaptchaView(View):
    def post(self, request):
        # BASE_DIR = Path(__file__).resolve().parent.parent
        # MEDIA_URL = "media/"
        # MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  
        print(">>>>>>>>>>>>>>>>>>>>>")
        # Get parameters from the POST request or set defaults
        text_length = int(request.POST.get("text_length", 5))
        width = int(request.POST.get("width", 200))
        height = int(request.POST.get("height", 70))
        font_size = int(request.POST.get("font_size", 40))

        # Generate random text
        text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=text_length))

        # Create an image with white background
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # Load a font
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Calculate text size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # Draw the text
        draw.text((text_x, text_y), text, font=font, fill='black')

        # Add noise (lines and dots)
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

        # Ensure the directory exists
        output_dir = "captchas"
        os.makedirs(output_dir, exist_ok=True)

        # Count existing files in the directory to determine the next file name
        existing_files = os.listdir(output_dir)
        next_file_number = len(existing_files) + 1
        file_name = f"{next_file_number}.png"
        # file_path = os.path.join(output_dir, file_name)
        print("$$$$$$$$$$$$$$$$$$$")
        file_path = os.path.join(settings.MEDIA_ROOT, "captchas", file_name)
        print("@@@@@@@@@@@@@@")

        # Save the image
        image.save(file_path)
        # image.open(file_path)
        # print(settings.MEDIA_URL)
        # print(settings.MEDIA_ROOT)
        # Encrypt the text
        encrypted_text = cipher.encrypt(text.encode()).decode()
        image_url = f"{settings.MEDIA_URL}captchas/{file_name}"
        # Return JSON response
        return JsonResponse({"image_path": image_url, "encrypted_text": encrypted_text})


@method_decorator(csrf_exempt, name='dispatch')
class ValidateCaptchaView(View):
    def post(self, request):
        # Get parameters from the POST request
        encrypted_text = request.POST.get("encrypted_text")
        user_input = request.POST.get("user_input")

        if not encrypted_text or not user_input:
            return JsonResponse({"status": "fail", "message": "Both encrypted_text and user_input are required"}, status=400)

        try:
            # Decrypt the text
            decrypted_text = cipher.decrypt(encrypted_text.encode()).decode()

            # Compare the decrypted text with user input
            if decrypted_text == user_input:
                return JsonResponse({"status": "success", "message": "Validation successful"})
            else:
                return JsonResponse({"status": "fail", "message": "Validation failed"})
        except Exception as e:
            # Handle decryption errors
            return JsonResponse({"status": "fail", "message": "Invalid encrypted_text or decryption failed", "error": str(e)}, status=400)