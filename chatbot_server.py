# -*- coding: utf-8 -*-
# =============================================
# 📚 진로 연결 AI 도서 챗봇 - Gemini 버전
#
# 설치:  pip install google-generativeai flask flask-cors requests
# 실행:  python chatbot_server.py
# =============================================

import json
import re
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =============================================
# 🔑 API 키 입력
# =============================================
GEMINI_API_KEY = "AIzaSyAFdhHL69ZmNDfup9QJIElvf5mmLI2yk84"   # aistudio.google.com
ALADIN_API_KEY = "여기에_알라딘_API_키_입력"    # 없으면 그냥 놔둬도 됨

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# 메모리 저장소
student_profiles       = {}
conversation_histories = {}

LEVEL_DESCRIPTIONS = {
    "입문": "해당 분야를 처음 접하는 사람용. 쉬운 말, 이야기 중심, 전문 용어 최소화.",
    "중급": "기초 지식은 있지만 더 깊이 공부하고 싶은 학생용. 개념·원리 위주.",
    "심화": "전공 수준의 깊이 있는 내용을 원하는 학생용. 논문·전공서 수준도 포함."
}

def build_system_prompt(profile):
    name   = profile.get("name", "학생")
    grade  = profile.get("grade", "고3")
    career = profile.get("career", "미정")
    level  = profile.get("level", "입문")
    ldesc  = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["입문"])

    return f"""
너는 '{name}'의 진로 맞춤 도서 멘토야. 이름은 '북이'야.

[학생 정보]
- 이름: {name} / 학년: {grade}학년 / 희망 진로: {career} / 독서 수준: {level}
- 수준 기준: {ldesc}

[3가지 핵심 역할]
1. 수준 맞춤 추천: 반드시 {level} 수준에 맞는 책만 추천. 너무 어렵거나 쉬운 책은 제외.
2. 진로 연결 설명: 추천 책이 '{career}' 진로와 어떻게 연결되는지 한 문장으로 반드시 설명.
3. 다음 행동 제안: 책 읽은 후 할 수 있는 구체적 행동 1~2개를 항상 제안.

[말투] 친근하되 신뢰감 있게. {name}을 가끔 이름으로 불러줘. 500자 이내 권장.
[금지] 행동 제안 없이 책만 나열 금지. 진로 연결 설명 생략 금지.
항상 한국어로 대답해.
"""

def build_roadmap_prompt(profile):
    return f"""
다음 학생의 진로 로드맵을 3단계로 만들어줘.

학생: {profile.get('grade')}학년 / 진로: {profile.get('career')} / 수준: {profile.get('level')}

반드시 아래 JSON 형식만 출력해. 다른 말은 하지 마.

{{
  "roadmap": [
    {{
      "stage": "1단계",
      "title": "기초 다지기",
      "period": "지금 ~ 3개월",
      "goal": "이 단계 핵심 목표 한 문장",
      "books": ["책 제목 1", "책 제목 2"],
      "actions": ["구체적 행동 1", "구체적 행동 2"]
    }},
    {{
      "stage": "2단계",
      "title": "심화 학습",
      "period": "3 ~ 6개월",
      "goal": "이 단계 핵심 목표 한 문장",
      "books": ["책 제목 1", "책 제목 2"],
      "actions": ["구체적 행동 1", "구체적 행동 2"]
    }},
    {{
      "stage": "3단계",
      "title": "실전 준비",
      "period": "6개월 이후",
      "goal": "이 단계 핵심 목표 한 문장",
      "books": ["책 제목 1", "책 제목 2"],
      "actions": ["구체적 행동 1", "구체적 행동 2"]
    }}
  ],
  "advice": "{profile.get('name', '학생')}에게 한 마디 조언"
}}
"""

def search_books(query, max_results=5):
    try:
        res = requests.get(
            "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx",
            params={
                "ttbkey": ALADIN_API_KEY, "Query": query,
                "QueryType": "Keyword", "MaxResults": max_results,
                "SearchTarget": "Book", "output": "js", "Version": "20131101"
            },
            timeout=5
        )
        return [{
            "title":       b.get("title", ""),
            "author":      b.get("author", ""),
            "publisher":   b.get("publisher", ""),
            "description": b.get("description", "")[:180],
            "cover":       b.get("cover", ""),
            "link":        b.get("link", "")
        } for b in res.json().get("item", [])]
    except:
        return []

def books_to_text(books):
    out = "=== 도서 검색 결과 ===\n\n"
    for i, b in enumerate(books, 1):
        out += f"{i}. 《{b['title']}》 — {b['author']}\n   {b['description']}\n\n"
    return out


@app.route("/")
def index():
    return open("chatbot_ui.html", encoding="utf-8").read()


@app.route("/profile", methods=["POST"])
def set_profile():
    data    = request.json
    user_id = data.get("user_id", "default")
    student_profiles[user_id] = {
        "name":   data.get("name", "학생"),
        "grade":  data.get("grade", "고3"),
        "career": data.get("career", "미정"),
        "level":  data.get("level", "입문")
    }
    conversation_histories[user_id] = []
    return jsonify({"status": "ok", "profile": student_profiles[user_id]})


@app.route("/roadmap", methods=["POST"])
def get_roadmap():
    data    = request.json
    user_id = data.get("user_id", "default")
    profile = student_profiles.get(user_id,
        {"name": "학생", "grade": "고3", "career": "미정", "level": "입문"})

    try:
        response = model.generate_content(build_roadmap_prompt(profile))
        raw      = response.text
        clean    = re.sub(r"```(?:json)?|```", "", raw).strip()
        parsed   = json.loads(clean)
        return jsonify({"status": "ok", **parsed})
    except Exception as e:
        print(f"[로드맵 오류] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    data         = request.json
    user_id      = data.get("user_id", "default")
    user_message = data.get("message", "").strip()
    search_query = data.get("search_query", "")

    if not user_message:
        return jsonify({"error": "메시지 없음"}), 400

    profile = student_profiles.get(user_id,
        {"name": "학생", "grade": "고3", "career": "미정", "level": "입문"})

    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    book_results = []
    full_msg     = user_message
    if search_query:
        book_results = search_books(search_query)
        full_msg     = f"{user_message}\n\n{books_to_text(book_results)}"

    system_prompt  = build_system_prompt(profile)
    history        = conversation_histories[user_id]

    try:
        # 간단한 프롬프트 (히스토리 제거)
        final_prompt = f"{system_prompt}\n\n사용자: {full_msg}"
        
        print(f"[요청] {user_id}: {user_message[:50]}")
        response = model.generate_content(final_prompt)
        reply = response.text
        print(f"[응답] {reply[:50]}")
        
        conversation_histories[user_id].append({"role": "user",      "content": full_msg})
        conversation_histories[user_id].append({"role": "assistant", "content": reply})

        if len(conversation_histories[user_id]) > 20:
            conversation_histories[user_id] = conversation_histories[user_id][-20:]

        return jsonify({"reply": reply, "books": book_results, "profile": profile})
    except Exception as e:
        print(f"[채팅 오류] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/clear", methods=["POST"])
def clear():
    user_id = request.json.get("user_id", "default")
    conversation_histories.pop(user_id, None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("=" * 55)
    print("📚 진로 연결 AI 도서 챗봇 서버 시작! (Gemini)")
    print("   http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)