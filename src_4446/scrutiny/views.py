from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ScrutinyRecord, Data
from .serializers import ScrutinyRequestSerializer
from app.models import User, Project
from deep_translator import GoogleTranslator
from .utils import predict_department, load_combined_model
from drf_yasg.utils import swagger_auto_schema
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
import os
import re
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Load status model and tokenizer
status_model_path = "/home/cmoai/modell/lstm_message_classifier.h5"
status_tokenizer_path = "/home/cmoai/modell/tokenizer.json"

status_model = load_model(status_model_path)

# Load status tokenizer
def load_tokenizer(tokenizer_path):
    with open(tokenizer_path, "r") as f:
        tokenizer_data = f.read()
    return tokenizer_from_json(tokenizer_data)

status_tokenizer = load_tokenizer(status_tokenizer_path)

# Helper function to clean text for LSTM prediction
def clean_text(text):
    text = str(text)
    text = re.sub(r'[^a-zA-Z\u0A80-\u0AFF\s]', '', text)  # Remove special characters
    return text.lower()

# Helper function to prepare texts for LSTM
def prepare_texts_for_lstm(texts, tokenizer, max_len=100):
    cleaned_texts = [clean_text(text) for text in texts]
    sequences = tokenizer.texts_to_sequences(cleaned_texts)
    return pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')

# Function to predict status using LSTM model
def predict_status_lstm(text, tokenizer, model):
    input_data = prepare_texts_for_lstm([text], tokenizer, model.input_shape[1])
    predictions = model.predict(input_data)
    return "Accept" if (predictions > 0.5).astype(int).flatten()[0] == 1 else "Reject"

# Simple dictionary for department mapping
department_dict = {
    3: "AGRICULTURE FARMERS WELFARE AND CO-OPERATION DEPARTMENT",
    4: "EDUCATION DEPARTMENT",
    5: "ENERGY AND PETRO CHEMICALS DEPARTMENT",
    6: "FINANCE DEPARTMENT",
    7: "FOOD CIVIL SUPPLIES AND CONSUMER AFFAIRS DEPARTMENT",
    8: "FOREST AND ENVIRONMENT DEPARTMENT",
    9: "GENERAL ADMINISTRATION DEPARTMENT",
    11: "HEALTH AND FAMILY WELFARE DEPARTMENT",
    12: "HOME DEPARTMENT",
    13: "INDUSTRIES AND MINES DEPARTMENT",
    14: "INFORMATION AND BROADCASTING DEPARTMENT",
    15: "LABOUR AND EMPLOYMENT DEPARTMENT",
    16: "LEGAL DEPARTMENT",
    17: "LEGISLATIVE AND PARLIAMENTARY AFFAIRS DEPARTMENT",
    18: "NARMADA WATER RESOURCES AND WATER SUPPLY DEPARTMENT",
    19: "PANCHAYATS RURAL HOUSING AND RURAL DEVELOPMENT DEPARTMENT",
    20: "PORTS AND TRANSPORT DEPARTMENT",
    21: "REVENUE DEPARTMENT",
    22: "ROADS AND BUILDING DEPARTMENT",
    23: "SCIENCE AND TECHNOLOGY DEPARTMENT",
    24: "SOCIAL JUSTICE AND EMPOWERMENT DEPARTMENT",
    25: "SPORTS YOUTH AND CULTURAL ACTIVITIES DEPARTMENT",
    26: "URBAN DEVELOPMENT AND URBAN HOUSING DEPARTMENT",
    27: "WOMEN AND CHILD DEVELOPMENT DEPARTMENT",
    28: "TRIBAL DEVELOPMENT DEPARTMENT",
    29: "CLIMATE CHANGE DEPARTMENT",
    59: "CHIEF MINISTER OFFICE DEPARTMENT"
}

class ScrutinyDepartmentRoutingView(APIView):

    @swagger_auto_schema(request_body=ScrutinyRequestSerializer)
    def post(self, request, *args, **kwargs):
        # Step 1: Validate input
        serializer = ScrutinyRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Extract the text and language data
        scr_text = request.data.get('text', '')
        scr_lang = request.data.get('lang', 'en')

        # Step 3: Translate text if necessary (only if language is 'gu' for Gujarati)
        if scr_lang == "gu":  # Assuming `gu` is Gujarati
            try:
                scr_text = GoogleTranslator(source="gu", target="en").translate(scr_text)
            except Exception as e:
                return Response({"status": "fail", "message": f"Translation failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Load the model and vectorizer for department prediction
        try:
            model, tfidf_vectorizer, rules_map = load_combined_model()
        except Exception as e:
            return Response({"status": "fail", "message": f"Model loading failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 5: Predict department(s) based on the text
        try:
            department_predictions = predict_department(scr_text, model, tfidf_vectorizer, rules_map)
        except Exception as e:
            return Response({"status": "fail", "message": f"Prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 6: Convert department predictions into department names using department_dict
        department_names = [department_dict.get(int(department), "Unknown") for department in department_predictions]
        department_names_str = ", ".join(department_names)

        # Step 7: Predict status using the LSTM model
        try:
            status_result = predict_status_lstm(scr_text, status_tokenizer, status_model)
        except Exception as e:
            return Response({"status": "fail", "message": f"Status prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 8: Create Data record (like in sentiment.views)

        user = request.user
        # Ensure a valid project is available
        project = Project.objects.filter(user=user).first()
        if not project:
            return Response(
                {"error": "No project found for this authenticated user"},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = Data.objects.create(
            audio_path="",  
            text=scr_text,
            etext=""  
        )

        scrutiny_record = ScrutinyRecord.objects.create(
            data=data,
            user=user,
            project=project,
            is_succ=False,  
            api_hit=1,  
            department=department_names_str,  
            scrutiny_decision=status_result  
        )

        scrutiny_record.is_succ = True  
        scrutiny_record.save()  

        response_data = {
            'scrutiny_decision': status_result,  
            'department': department_names_str,
            'data_id': data.id  
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
