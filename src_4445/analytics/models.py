from django.db import models
from auth_app.models import Project

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
