import streamlit as st
# 다른 파일들을 불러옵니다 (모듈로 사용)
from components import market_value, skill_gap, company_recommend 

st.set_page_config(page_title="채용 데이터 대시보드", layout="wide")

# 사이드바 설정 (모든 페이지 공통 적용)
with st.sidebar:
    st.header("필터 설정")
    selected_tech = st.multiselect("기술 스택", ["Python", "SQL", "Docker", "AWS"])
    date_range = st.date_input("조회 기간")
    st.markdown("---")
    show_raw = st.checkbox("데이터 상세 보기")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["시장 가치 분석", "스킬 갭 분석", "회사 추천"])

with tab1:
    st.subheader("시장 가치")
    # market_value.py의 메인 로직을 market_value.render() 등으로 함수화하여 호출
    market_value.render(selected_tech)

with tab2:
    st.subheader("스킬 갭")
    skill_gap.render(selected_tech)

with tab3:
    st.subheader("회사 추천")
    company_recommend.render(selected_tech)