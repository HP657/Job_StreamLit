import streamlit as st
from db import load_df
from utils.queries import ALL_SKILLS, MARKET_DEMAND

# 루트 디렉토리의 modules 폴더에서 호출
from modules import market_value, skill_gap, company_recommend, skill_network, company_heatmap, career_gap

st.set_page_config(page_title="커리어 대시보드", layout="wide")

# 사이드바 자동 메뉴 숨김 (파일 이름 안 보이게 함)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 개발자 맞춤형 커리어 분석 대시보드")

# 데이터 로드
all_skills = load_df(ALL_SKILLS)["name"].tolist()
market_df = load_df(MARKET_DEMAND)
market_dict = dict(zip(market_df["name"], market_df["demand_count"]))

# 사이드바 프로필 설정
st.sidebar.header("👤 나의 프로필 설정")
selected_skills = st.sidebar.multiselect("보유 기술 선택", all_skills)
user_skill_map = {skill: 0.5 if st.sidebar.radio(f"{skill} 숙련도", ["초급", "숙련"], key=f"level_{skill}", horizontal=True) == "초급" else 1.0 for skill in selected_skills}

# 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 역량 갭", "🔗 네트워크", "📊 경력 단계별 분석", "💰 시장 가치", "🏢 기업 추천", "🏢 기업 기술 DNA"
])

# 렌더링
with tab1: skill_gap.render(user_skill_map)
with tab2: skill_network.render(user_skill_map)
with tab3: career_gap.render(all_skills)
with tab4: market_value.render(user_skill_map, all_skills, market_dict)
with tab5: company_recommend.render(user_skill_map)
with tab6: company_heatmap.render(user_skill_map)

st.markdown("---")
st.caption("본 대시보드는 실시간 채용 공고 데이터를 분석하여 최적의 학습 경로를 제시합니다.")
