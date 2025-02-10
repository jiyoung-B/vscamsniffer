from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AudioFile
from django.core.files.storage import default_storage

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        # 확장자 검증
        if not file.name.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            return JsonResponse({'error': '음성 파일(mp3, wav, ogg, m4a)만 업로드 가능합니다.'}, status=400)

        saved_file = default_storage.save(f'uploads/{file.name}', file)
        audio = AudioFile.objects.create(file=saved_file)
        return JsonResponse({'message': '파일 업로드 성공!', 'file_url': audio.file.url})
    
    return JsonResponse({'error': '파일을 업로드하세요.'}, status=400)
