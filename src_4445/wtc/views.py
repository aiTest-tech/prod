from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import WTC
from .serializers import WTCSerializer
from drf_yasg.utils import swagger_auto_schema
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import os
import re
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import joblib
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
from rest_framework.permissions import IsAuthenticated
from auth_app.models import Project
from rest_framework.generics import ListAPIView
from .models import WTC
from .serializers import WTCSerializer_analy
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import date, timedelta
from django.db.models import Count, Q
from rest_framework.views import APIView
from .models import WTC

class RequestsPerDayView(APIView):
    def get(self, request, *args, **kwargs):
        # Group by date and count the records
        requests_per_day = (
            WTC.objects.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        return Response(requests_per_day)
    
# class WTCListViewAnaly(ListAPIView):
#     queryset = WTC.objects.all()
#     serializer_class = WTCSerializer_analy

class WTCListViewAnaly(ListAPIView):
    serializer_class = WTCSerializer_analy

    def get_queryset(self):
        return WTC.objects.all().order_by('-created_at') 

class SentimentSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        sentiment_summary = WTC.objects.values('sentiment_cal_pol').annotate(count=Count('id'))
        return Response(sentiment_summary)

class ScrutinySummaryView(APIView):
    def get(self, request, *args, **kwargs):
        sentiment_summary = WTC.objects.values('lo_sc').annotate(count=Count('id'))
        return Response(sentiment_summary)

# Configure TensorFlow to use CPU only
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Pre-load Models and Tokenizers
model_name = "/home/cmoai/Models"
tokenizer = AutoTokenizer.from_pretrained(model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(model_name)

department_model_path = "/home/cmoai/modell/department_classifier_model.pkl"
status_model_path = "/home/cmoai/modell/lstm_message_classifier.h5"
status_tokenizer_path = "/home/cmoai/modell/tokenizer.json"
vectorizer_path = "/home/cmoai/modell/tfidf_vectorizer.pkl"

# Load department routing model and TF-IDF vectorizer
department_model = joblib.load(department_model_path)
department_vectorizer = joblib.load(vectorizer_path)

# Load LSTM model and tokenizer
def load_tokenizer(tokenizer_path):
    with open(tokenizer_path, "r") as f:
        tokenizer_data = f.read()
    return tokenizer_from_json(tokenizer_data)

status_tokenizer = load_tokenizer(status_tokenizer_path)
status_model = load_model(status_model_path)

department_dict = {
    3: "AGRICULTURE, FARMERS WELFARE AND CO-OPERATION DEPARTMENT",
    4: "EDUCATION DEPARTMENT",
    5: "ENERGY AND PETRO CHEMICALS DEPARTMENT",
    6: "FINANCE DEPARTMENT",
    7: "FOOD, CIVIL SUPPLIES AND CONSUMER AFFAIRS DEPARTMENT",
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
    19: "PANCHAYATS, RURAL HOUSING AND RURAL DEVELOPMENT DEPARTMENT",
    20: "PORTS AND TRANSPORT DEPARTMENT",
    21: "REVENUE DEPARTMENT",
    22: "ROADS AND BUILDING DEPARTMENT",
    23: "SCIENCE AND TECHNOLOGY DEPARTMENT",
    24: "SOCIAL JUSTICE AND EMPOWERMENT DEPARTMENT",
    25: "SPORTS, YOUTH AND CULTURAL ACTIVITIES DEPARTMENT",
    26: "URBAN DEVELOPMENT AND URBAN HOUSING DEPARTMENT",
    27: "WOMEN AND CHILD DEVELOPMENT DEPARTMENT",
    28: "TRIBAL DEVELOPMENT DEPARTMENT",
    29: "CLIMATE CHANGE DEPARTMENT",
    59: "CHIEF MINISTER OFFICE DEPARTMENT"
}
        
# Helper Functions
def translate_text(text, source_lang="gu", target_lang="en"):
    """Translate text using GoogleTranslator."""
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        return f"Translation failed: {str(e)}"

def clean_text(text):
    """Clean input text for LSTM prediction."""
    text = str(text)
    text = re.sub(r'[^a-zA-Z\u0A80-\u0AFF\s]', '', text)  # Remove special characters
    return text.lower()

def predict_department(text):
    """Predict department routing."""
    transformed_text = department_vectorizer.transform([text])
    prediction = department_model.predict(transformed_text)
    return department_dict.get(prediction[0], "Others")

def prepare_texts_for_lstm(texts, tokenizer, max_len=100):
    """Prepare text for LSTM input."""
    cleaned_texts = [clean_text(text) for text in texts]
    sequences = tokenizer.texts_to_sequences(cleaned_texts)
    return pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')

def predict_status_lstm(text, tokenizer, model):
    """Predict status using LSTM model."""
    input_data = prepare_texts_for_lstm([text], tokenizer, model.input_shape[1])
    predictions = model.predict(input_data)
    return "Accept" if (predictions > 0.5).astype(int).flatten()[0] == 1 else "Reject"

def predict_sentiment(text):
    """Predict sentiment using original model."""
    encoded_input = tokenizer(text, return_tensors="pt")
    output = sentiment_model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    labels = ["Negative", "Neutral", "Positive"]
    sentiment = {label: score for label, score in zip(labels, scores)}
    max_label = max(sentiment, key=sentiment.get)
    max_score = sentiment[max_label]
    return max_label, max_score

# Main API View
class TextDataView(APIView):

    # permission_classes = [IsAuthenticated] 

    def check_permissions(self, request):
        if request.method == "POST" and not request.user.is_authenticated:
            raise PermissionDenied("Authentication is required for POST requests.")

    def get(self, request):
        texts = WTC.objects.all()
        serializer = WTCSerializer(texts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=WTCSerializer)
    def post(self, request):
        # self.permission_classes = [IsAuthenticated]
        print(">>>>>>>>>> request - get <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ")
        print("********************************")
        print("********************************")
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", request.data)
        print("********************************")
        print("********************************")
        print("********************************")
        print("********************************")
        serializer = WTCSerializer(data=request.data)
        wtc_message = request.data.get('message', 'false')
        wtc_lang = request.data.get('lang', False)

        # Translation
        if wtc_lang == "gu":
            wtc_message = translate_text(wtc_message)

        # Parallel Execution for Sentiment, Department, and Status
        with ThreadPoolExecutor() as executor:
            future_sentiment = executor.submit(predict_sentiment, wtc_message)
            future_department = executor.submit(predict_department, wtc_message)
            future_status = executor.submit(
                predict_status_lstm, wtc_message, status_tokenizer, status_model
            )

            # Collect Results
            sentiment_label, sentiment_score = future_sentiment.result()
            department_name = future_department.result()
            status_result = future_status.result()

        user = request.user
        # Ensure a valid project is available
        project = Project.objects.filter(user=user).first()
        if not project:
            return Response(
                {"error": "No project found for this authenticated user"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Save WTC Entry
        if serializer.is_valid():
            serializer.validated_data.update({
                'sentiment_cal_gra': sentiment_score,
                'sentiment_cal_pol': sentiment_label,
                'depr_rout': department_name,
                'lo_sc': status_result,
                'user' : user, 
                'project' : project
            })
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ModeDistributionView(APIView):
    def get(self, request, *args, **kwargs):
        mode_distribution = WTC.objects.values('mode').annotate(count=Count('id'))
        return Response(mode_distribution)
    

class DeprRoutDistributionView(APIView):
    def get(self, request, *args, **kwargs):
        depr_rout_distribution = WTC.objects.values('depr_rout').annotate(count=Count('id'))
        return Response(depr_rout_distribution)
    
class AnalyticsAPIView(APIView):
    def get(self, request):
        # Total Applications
        total_applications = WTC.objects.count()

        # Pending Applications
        pending_applications = WTC.objects.filter(pending=True).count()

        # Today's Applications
        today = date.today()
        todays_applications = WTC.objects.filter(created_at__date=today).count()

        # Daily Average Applications (over the past 7 days)
        last_week = today - timedelta(days=7)
        past_week_apps = WTC.objects.filter(created_at__date__gte=last_week).count()
        daily_avg = round(past_week_apps / 7, 2) if past_week_apps > 0 else 0.00


        # Construct Response Data
        data = {
            "total_applications": total_applications,
            "todays_applications": todays_applications,
            "pending_applications": pending_applications,
            "daily_average_applications": daily_avg,
        }

        return Response(data)


class TypeDistributionView(APIView):
    def get(self, request, *args, **kwargs):
        # Allowed types to match (case-insensitive and singular/plural aware)
        allowed_types = ['Grievance', 'Appointment', 'Suggestion', 'Wish']
        
        # Create filters for case-insensitive matches ignoring trailing 's'
        from django.db.models import Q
        
        filters = Q()
        for t in allowed_types:
            filters |= Q(type__iexact=t) | Q(type__iexact=f"{t}s")
        
        # Query with the filters
        type_distribution = (
            WTC.objects.filter(filters)
            .values('type')
            .annotate(count=Count('id'))
        )
        return Response(type_distribution)
    

    # # Total counts
    # total_records = WTC.objects.count()
    # total_accepted = WTC.objects.filter(Q(lo_sc="accept") | Q(lo_sc_hu="accept")).count()
    # total_rejected = WTC.objects.filter(Q(lo_sc="reject") | Q(lo_sc_hu="reject")).count()

    # # Machine-generated statistics (lo_sc)
    # machine_accepted = WTC.objects.filter(lo_sc="accept").count()
    # machine_rejected = WTC.objects.filter(lo_sc="reject").count()

    # # Accuracy Calculation
    # machine_decisions = WTC.objects.filter(Q(lo_sc="accept") | Q(lo_sc="reject")).count()
    # matched_decisions = WTC.objects.filter(
    #     (Q(lo_sc="accept") & Q(lo_sc_hu="accept")) |
    #     (Q(lo_sc="reject") & Q(lo_sc_hu="reject"))
    # ).count()

    # accuracy = (matched_decisions / machine_decisions) * 100 if machine_decisions > 0 else 0

    # # Context for the template
    # context = {
    #     # "total_records": total_records,
    #     "total_accepted": total_accepted,
    #     "total_rejected": total_rejected,
    #     "machine_accepted": machine_accepted,
    #     "machine_rejected": machine_rejected,
    #     "accuracy": round(accuracy, 2),
    # }

    # return render(request, "wtc_statistics.html", context)

class WTCStatisticsAPIView(APIView):
    """
    API View to calculate and return WTC statistics.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Total counts
            total_records = WTC.objects.count()
            total_accepted = WTC.objects.filter(Q(lo_sc="accept") | Q(lo_sc_hu="accept")).count()
            total_rejected = WTC.objects.filter(Q(lo_sc="reject") | Q(lo_sc_hu="reject")).count()

            # Machine-generated statistics (lo_sc)
            machine_accepted = WTC.objects.filter(lo_sc="accept").count()
            machine_rejected = WTC.objects.filter(lo_sc="reject").count()

            # Accuracy Calculation
            machine_decisions = WTC.objects.filter(Q(lo_sc="accept") | Q(lo_sc="reject")).count()
            matched_decisions = WTC.objects.filter(
                (Q(lo_sc="accept") & Q(lo_sc_hu="accept")) |
                (Q(lo_sc="reject") & Q(lo_sc_hu="reject"))
            ).count()

            accuracy = (matched_decisions / machine_decisions) * 100 if machine_decisions > 0 else 0

            # Response data
            data = {
                "total_accepted": total_accepted,
                "total_rejected": total_rejected,
                "machine_accepted": machine_accepted,
                "machine_rejected": machine_rejected,
                "accuracy": round(accuracy, 2),
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
