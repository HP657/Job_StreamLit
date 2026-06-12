import streamlit as st

from db import load_df
from utils.queries import COMPANY_SKILLS
from utils.recommendation import get_recommended_companies


def render(user_skills: list[str]) -> None:
    st.header("🏢 추천 기업")

    if not user_skills:
        st.info("보유 기술을 선택하면 추천 기업이 표시됩니다.")
        return

    company_df = load_df(COMPANY_SKILLS)
    recommend_df = get_recommended_companies(user_skills, company_df)

    if recommend_df.empty:
        st.warning("추천 가능한 기업 데이터가 없습니다.")
        return

    st.dataframe(recommend_df, use_container_width=True)

    top = recommend_df.iloc[0]
    st.success(f"가장 적합한 기업: {top['회사']} (매칭도 {top['매칭도']}%)")
