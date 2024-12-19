    # from django.db import models
    # from base.models import BaseModel, Data
    # from auth_app.models import User, Project

    # class ASRData(BaseModel):
    #     data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name="asr_data", null=True)
    #     user = models.ForeignKey(User, on_delete=models.CASCADE)
    #     project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #     min = models.IntegerField()
    #     is_succ = models.BooleanField(default=False)
    #     api_hit = models.IntegerField(default=0)

    #     def __str__(self):
    #         return f"ASR Data {self.id} - Success: {self.is_succ}"

from django.db import models
from base.models import BaseModel, Data
from auth_app.models import User, Project
from sentiment.models import SentimentData
from scrutiny.models import ScrutinyRecord

class ASRData(BaseModel):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name="asr_data", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    min = models.IntegerField()
    is_succ = models.BooleanField(default=False)
    api_hit = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.data:
                # Create SentimentData instance
            SentimentData.objects.create(
                data=self.data,
                user=self.user,
                project=self.project,
                is_succ=self.is_succ,
                api_hit=self.api_hit
            )
                # Create ScrutinyRecord instance
            ScrutinyRecord.objects.create(
                data=self.data,
                user=self.user,
                project=self.project,
                is_succ=self.is_succ,
                api_hit=self.api_hit
            )

    def __str__(self):
            return f"ASR Data {self.id} - Success: {self.is_succ}"