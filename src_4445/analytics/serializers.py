from rest_framework import serializers
from .models import Project, ProjectAnalytics

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']

class ProjectAnalyticsSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    success_rate = serializers.SerializerMethodField()
    failure_rate = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAnalytics
        fields = [
            'id',
            'project',
            'api_name',
            'total_minutes_called',
            'total_requests',
            'successful_requests',
            'failed_requests',
            'success_rate',
            'failure_rate',
        ]

    def get_success_rate(self, obj):
        return obj.success_rate()

    def get_failure_rate(self, obj):
        return obj.failure_rate()