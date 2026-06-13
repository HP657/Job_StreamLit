import streamlit as st
from db import load_df
from utils.queries import ALL_SKILLS, MARKET_DEMAND

# 모든 페이지 모듈 import
import pages.market_value as market_value_page
import pages.skill_gap as skill_gap_page
import pages.company_recommend as company_recommend_page
import pages.skill_network as skill_network_page
import pages.company_heatmap as company_heatmap_page
import pages.career_gap as career_gap_page
import pages.tech_lifecycle as tech_lifecycle_page

st.set_page_config(page_title="개발자 커리어 대시보드", layout="wide")
st.title("🚀 개발자 맞춤형 커리어 분석 대시보드")

# 공통 데이터 로드
all_skills = load_df(ALL_SKILLS)["name"].tolist()
market_df = load_df(MARKET_DEMAND)
market_dict = dict(zip(market_df["name"], market_df["demand_count"]))

# 사이드바 입력
st.sidebar.header("👤 나의 프로필 설정")
selected_skills = st.sidebar.multiselect("보유 기술 선택", all_skills)
user_skill_map = {skill: 0.5 if st.sidebar.radio(f"{skill} 숙련도", ["초급", "숙련"], key=f"level_{skill}", horizontal=True) == "초급" else 1.0 for skill in selected_skills}


tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📈 트렌드", 
    "🎯 역량 갭", 
    "🔗 네트워크", 
    "📊 경력 단계별 분석",
    "💰 시장 가치", 
    "🏢 기업 분석", 
    "🏢 기업 기술 DNA",
    "⏳ 기술 생애주기"
])

with tab1: trend_analysis_page.render()
with tab2: skill_gap_page.render(user_skill_map)
with tab3: skill_network_page.render(user_skill_map)
with tab4: career_gap_page.render() # 경력 단계별 분석
with tab5: market_value_page.render(user_skill_map, all_skills, market_dict)
with tab6: company_recommend_page.render(user_skill_map)
with tab7: company_heatmap_page.render(user_skill_map)
with tab8: tech_lifecycle_page.render()

st.markdown("---")
st.caption("본 대시보드는 실시간 채용 공고 데이터를 분석하여 최적의 학습 경로를 제시합니다.")