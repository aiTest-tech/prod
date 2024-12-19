# from django.db import models
# from base.models import Data
# from auth_app.models import User, Project

# class ScrutinyRecord(models.Model):
#     data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name="scrutiny_data")  # Adjusted related name
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     is_succ = models.BooleanField(default=False)  # Status flag
#     api_hit = models.IntegerField(default=0)  # Track API hits
#     label = models.CharField(max_length=50, null=True, blank=True)  # Label for scrutiny decision
#     department = models.CharField(max_length=255, null=True, blank=True)  # Department routing

#     def __str__(self):
#         return f"Scrutiny Record {self.id} - Success: {self.is_succ}"

from django.db import models
from base.models import Data
from auth_app.models import User, Project

class ScrutinyRecord(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE, related_name="scrutiny_data")  # Adjusted related name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_succ = models.BooleanField(default=False)  # Status flag indicating success or failure of the scrutiny
    api_hit = models.IntegerField(default=0)  # Track API hits
    label = models.CharField(max_length=50, null=True, blank=True)  # Label for scrutiny decision
    department = models.CharField(max_length=255, null=True, blank=True)  # Department routing
    scrutiny_decision = models.CharField(max_length=20, choices=[('Accept', 'Accept'), ('Reject', 'Reject')], null=True, blank=True)  # Store status prediction result

    def __str__(self):
        return f"Scrutiny Record {self.id} - Success: {self.is_succ} - Decision: {self.scrutiny_decision}"

