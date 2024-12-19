from django.db import models
from base.models import Data
from auth_app.models import User, Project

class SentimentData(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name="sentiment_data")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_succ = models.BooleanField(default=False)
    api_hit = models.IntegerField(default=0)
    label = models.CharField(max_length=50, null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    # asr_data_link = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return f"Sentiment Data {self.id} - Success: {self.is_succ}"