import streamlit as st
from db import load_df
from utils.queries import ALL_SKILLS, MARKET_DEMAND
from modules import (
    market_value, skill_gap, company_recommend, 
    skill_network, company_heatmap, career_gap, architecture
)

# 페이지 설정
st.set_page_config(page_title="커리어 분석 대시보드", layout="wide")

# 사이드바 스타일 및 내장 메뉴 숨김
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 1. 세션 상태 초기화 (메뉴 상태 유지)
if 'current_menu' not in st.session_state:
    st.session_state.current_menu = "🎯 역량 갭"

# 데이터 로드
all_skills = load_df(ALL_SKILLS)["name"].tolist()
market_df = load_df(MARKET_DEMAND)
market_dict = dict(zip(market_df["name"], market_df["demand_count"]))

# --- 사이드바 영역 ---
st.sidebar.title("🚀 분석 도구")

# 프로필 설정
st.sidebar.header("👤 나의 프로필")
selected_skills = st.sidebar.multiselect("보유 기술 선택", all_skills, label_visibility="collapsed")
user_skill_map = {}
with st.sidebar.container(border=True):
    st.caption("기술 숙련도 설정")
    for skill in selected_skills:
        level = st.radio(f"{skill}", ["초급", "숙련"], key=f"level_{skill}", horizontal=True)
        user_skill_map[skill] = 0.5 if level == "초급" else 1.0

st.sidebar.markdown("---")

# 메뉴 디자인 (버튼 기반)
st.sidebar.markdown("### 📋 분석 대시보드")
menu_items = [
    "🎯 역량 갭", "🔗 네트워크", "📊 경력 단계별 분석", 
    "💰 시장 가치", "🏢 기업 추천", "🏢 기업 기술 DNA", "🏗️ 아키텍처"
]

for label in menu_items:
    if st.sidebar.button(label, use_container_width=True, type="primary" if st.session_state.current_menu == label else "secondary"):
        st.session_state.current_menu = label
        st.rerun()

# --- 메인 영역 렌더링 ---
st.title(f"{st.session_state.current_menu} 분석")

if st.session_state.current_menu == "🎯 역량 갭": 
    skill_gap.render(user_skill_map)
elif st.session_state.current_menu == "🔗 네트워크": 
    skill_network.render(user_skill_map)
elif st.session_state.current_menu == "📊 경력 단계별 분석": 
    career_gap.render(all_skills)
elif st.session_state.current_menu == "💰 시장 가치": 
    market_value.render(user_skill_map, all_skills, market_dict)
elif st.session_state.current_menu == "🏢 기업 추천": 
    company_recommend.render(user_skill_map)
elif st.session_state.current_menu == "🏢 기업 기술 DNA": 
    company_heatmap.render(user_skill_map)
elif st.session_state.current_menu == "🏗️ 아키텍처": 
    architecture.render()

st.sidebar.markdown("---")
st.sidebar.caption("본 대시보드는 실시간 채용 공고 데이터를 분석하여 최적의 학습 경로를 제시합니다.")