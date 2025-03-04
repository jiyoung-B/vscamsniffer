<img src="https://capsule-render.vercel.app/api?type=waving&color=000080&height=200&section=header&text=보이스피싱 예방 프로젝트&fontSize=90" />


## 프로젝트 소개 📞
LLM을 활용한 보이스피싱 예방 웹 애플리케이션

-----
### Skill 📚


back-end
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
<img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white">
<img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=React&logoColor=white">


배포
Azure Virtual Machines
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white">
<img src="https://img.shields.io/badge/kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white">

--------

### 핵심 기능



<챗봇 기반 보이스피싱 예방 서비스>



📌 KoBERT를 이용한 보이스피싱 판별 프롬프트

- 사용자가 통화 내용을 음성 파일로 첨부 (mp3,mp4,wav)
- 입력된 음성 파일을 STT를 통해 text로 전환
- 판별 결과: 보이스피싱 가능성이 높음 (위험도: 92%)

- 근거:
    - '계좌 정지'와 같은 긴급성을 강조하는 표현이 포함됨
    - 사용자의 클릭을 유도하는 URL 포함됨



📌 Kollama를 활용한 보이스피싱 롤플레잉

- 보이스피싱 상황을 사용자가 선택 (ex:경찰 사칭, 은행원 사칭, 가족 협박 등)
- 응답생성시 RAG를 참조
- openAI STT & 일레븐랩스 TTS를 활용하여 실감나는 롤플레잉 지원
- 롤플레잉 종료후 올바른 대처인지 판단하여 피드백 제시



📌 Kollama를 활용한 보이스피싱 대처방안 제시

1. 개인정보가 상대에게 유출되었나요?
2. 보유 중인 계좌에서 돈이 인출되었나요?

위 보기를 제공하고 유저가 선택시 적절한 대응방안을 RAG를 참조해 대답 생성


------

## Architecture
![Image](https://github.com/user-attachments/assets/46866c51-6a8c-469d-b3da-9981e8bbfd32)