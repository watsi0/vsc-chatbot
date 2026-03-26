# 📚 진로 연결 AI 도서 챗봇 - 실행 가이드

## 🚀 빠른 시작

### 1. 패키지 설치
```powershell
pip install -r requirements.txt
```

### 2. API 키 설정
`chatbot_server.py` 파일의 **22번 라인**을 수정하세요:

```python
GEMINI_API_KEY = "여기에_본인의_Gemini_API_키_입력"
```

**API 키 얻기:**
- https://aistudio.google.com 방문
- API 키 생성 후 복사

### 3. 서버 실행
```powershell
python chatbot_server.py
```

### 4. 브라우저에서 접속
```
http://127.0.0.1:5000
```

---

## 📋 필요한 파일

- `chatbot_server.py` - 백엔드 서버
- `chatbot_ui.html` - 프론트엔드 UI
- `requirements.txt` - 패키지 목록

---

## ⚙️ 시스템 요구사항

- Python 3.8 이상
- Windows / Mac / Linux
- 인터넷 연결 (Gemini API 호출용)

---

## 🔧 문제 해결

### 포트 5000이 이미 사용 중인 경우
`chatbot_server.py`의 마지막 라인 수정:
```python
app.run(debug=True, port=5001)  # 5000을 5001로 변경
```

### API 키 오류
- API 키가 정확한지 확인
- 특수문자나 공백이 없는지 확인

### 패키지 설치 오류
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📝 주요 기능

✅ 학생 프로필 맞춤 설정
✅ AI 도서 추천 (Gemini)
✅ 진로 로드맵 생성
✅ 대화 이력 저장
✅ 도서 검색

---

**문제가 있으면 터미널 로그를 확인해주세요!**
