from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from azure.storage.blob import BlobServiceClient
from django.conf import settings
import os

# Azure Blob Storage 클라이언트 설정
AZURE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={settings.AZURE_ACCOUNT_NAME};AccountKey={settings.AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)

@method_decorator(csrf_exempt, name="dispatch")
class AudioFileUploadView(View):
    def post(self, request):
        print("[DEBUG] 파일 업로드 요청 수신")

        if "file" not in request.FILES:
            print("🚨 [ERROR] 파일이 요청에 포함되지 않음")
            return JsonResponse({"error": "파일이 포함되지 않았습니다."}, status=400, content_type="application/json")

        uploaded_file = request.FILES["file"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        allowed_extensions = [".mp3", ".wav", ".ogg", ".m4a"]

        print(f"[DEBUG] 업로드된 파일 이름: {uploaded_file.name}")
        print(f"[DEBUG] 파일 확장자: {ext}")
        print(f"[DEBUG] 파일 크기: {uploaded_file.size} bytes")

        # ✅ 잘못된 파일 확장자인 경우 오류 응답 반환
        if ext not in allowed_extensions:
            print(f"🚨 [ERROR] 잘못된 파일 형식 업로드: {uploaded_file.name} ({ext})")
            return JsonResponse({"error": "음성 파일(mp3, wav, ogg, m4a)만 업로드 가능합니다."}, status=400, content_type="application/json")

        try:
            # Azure Blob Storage에 직접 업로드
            blob_client = container_client.get_blob_client(f"uploads/{uploaded_file.name}")
            blob_client.upload_blob(uploaded_file.read(), overwrite=True)

            file_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER}/uploads/{uploaded_file.name}"

            print(f"Azure 파일 업로드 완료: {file_url}")  # 터미널 로그 확인
            return JsonResponse({"file_url": file_url}, status=200, content_type="application/json")

        except Exception as e:
            print(f"🚨 [ERROR] 업로드 중 오류 발생: {str(e)}")  # 터미널 로그 확인
            return JsonResponse({"error": "파일 업로드 중 오류가 발생했습니다."}, status=500, content_type="application/json")
