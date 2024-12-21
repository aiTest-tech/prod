import base64
import json
import os
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
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
import os
from prometheus_client import Counter
from datetime import datetime, timedelta
import time
from rest_framework.parsers import JSONParser
import logging
import os


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
        logging.info(" RECEVIED  ---  POST request for speech-to-text processing @@@@@@@@@@@@@@@@")
        try:
            print("speech-to-text-base-input >>>>>> speech-to-text-base-input")
            raw_payload = request.body
            # print(json.loads(raw_payload))
            data_au_ba = json.loads(raw_payload)
            audio_base64 = data_au_ba.get('audio_base64')
            lang = data_au_ba.get("lang")
            # print("@@@@@@@@@@@@@@@")
            # print(request.data.get)

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

            data = Data.objects.create(
            audio_path="",
            text='',  # Initially empty text, will be populated later if successful
            etext=''  # Translation can be added here if needed
                )
            user = request.user
            # Ensure a valid project is available
            project = Project.objects.filter(user=user).first()
            if not project:
                return Response(
                    {"error": "No project found for this authenticated user"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            # print("data", data)
            # print("user", user)
            # print("project", project)
            asr_data = ASRData.objects.create(
                data=data,
                user= user,
                project= project,  # Ensure this is not None
                min=0,  # Convert duration to seconds for storage
                is_succ=False  # Default to False until we check the response
                # api_hit=""  # First hit
            )
            # asr_data.save()
            # Call the ASR API


            # logging.info("Payload sent to bhashini... ")
            # response = requests.post(ASR_API_URL, headers=ASR_API_HEADERS, data=json.dumps(payload))
            # logging.info("Response from  bhashini... ")

            max_retries = 2  # Retry once if the request fails due to timeout
            timeout = 10  # Timeout duration in seconds
            for attempt in range(max_retries + 1):
                try:
                    logging.info(f"<<<<<<<<<<<<<<<<<<<  lang >>>>>>>>>>>>>>>>>> ::  {lang}")
                    logging.info("Payload sent to bhashini... Attempt %d", attempt + 1)
                    response = requests.post(
                        ASR_API_URL, headers=ASR_API_HEADERS, data=json.dumps(payload), timeout=timeout
                    )
                    logging.info("Response received from bhashini... ")
                    break  # Exit loop if the request succeeds
                except requests.exceptions.Timeout as e:
                    logging.warning("Request timed out. Retrying... Attempt %d", attempt + 1)
                    if attempt == max_retries:
                        return Response(
                            {"error": "Request timed out after multiple attempts."},
                            status=status.HTTP_504_GATEWAY_TIMEOUT,
                        )

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
            asr_data.is_succ = True
            asr_data.save()
            logging.info(" SENT ::: POST request  To Frontend @@@@@@@@@@@@@@@@@@@@@@@@")
            return Response(
                {"text": source_text},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
