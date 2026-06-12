import streamlit as st

from utils.analysis import safe_load_df
from utils.queries import ALL_SKILLS, MARKET_DEMAND
import pages.market_value as market_value_page
import pages.skill_gap as skill_gap_page
import pages.company_recommend as company_recommend_page
import pages.market_trend as market_trend_page
import pages.skill_network as skill_network_page
import pages.company_dna as company_dna_page
import pages.experience_skill as experience_skill_page
import pages.tech_lifecycle as tech_lifecycle_page


st.set_page_config(page_title="시장 가치 분석", layout="wide")
st.title("📊 나의 시장 가치 분석")

# ── 공통 데이터 로드 ────────────────────────────────────────
all_df = safe_load_df(ALL_SKILLS)
all_skills = all_df["name"].tolist() if not all_df.empty else []
market_df = safe_load_df(MARKET_DEMAND)
market_dict = dict(zip(market_df["name"], market_df["demand_count"])) if not market_df.empty else {}

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

market_trend_page.render()

st.divider()

skill_network_page.render()

st.divider()

company_dna_page.render()

st.divider()

experience_skill_page.render()

st.divider()

tech_lifecycle_page.render()