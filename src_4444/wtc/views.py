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
from sentiment.models import SentimentData
from base.models import  Data
from scrutiny.models import ScrutinyRecord
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from datetime import datetime


# def call_scrutiny_api(lang, text):
#     url = "http://10.10.2.179:3333/api/scrutiny/"
#     payload = {
#         "lang": lang,
#         "text": text
#     }
#     headers = {
#         "Content-Type": "application/json",  # Specify the content type as JSON
#         "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0NDE1MTIxLCJpYXQiOjE3MzMxMTkxMjEsImp0aSI6ImY2MGI2MDc2NDg0NTRjMzhhZGZhMTNlMjFkMTdmYTc2IiwidXNlcl9pZCI6MX0.Y7QgERUklS0ZRpnBPYnNuS14b5JQ3pIrb3y5vgY6jVA"  # Replace <your_token> with your actual token if required
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
        
#         if response.status_code == 200:
#             # Successfully got a response
#             return response
#             print("Response Data:", response.json())
#         else:
#             return None
#             print(f"Error: {response.status_code}, {response.text}")

#     except requests.exceptions.RequestException as e:
#         print(f"Error calling API: {e}")

# # Example usage
# lang = "en"  # or "gu" for Gujarati
# text = "The quality of roads in my locality is very poor."

# import pickle

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

# class WTCListViewAnaly(ListAPIView):
#     serializer_class = WTCSerializer

#     def get_queryset(self):
#         return WTC.objects.all().order_by('-created_at') 

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

# department_model_path = "/home/cmoai/modell/combined_department_predictor.pkl"  # Updated to new model path
# status_model_path = "/home/cmoai/modell/lstm_message_classifier.h5"
# status_tokenizer_path = "/home/cmoai/modell/tokenizer.json"
# vectorizer_path = "/home/cmoai/modell/tfidf_vectorizer.pkl"


# Load department routing model and TF-IDF vectorizer
department_model = joblib.load(department_model_path)
department_vectorizer = joblib.load(vectorizer_path)

# # Load department routing model
# def load_department_model(model_filename):
#     with open(model_filename, 'rb') as file:
#         department_model = pickle.load(file)
#     return department_model

# department_model = load_department_model(department_model_path)


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
    # transformed_text = translate_text(text, source_lang="gu", target_lang="en")
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
    
    # @swagger_auto_schema(request_body=WTCSerializer)
    # def post(self, request):
    #     print(">>>>>>>>>> request - get <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ")
    #     print("********************************")
    #     print("********************************")
    #     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", request.data)
    #     print("********************************")
    #     print("********************************")
    #     print("********************************")
    #     print("********************************")
    #     serializer = WTCSerializer(data=request.data)
    #     wtc_message = request.data.get('message', 'false')
    #     wtc_subject = request.data.get('subject', 'false')
    #     wtc_lang = request.data.get('lang', False)

    #     # Translation
    #     if wtc_lang == "gu":
    #         wtc_message = translate_text(wtc_message)
    #         wtc_subject = translate_text(wtc_subject)

    #     # Handle long messages by chunking
    #     def calculate_avg_message_sentiment(message):
    #         if len(message) > 500:
    #             chunks = [message[i:i + 500] for i in range(0, len(message), 500)]
    #             chunk_sentiments = [predict_sentiment(chunk)[1] for chunk in chunks]  # Extract score
    #             return sum(chunk_sentiments) / len(chunk_sentiments)
    #         return predict_sentiment(message)[1]

    #     # Calculate weighted sentiment
    #     if len(wtc_message) > 500:
    #         avg_message_sentiment = calculate_avg_message_sentiment(wtc_message)
    #         subject_sentiment_score = predict_sentiment(wtc_subject)[1]
    #         weighted_sentiment_score = (0.4 * subject_sentiment_score) + (0.6 * avg_message_sentiment)
    #     else:
    #         weighted_sentiment_score = predict_sentiment(wtc_message)[1]

    #     # Parallel Execution for Department and Status Predictions
    #     with ThreadPoolExecutor() as executor:
    #         future_department = executor.submit(predict_department, wtc_message)
    #         future_status = executor.submit(
    #             predict_status_lstm, wtc_message, status_tokenizer, status_model
    #         )

    #         # Collect Results
    #         department_name = future_department.result()
    #         status_result = future_status.result()

    #     user = request.user
    #     # Ensure a valid project is available
    #     project = Project.objects.filter(user=user).first()
    #     if not project:
    #         return Response(
    #             {"error": "No project found for this authenticated user"},
    #             status=status.HTTP_404_NOT_FOUND,
    #         )

    #     # Save WTC Entry
    #     if serializer.is_valid():
    #         serializer.validated_data.update({
    #             'sentiment_cal_gra': weighted_sentiment_score,
    #             'sentiment_cal_pol': "positive" if weighted_sentiment_score > 0 else "negative",
    #             'depr_rout': department_name,
    #             'lo_sc': status_result,
    #             'user': user,
    #             'project': project
    #         })
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        wtc_subject = request.data.get('subject', 'false')
        wtc_lang = request.data.get('lang', False)
        sentiment_label = sentiment_score = ""
        mach_sc = "None"
        mach_dept = "None"

        user = request.user
        project = Project.objects.filter(user=user).first()
        data_fe = Data.objects.create(
                    audio_path="",  # Not applicable here
                    text=wtc_message,
                    etext="",  # Optionally, save extra translated text if needed
                )
        sentiment_record = SentimentData.objects.create(
                    data=data_fe,
                    user=user,
                    project=project,
                    is_succ=False,  # Initially set to False, will update after successful analysis
                    api_hit=1,
                    label = " ",
                    score = 0,  # Increment API hit count as per logic
                )
        scrutRec = ScrutinyRecord.objects.create(
            data=data_fe,
            user=user,
            project=project,
            is_succ=False,  # Initially set to False
            api_hit=1,  # Increment API hit count
        )
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # get_sc_dep_api = call_scrutiny_api(wtc_lang, wtc_subject)
        print(">>>>>>>>>>>%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        # print(get_sc_dep_api)
        url = "http://10.10.2.179:4446/api/scrutiny/"
        payload_sc_dept = {
            "lang": wtc_lang,
            "text": wtc_message
        }
        headers_sc_dept = {
            "Content-Type": "application/json",  # Specify the content type as JSON
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0NDE1MTIxLCJpYXQiOjE3MzMxMTkxMjEsImp0aSI6ImY2MGI2MDc2NDg0NTRjMzhhZGZhMTNlMjFkMTdmYTc2IiwidXNlcl9pZCI6MX0.Y7QgERUklS0ZRpnBPYnNuS14b5JQ3pIrb3y5vgY6jVA"  # Replace <your_token> with your actual token if required
        }

        # try:
        response = requests.post(url, json=payload_sc_dept, headers=headers_sc_dept)
        print(response)
        print(response.status_code)
        if response.status_code == 201:
            print(response.json())
            mach_sc = response.json().get('scrutiny_decision', "None")
            mach_dept = response.json().get('department', "None")
        print("<<<<<<<<<<<<<<<<<%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        # Translation
        if wtc_lang == "gu":
            # wtc_message = translate_text(wtc_message)
            wtc_subject = translate_text(wtc_subject)

        # Parallel Execution for Sentiment, Department, and Status
        with ThreadPoolExecutor() as executor:
            future_sentiment = executor.submit(predict_sentiment, wtc_subject)
            # future_department = executor.submit(predict_department, wtc_message)
            # future_status = executor.submit(
            #     predict_status_lstm, wtc_subject, status_tokenizer, status_model
            # )

            # Collect Results
            sentiment_label, sentiment_score = future_sentiment.result()
            # department_name = future_department.result()
            # status_result = future_status.result()

        
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
                'depr_rout': mach_dept,
                'depr_rout_fetch_first': mach_dept.split(',')[0],
                'lo_sc': mach_sc,
                'user' : user, 
                'project' : project
            })
            serializer.save()
            sentiment_record.is_succ = True
            sentiment_record.save()
            scrutRec.is_succ = True
            scrutRec.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ModeDistributionView(APIView):
    def get(self, request, *args, **kwargs):
        mode_distribution = WTC.objects.values('mode').annotate(count=Count('id'))
        return Response(mode_distribution)
    

class DeprRoutDistributionView(APIView):
    def get(self, request, *args, **kwargs):
        depr_rout_distribution = WTC.objects.values('depr_rout_fetch_first').annotate(count=Count('id'))
        return Response(depr_rout_distribution)
    
def calculate_general_daily_avg(model):
    """
    Calculate the general daily average of objects in the database
    based on total requests / total days since the first record.

    Args:
        model (Model): The Django model to query.

    Returns:
        float: Daily average of objects created in the database.
    """
    # Get the earliest record and the total count of records
    earliest_record = model.objects.order_by('created_at').first()
    total_count = model.objects.count()

    # If there are no records, return 0.00
    if not earliest_record or total_count == 0:
        return 0.00

    # Calculate the total number of days since the first record
    earliest_date = earliest_record.created_at.date()
    today = datetime.now().date()
    total_days = (today - earliest_date).days + 1  # Include the current day

    # Calculate the average: total requests / total days
    return round(total_count / total_days, 2)
    
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
        # last_period = today - timedelta(days=days)
        # total_count = WTC.objects.filter(created_at__date__gte=last_period).count()
        daily_avg =  calculate_general_daily_avg(WTC)


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
            total_accepted = WTC.objects.filter(Q(lo_sc_hu="Accept") | Q(lo_sc_hu="Accept")).count()
            total_rejected = WTC.objects.filter(Q(lo_sc_hu="Reject") | Q(lo_sc_hu="Reject")).count()

            # Machine-generated statistics (lo_sc)
            machine_accepted = WTC.objects.filter(lo_sc="Accept").count()
            machine_rejected = WTC.objects.filter(lo_sc="Reject").count()

            # Accuracy Calculation
            machine_decisions = WTC.objects.filter(Q(lo_sc="Accept") | Q(lo_sc="Reject")).count()
            matched_decisions = WTC.objects.filter(
                (Q(lo_sc="Accept") & Q(lo_sc_hu="Accept")) |
                (Q(lo_sc="Reject") & Q(lo_sc_hu="Reject"))
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

@csrf_exempt
def search_wtc_records(request):
    if request.method == 'POST':
        try:
            # Parse the JSON request body
            body = json.loads(request.body.decode('utf-8'))
            search_string = body.get('search_string', None)

            if not search_string:
                return JsonResponse({'success': False, 'error': 'Search string is required'}, status=400)

            # Build the query to search across multiple fields
            filters = Q(
                name__icontains=search_string
            ) | Q(
                email__icontains=search_string
            ) | Q(
                phone__icontains=search_string
            ) | Q(
                subject__icontains=search_string
            )

            # Fetch matching records
            records = WTC.objects.filter(filters).values(
                'id', 'name', 'email', 'phone', 'subject', 'created_at'
            )

            # Return results as JSON
            return JsonResponse({'success': True, 'records': list(records)}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

    return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'}, status=405)


@csrf_exempt
def primary_scrutiny_done(request):

    if request.method == "POST":
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            record_id = data.get("id")
            lo_sc_value = data.get("lo_sc_hu")

            # Validate inputs
            if not record_id or not lo_sc_value:
                return JsonResponse({"error": "Invalid input data"}, status=400)

            # Fetch the record from the database
            try:
                wtc_record = WTC.objects.get(id=record_id)
            except WTC.DoesNotExist:
                return JsonResponse({"error": "Record not found"}, status=404)

            # Update the fields
            wtc_record.lo_sc_hu = lo_sc_value
            wtc_record.pending = False
            wtc_record.save()

            return JsonResponse({"message": "Record updated successfully"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class WTCLOListView(ListAPIView):
    serializer_class = WTCSerializer
    # permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access the view

    def get_queryset(self):
        # Access the user from the request object
        user = self.request.user.id
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(user)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")

        if user == 1 or user == 8 :
            # You can use the user object to filter or log as needed
            # Example: Filter by user-related records
            return WTC.objects.filter(
                (Q(pending=True) | Q(is_posted=False)) & Q(user=user)
            ).order_by('-created_at')
        return JsonResponse({"Auth": "fail"}, status=405)

class WTCListViewAnaly(ListAPIView):
    serializer_class = WTCSerializer

    def get_queryset(self):
        # Access the user from the request object
        user = self.request.user.id
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(user)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")

        if user == 1 or user == 8:
            return WTC.objects.all().order_by('-created_at') 
        return JsonResponse({"Auth": "fail"}, status=405)
        