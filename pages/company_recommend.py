import streamlit as st

<<<<<<< Updated upstream
from db import load_df
from utils.queries import COMPANY_SKILLS, EXPERIENCE_SKILL_COUNT
=======
from utils.analysis import safe_load_df
from utils.queries import COMPANY_SKILLS
>>>>>>> Stashed changes
from utils.recommendation import get_recommended_companies
from utils.graphs import build_company_heatmap, build_experience_bar_chart


def render(user_skills: list[str]) -> None:
    st.header("🏢 추천 기업")

    if not user_skills:
        st.info("보유 기술을 선택하면 추천 기업이 표시됩니다.")
        return

    company_df = safe_load_df(COMPANY_SKILLS)
    recommend_df = get_recommended_companies(user_skills, company_df)

    if recommend_df.empty:
        st.warning("추천 가능한 기업 데이터가 없습니다.")
        return

    st.dataframe(recommend_df, use_container_width=True)

    st.subheader("🧬 기업별 기술 DNA")
    st.plotly_chart(build_company_heatmap(company_df), use_container_width=True)

    st.subheader("📊 경력 단계별 핵심 스킬 비교")
    experience_df = load_df(EXPERIENCE_SKILL_COUNT)
    st.plotly_chart(build_experience_bar_chart(experience_df), use_container_width=True)

    top = recommend_df.iloc[0]
    st.success(f"가장 적합한 기업: {top['회사']} (매칭도 {top['매칭도']}%)")