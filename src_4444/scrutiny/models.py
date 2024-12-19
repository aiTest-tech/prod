from django.db import models
from base.models import Data
from auth_app.models import User, Project

class ScrutinyRecord(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name="l1_scr_data")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_succ = models.BooleanField(default=False)
    api_hit = models.IntegerField(default=0)
    lo_scu = models.TextField(null=True, blank=True)
    depar_route = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"L1 Scr Depr Routing {self.id} - Success: {self.is_succ}"