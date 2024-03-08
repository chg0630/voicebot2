import streamlit as st
# audiorecorder 패키지 추가
from audiorecorder import audiorecorder
# OpenAI 패키지 추가
import openai
# 파일 삭제를 위한 패키지 추가
import os
# 시간 정보를 위한 패키지 추가
from datetime import datetime
# TTS 패키지 추가
from gtts import gTTS
# 음원 파일을 재생하기 위한 패키지 추가
import base64

##### 기능 구현 함수 #####
def STT(audio):
    # 파일 저장
    filename = "input.mp3"
    audio.export(filename, format="mp3")

    # 음원 파일 열기
    audio_file = open(filename, "rb")

    # Whisper 모델을 활용해 텍스트 얻기
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()

    # 파일 삭제
    os.remove(filename)
    return transcript["text"]

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model = model, messages = prompt)
    gptResponse = response["choices"][0]["message"]
    return gptResponse["content"]

def TTS(response):
    # gTTS를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text = response, lang = "ko")
    tts.save(filename)

    # 음원 파일 자동 재생
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay = "True">
            <source src = "data:audio/mp3;base64,{b64}" type = "audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html = True,)

    # 파일 삭제
    os.remove(filename)

#### 메인 함수 ####
def main():

    # 기본 설정
    st.set_page_config(          # => 웹 브라우저에 표시할 타이틀과 레이아웃 설정
        page_title = "음성 비서 프로그램",  # 웹 브라우저의 탭에 표시할 제목 설정
        layout = "wide")         # 콘텐츠를 넓게 배치하도록 설정
    
    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role" : "system", "content" : "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False
    
    # 제목
    st.header("음성 비서 프로그램")  # 제목 작성

    # 구분선
    st.markdown("---")

    # 기본 설명
    with st.expander("음성 비서 프로그램에 관하여", expanded = True):  
          # st.expander()로 감싸 설명 영역에 있는 내용들을 접거나 펼 수 있음
        st. write(    # 프로그램 설명 입력
        """
        - 음성 비서 프로그램의 UI는 스트림릿을 활용하였습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용하였습니다.
        - 답변은 OpenAI의 GPT 모델을 활용하였습니다.
        - TTS(Text-To-Speech)는 Google Translate TTS를 활용하였습니다.
        """
        )

        st.markdown("")

    # 사이드바 생성
    with st.sidebar:   # 들여쓰기하여 작성된 코드는 모두 사이드바 안쪽 공간에 생성
        
        # Open AI API 키 입력받기
        openai.api_key = st.text_input(label = "OPENAI API 키", placeholder = "Enter Your API Key", value = "", type = "password")
                                 # 텍스트 입력창 생성 / 텍스트 입력창 위에 표시할 라벨 / 텍스트 입력 창 안에 표시할 설명 문구 / 타입을 "password"로 하면 값이 가려짐        
        st.markdown("---")

        # GPT 모델을 선택하기 위한 라디오 버튼 생성
        model = st.radio(label = "GPT 모델", options = ["gpt-4", "gpt-3.5-turbo"])
                    # 라디오 버튼 위에 표시할 라벨 / 추가할 라디오 버튼을 리스트 형태로 입력
        st.markdown("---")

        # 리셋 버튼 생성
        if st.button(label = "초기화"):   # 초기화 버튼 누르면 session_state 초기화
            # 리셋 코드
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role" : "system", "content" : "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True

    # 기능 구현 공간
    col1, col2 = st.columns(2)  # 기능 구현 영역을 두 개의 영역으로 분할 / 각 영역의 이름은 col1, col2로 지정
    with col1:  
        # 왼쪽 영역 작성
        st.subheader("질문하기")
        # 음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):  # 음성 녹음이 들어왔는지 판단
            # 음성 재생
            st.audio(audio.export().read())  # 녹음 결과를 다시 들어볼 수 있도록 구현
           
            # 음성 파일에서 텍스트 추출
            question = STT(audio)

            # 채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]

            # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role" : "user", "content" : question}]

    with col2:
        # 오른쪽 영역 작성
        st.subheader("질문/답변")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # ChatGPT에게 답변 얻기
            response = ask_gpt(st.session_state["messages"], model)

            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role" : "system", "content" : response}]

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # 채팅 형식으로 시각화하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html = True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html = True)
                    st.write("")

            # gTTS를 활용하여 음성 파일 생성 및 재생
            TTS(response)

if __name__ == "__main__":
    main()