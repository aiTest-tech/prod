from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from deep_translator import GoogleTranslator
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from .serializers import AnalyzeSerializer
from .models import SentimentData, Data
from app.models import User, Project
from rest_framework.permissions import IsAuthenticated
import json

# Load pre-trained transformer model for sentiment analysis
model_name = "/home/cmoai/Models"  # Update the path to your model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

class AnalyzeSentiment(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=AnalyzeSerializer)
    def post(self, request, *args, **kwargs):
        try:
            serializer = AnalyzeSerializer(data=request.data)

            if serializer.is_valid():
                lang = serializer.validated_data.get("lang", None)
                text_data = serializer.validated_data.get("data", None)

                # Handle empty or invalid text_data
                if not text_data:
                    return Response(
                        {"error": "Text data is required for sentiment analysis."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Translate text if the language is Gujarati
                if lang == "gu":
                    try:
                        text_data = GoogleTranslator(source="gu", target="en").translate(text_data)
                        print(f"Translated text: {text_data}")
                    except Exception as e:
                        return Response(
                            {"error": "Failed to translate Gujarati text.", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                
                # Get the user and project (replace with actual logic)
                # user = request.user
                # project = Project.objects.filter(user=user).first()
                # if not project:
                #     return Response(
                #         {"error": "No project found for this authenticated user"},
                #         status=status.HTTP_404_NOT_FOUND,
                #     )  
                
                # Create the Data record

                data = Data.objects.create(
                    audio_path="",  # Not applicable here
                    text=text_data,
                    etext="",  # Optionally, save extra translated text if needed
                )

                user_instance = User.objects.get(id=1)
                proj_inst = Project.objects.get(id=1)
                # Create an initial SentimentData record
                sentiment_record = SentimentData.objects.create(
                    data=data,
                    user=user_instance,
                    project=proj_inst,
                    is_succ=False,  # Initially set to False, will update after successful analysis
                    api_hit=1,
                    label = " ",
                    score = 0,  # Increment API hit count as per logic
                )

                # Tokenize and process the text using the pre-trained model
                encoded_input = tokenizer(text_data, return_tensors="pt")
                output = model(**encoded_input)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores)  # Apply softmax to convert logits to probabilities

                # Define sentiment labels and their respective scores
                labels = ["Negative", "Neutral", "Positive"]
                sentiment = {label: score for label, score in zip(labels, scores)}

                # Get the sentiment with the highest score
                max_label = max(sentiment, key=sentiment.get)
                max_score = sentiment[max_label]

                # Update the SentimentData record with the result
                sentiment_record.is_succ = True  # Mark as successful
                sentiment_record.label = max_label
                sentiment_record.score = max_score
                sentiment_record.save()  # Save the sentiment record after analysis

                # Prepare the response with sentiment analysis results
                result = {
                    "sentiment": max_label,
                    "gravity": max_score,
                    "data_id": data.id,  # Include the Data record ID in the response
                }

                return Response(result, status=status.HTTP_200_OK)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
