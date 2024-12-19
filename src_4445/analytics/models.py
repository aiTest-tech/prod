# from django.db import models

# # Model for ASR Data
# class ASRData(models.Model):
#     project_id = models.CharField(max_length=255, help_text="ID of the project")
#     min = models.FloatField(help_text="Minutes called")
#     is_Succ = models.BooleanField(default=False, help_text="Was the call successful")

#     def __str__(self):
#         return f"ASRData: {self.project_id}"

# # Model for Sentiment Data
# class SentimentData(models.Model):
#     project_id = models.CharField(max_length=255, help_text="ID of the project")
#     is_Succ = models.BooleanField(default=False, help_text="Was the sentiment request successful")

#     def __str__(self):
#         return f"SentimentData: {self.project_id}"

# # Model for Scrutiny Record
# class ScrutinyRecord(models.Model):
#     project_id = models.CharField(max_length=255, help_text="ID of the project")
#     # Add any other fields related to scrutiny if required

#     def __str__(self):
#         return f"ScrutinyRecord: {self.project_id}"

from django.db import models
from auth_app.models import Project

# Model for Projects
# class Project(models.Model):
#     name = models.CharField(max_length=255, unique=True, help_text="Name of the project")

#     def __str__(self):
#         return self.name

# Model for Project Analytics
class ProjectAnalytics(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="analytics")
    api_name = models.CharField(max_length=50, help_text="Name of the API (e.g., ASR, Sentiment, Scrutiny)")
    total_minutes_called = models.FloatField(default=0, help_text="Total minutes called for this API")
    total_requests = models.IntegerField(default=0, help_text="Total requests made to this API")
    successful_requests = models.IntegerField(default=0, help_text="Total successful requests")
    failed_requests = models.IntegerField(default=0, help_text="Total failed requests")

    def success_rate(self):
        return (self.successful_requests / self.total_requests * 100) if self.total_requests else 0

    def failure_rate(self):
        return (self.failed_requests / self.total_requests * 100) if self.total_requests else 0

    def __str__(self):
        return f"{self.api_name} Analytics for {self.project.name}"
