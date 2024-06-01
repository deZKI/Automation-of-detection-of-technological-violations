from rest_framework import serializers
from .models import OriginalVideo, ProceedVideo, TimeCode


class OriginalVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalVideo
        fields = ['id', 'title', 'video']


class ProceedVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProceedVideo
        fields = ['id', 'title', 'original_video', 'version', 'video', 'excel_file', 'pdf_file']


class TimeCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeCode
        fields = ['id', 'proceed_video', 'prediction', 'time_in_seconds']
