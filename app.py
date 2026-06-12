import streamlit as st
import os

# 1. 페이지 설정 (인구 대시보드 스타일)
st.set_page_config(
    page_title="채용 데이터 대시보드",
    page_icon="📊",
    layout="wide",
)

# 2. 사이드바 구성 (인구 대시보드 스타일)
with st.sidebar:
    st.header("⚙️ 설정")
    # 예시: 인구 대시보드의 '연도/성별' 필터처럼 기술 필터 추가
    selected_tech = st.multiselect("분석할 기술 스택 선택", ["Python", "SQL", "Docker", "AWS"])
    
    st.divider()
    
    st.subheader("보기 옵션")
    show_raw = st.checkbox("원본 데이터 보기", value=False)
    
    st.info("기술 스택을 선택하면 대시보드가 자동으로 업데이트됩니다.")

# 3. 메인 제목
st.title("📊 채용 데이터 통합 대시보드")
st.write("기술 스택별 시장 가치와 스킬 갭을 한눈에 확인하세요.")

# 4. 탭 구성 (페이지 이동 대신 탭으로 깔끔하게 통합)
tab1, tab2, tab3 = st.tabs(["시장 가치 분석", "스킬 갭 분석", "회사 추천"])

with tab1:
    st.subheader("시장 가치 데이터")
    # 여기에 기존 market_value 로직을 넣거나 불러오세요.
    
with tab2:
    st.subheader("스킬 갭 분석")
    
with tab3:
    st.subheader("추천 기업 목록")