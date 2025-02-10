from django.db import models

# 파일 확장자 검증 함수
def validate_audio_file(value):
    import os
    from django.core.exceptions import ValidationError
    
    ext = os.path.splitext(value.name)[1].lower()  # 파일 확장자 확인
    allowed_extensions = ['.mp3', '.wav', '.ogg', '.m4a']  # 허용된 확장자 목록
    
    if ext not in allowed_extensions:
        raise ValidationError('음성 파일(mp3, wav, ogg, m4a)만 업로드 가능합니다.')

# 오디오 파일 모델
class AudioFile(models.Model):
    file = models.FileField(upload_to='uploads/', validators=[validate_audio_file])  # 파일 저장 경로 및 검증
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 업로드 시간 자동 저장

    def __str__(self):
        return f"파일 이름: {self.file.name} (업로드: {self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
