from django.db import models

class AudioFile(models.Model):
    file = models.FileField(upload_to="uploads/")  # 파일 업로드 경로 지정
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 업로드 시간 자동 저장

    def __str__(self):
        return f"파일 이름: {self.file.name} (업로드: {self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
