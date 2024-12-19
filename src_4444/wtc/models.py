from django.db import models
from auth_app.models import User, Project

class WTC(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    type = models.TextField(null=True, blank=True)
    lang = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100,null=True, blank=True)
    occupation = models.CharField(max_length=100,null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=15,null=True, blank=True)
    district_corporation = models.CharField(max_length=100,null=True, blank=True)
    taluka_zone = models.CharField(max_length=100,null=True, blank=True)
    village_area = models.CharField(max_length=100,null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True) # validators=[MaxLengthValidator(1000)
    department = models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mode = models.CharField(max_length=50,null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    asr_data_link = models.TextField(null=True, blank=True)
    lo_sc = models.TextField(null=True, blank=True)                      # it is manually driven
    sentiment_cal_gra = models.TextField(null=True, blank=True)
    sentiment_cal_pol = models.TextField(null=True, blank=True)
    depr_rout = models.TextField(null=True, blank=True)
    depr_rout_fetch_first = models.TextField(null=True, blank=True)
    pending = models.BooleanField(null=True, blank=True, default=True)
    is_posted = models.BooleanField(null=True, blank=True, default=False)
    lo_sc_hu = models.TextField(null=True, blank=True) # hu represrent the machience accuracry ? 


    def __str__(self):
        return f"WTC Entry {self.id} - {self.name}"