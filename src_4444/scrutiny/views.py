import joblib
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ScrutinyRequestSerializer
from .models import ScrutinyRecord, User, Project, Data
from app.models import ASRData
from drf_yasg.utils import swagger_auto_schema
from .models import ScrutinyRecord
from rest_framework.permissions import IsAuthenticated

# Dictionary to map department numbers to department names
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

class ScrutinyDepartmentRoutingView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ScrutinyRequestSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ScrutinyRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"status": "fail", "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        record_id = serializer.validated_data['id']
        text = serializer.validated_data['text']

        ## am-work123
        user = request.user
        project = Project.objects.filter(user=user).first()
        if not project:
            return Response(
                {"error": "No project found for this authenticated user"},
                status=status.HTTP_404_NOT_FOUND,
            )
                
        # Save the text and sentiment in the Data model
        data = Data.objects.create(
            audio_path="",  # Not applicable here
            text=text,
            etext="",  # Optionally add extra translated text
        )

        # Save the routing information in L1ScrDeprRouting model
        scrutRec = ScrutinyRecord.objects.create(
            data=data,
            user=user,
            project=project,
            is_succ=False,  # Initially set to False
            api_hit=1,  # Increment API hit count
        )
        
        try:
            record = ASRData.objects.get(id=record_id)

            # Simulated LSTM results for demonstration
            lstm_result_1 = "Accept"

            if lstm_result_1 != "Accept":
                record.scrutiny_decision = "Reject"
                record.save()

                # Update L1ScrDeprRouting for rejection status
                scrutRec.is_succ = False
                scrutRec.save()

                return Response(
                    {"status": "fail", "message": "Record rejected by L1 Scrutiny"},
                    status=status.HTTP_200_OK,
                )

            lstm_result_2 = 2  # Simulated department number

            department_number = lstm_result_2
            department_name = department_dict.get(department_number, "Others")

            record.scrutiny_decision = lstm_result_1
            record.department = department_name
            record.save()

            # Update L1ScrDeprRouting for success status
            scrutRec.is_succ = True
            scrutRec.save()

            response_data = {
                'L1 Scrutiny': lstm_result_1,
                'Department': department_name,
            }

            # Return sentiment analysis result
            return Response(response_data, status=status.HTTP_200_OK)

        except ASRData.DoesNotExist:
            return Response(
                {"status": "fail", "message": "Record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
