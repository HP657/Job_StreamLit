import streamlit as st

from db import load_df
from utils.queries import ALL_SKILLS, MARKET_DEMAND
import pages.market_value as market_value_page
import pages.skill_gap as skill_gap_page
import pages.company_recommend as company_recommend_page
import pages.trend_analysis as trend_analysis_page


st.set_page_config(page_title="시장 가치 분석", layout="wide")
st.title("📊 나의 시장 가치 분석")

# ── 공통 데이터 로드 ────────────────────────────────────────
all_skills = load_df(ALL_SKILLS)["name"].tolist()
market_df = load_df(MARKET_DEMAND)
market_dict = dict(zip(market_df["name"], market_df["demand_count"]))

# ── 사용자 입력 ─────────────────────────────────────────────
user_skills = st.multiselect("보유 기술 선택", all_skills)

st.divider()

# ── 페이지 렌더링 ───────────────────────────────────────────
market_value_page.render(user_skills, all_skills, market_dict)

st.divider()

skill_gap_page.render(user_skills)

st.divider()

company_recommend_page.render(user_skills)


st.divider()

trend_analysis_page.render()