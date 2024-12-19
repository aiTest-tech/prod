# from django.db import connection
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# import json
# class AnalyticsView(APIView):
#     #permission_classes = [IsAuthenticated]
#     def get(self, request, *args, **kwargs):
#         # List of all possible projects
#         all_projects = {
#             1: 'WTC',
#             2: 'JS',
#             3: 'SWA'
#         }

#         # Prepare the structure for the analytics response
#         result = {
#             "ASR": {},
#             "Sentiment": {},
#             "Scrutiny": {}
#         }

#         # Define SQL queries
#         queries = {
#             "ASR": """
#                 SELECT 
#                     project_id,
#                     SUM(api_hit) AS total_api_hits,
#                     SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) AS success_count,
#                     ROUND(100.0 * SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
#                     SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) AS failure_count,
#                     ROUND(100.0 * SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate,
#                     SUM(min) AS total_minutes
#                 FROM 
#                     app_asrdata
#                 GROUP BY 
#                     project_id; 
#             """,

#             "Sentiment": """
#                 SELECT 
#                     project_id,
#                     SUM(api_hit) AS total_api_hits,
#                     SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) AS success_count,
#                     ROUND(100.0 * SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
#                     SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) AS failure_count,
#                     ROUND(100.0 * SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate
#                 FROM 
#                     sentiment_sentimentdata
#                 GROUP BY 
#                     project_id;
#             """,

#             "Scrutiny": """
#                 SELECT 
#                     project_id,
#                     SUM(api_hit) AS total_api_hits,
#                     SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) AS success_count,
#                     ROUND(100.0 * SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
#                     SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) AS failure_count,
#                     ROUND(100.0 * SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate
#                 FROM 
#                     scrutiny_scrutinyrecord
#                 GROUP BY 
#                     project_id;
#             """
#         }

#         # Execute each query and populate the result
#         for api_name, query in queries.items():
#             with connection.cursor() as cursor:
#                 cursor.execute(query)
#                 rows = cursor.fetchall()

#             for row in rows:
#                 project_id, total_api_hits, success_count, success_rate, failure_count, failure_rate, *extras = row
#                 project_name = all_projects.get(project_id, f"Project {project_id}")

#                 # Handle ASR specific extra field for total_minutes
#                 total_minutes = extras[0] if extras else 0

#                 result[api_name][project_name] = {
#                     'Total API Hits': total_api_hits,
#                     'Successful Requests': success_count,
#                     'Success Rate': success_rate,
#                     'Failed Requests': failure_count,
#                     'Failure Rate': failure_rate,
#                 }

#                 if api_name == "ASR":
#                     result[api_name][project_name]['Total Minutes'] = total_minutes

#         result_li = {key: [value] for key, value in result.items()}
#         # print(json.dumps(result, indent=4))

#         return Response(result_li, status=status.HTTP_200_OK)

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class AnalyticsView(APIView):
    #permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # List of all possible projects
        all_projects = {
            1: 'WTC',
            2: 'JS',
            3: 'SWA'
        }

        # Prepare the structure for the analytics response
        result = {
            "asr": [],
            "sentiment": [],
            "l1_scrutiny": []
        }

        # Define SQL queries
        queries = {
            "asr": """
                SELECT 
                    project_id,
                    SUM(api_hit) AS total_api_hits,
                    SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) AS success_count,
                    ROUND(100.0 * SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
                    SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) AS failure_count,
                    ROUND(100.0 * SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate,
                    SUM(min) AS total_minutes
                FROM 
                    app_asrdata
                GROUP BY 
                    project_id; 
            """,

            "sentiment": """
                SELECT 
                    project_id,
                    SUM(api_hit) AS total_api_hits,
                    SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) AS success_count,
                    ROUND(100.0 * SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
                    SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) AS failure_count,
                    ROUND(100.0 * SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate
                FROM 
                    sentiment_sentimentdata
                GROUP BY 
                    project_id;
            """,

            "l1_scrutiny": """
                SELECT 
                    project_id,
                    SUM(api_hit) AS total_api_hits,
                    SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) AS success_count,
                    ROUND(100.0 * SUM(CASE WHEN is_succ = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate,
                    SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) AS failure_count,
                    ROUND(100.0 * SUM(CASE WHEN is_succ = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate
                FROM 
                    scrutiny_scrutinyrecord
                GROUP BY 
                    project_id;
            """
        }

        for api_name, query in queries.items():
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            for row in rows:
                project_id, total_api_hits, success_count, success_rate, failure_count, failure_rate, *extras = row
                project_name = all_projects.get(project_id, f"Project {project_id}")

                # Handle ASR specific extra field for total_minutes
                total_minutes = extras[0] if extras else 0

                # Construct the result data
                api_data = {
                    'project': project_name,
                    'total_requests': total_api_hits,
                    'success_request': success_count,
                    'success_rate': success_rate,
                    'failure_request': failure_count,
                    'failure_rate': failure_rate,
                }

                if api_name == "asr":
                    api_data['total_minutes_called'] = total_minutes

                # Append the project data to the appropriate list in the result
                result[api_name].append(api_data)

        return Response(result, status=status.HTTP_200_OK)
