from rest_framework import serializers
from .models import WTC

class WTCSerializer(serializers.ModelSerializer):
    class Meta:
        model = WTC
        fields = ['id', 'type', 'lang', 'project', 'user','name', 'occupation', 'address', 'phone',
            'district_corporation', 'taluka_zone', 'village_area', 'subject', 'message', 'department',
            'email', 'mode', 'created_at','lo_sc', 
            'sentiment_cal_gra', 
            'sentiment_cal_pol',
            'depr_rout']
        
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True},
            'project': {'required': False, 'allow_null': True},
        }

class WTCSerializer_analy(serializers.ModelSerializer):
    class Meta:
        model = WTC
        fields = [
            'id',
            'subject', 
            'message', 
            'email', 
            'created_at', 
            'lo_sc', 
            'sentiment_cal_gra', 
            'sentiment_cal_pol',
            'depr_rout'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Format `sentiment_cal_gra` as a percentage
        representation['sentiment_cal_gra'] = f"{float(instance.sentiment_cal_gra) * 100:.2f}%"
        return representation
