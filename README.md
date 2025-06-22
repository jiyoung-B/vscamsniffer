# 👮🏻‍♀️ Voice Phishing Detection Service

보이스피싱 예방을 위한 AI 기반 웹 서비스입니다.  
사용자의 음성 데이터를 분석하여 보이스피싱 확률을 추정하고,  
상황을 시뮬레이션하며 사용자 스스로 위험을 인지할 수 있도록 돕는 시스템을 목표로 하였습니다.

## 🔧 프로젝트 개요
- 사용자가 음성 녹음을 업로드하면, KoBERT 모델을 통해 보이스피싱 확률을 예측합니다.
- KoLLAMA 기반 사기범 역할 시뮬레이션 기능도 함께 제공됩니다.
- React 프론트엔드, FastAPI + Django 백엔드, Azure Kubernetes 기반 멀티 컨테이너 구조로 운영됩니다.

## 🌱 주요 기술 스택
| 분야 | 기술 |
|------|------|
| Frontend | React, WebSocket |
| Backend | FastAPI (Python 3.8), Django (Python 3.11) |
| AI Model | KoBERT (음성 → 텍스트 변환 후 사기확률 예측), KoLLAMA (대화 시뮬레이션) |
| Infra | Azure Kubernetes Service (AKS), Docker, NGINX, HTTPS |
| 배포/운영 | Azure GPU 노드, Container Registry, TLS 인증서 발급 및 HTTPS 설정 |

## 💼 나의 역할 (Infra 중심)
- **Kubernetes 인프라 구성 및 멀티 컨테이너 배포 (AKS)**
  - React, FastAPI, Django 서비스를 각기 다른 컨테이너로 구성하고 통합 배포
- **GPU 노드 설정 및 리소스 할당**
  - AI 모델(Django) 컨테이너에 GPU 노드 연결
- **HTTPS 도메인 설정**
  - NGINX + Ingress Controller 구성
  - 도메인 인증서 발급 및 HTTPS 라우팅 설정 (`https://vscamsniffer.work.gd`)
- **서버 간 통신 환경 구성**
  - WebSocket / API 통신 간 mixed-content 오류 해결 (ws → wss)
## Architecture
![image](https://github.com/user-attachments/assets/cde94bcb-f36d-4594-aa33-ff8348f8a6a5)

## 📝 참고 자료
- [📁 프로젝트 GitHub](https://github.com/VScamsniffer)
- [📄 발표용 PPT](https://drive.google.com/file/d/1HKSV04aBiTirrRj9jYMjuAuKvzn-lQJu/view)
- [🗂 Notion 프로젝트 기록](https://buly.kr/E78TKpR)

## 💡 회고 및 성장
이 프로젝트를 통해 처음으로 Python과 컨테이너 기반 백엔드 환경을 다루었고,  
특히 클라우드 인프라 구성 및 보안 연결(HTTPS) 설정에 대한 실무 경험을 쌓을 수 있었습니다.  
코드 구현보다는 인프라 관점에서 문제 해결과 안정적인 환경 제공에 집중하였고,  
이후 Airflow, Spark 등 데이터 파이프라인 기술을 학습하며 데이터 엔지니어로서의 기반을 넓혀가고 있습니다.

