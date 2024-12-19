from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Data(BaseModel):
    audio_path = models.FileField(upload_to='audio_files')
    text = models.TextField()
    etext = models.TextField()

    def __str__(self):
        return f"Data {self.id}: {self.text[:50]}"