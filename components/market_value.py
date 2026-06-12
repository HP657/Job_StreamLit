import streamlit as st

from db import load_df
from utils.queries import ALL_SKILLS, MARKET_DEMAND, SKILL_GROWTH
from utils.recommendation import (
    build_user_market_vectors,
    calc_market_match_score,
    calc_growth_rate,
)


def render(user_skills: list[str], all_skills: list[str], market_dict: dict) -> None:
    st.header("📊 나의 시장 가치")

    if not user_skills:
        st.info("보유 기술을 선택하면 시장 가치 분석이 표시됩니다.")
        return

    # ── 매칭률 ──────────────────────────────────────────────
    user_vec, market_vec = build_user_market_vectors(all_skills, user_skills, market_dict)
    match_score = calc_market_match_score(user_vec, market_vec)

    st.subheader("🏆 시장 매칭률")
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 기술 수", len(all_skills))
    col2.metric("선택 기술 수", len(user_skills))
    col3.metric("시장 매칭률", f"{match_score}%")
    st.progress(match_score / 100)

    # ── 성장 가속도 ─────────────────────────────────────────
    st.subheader("🚀 성장 가속도")

    growth_raw = load_df(SKILL_GROWTH)
    growth_df = calc_growth_rate(growth_raw)
    my_growth = growth_df[growth_df["name"].isin(user_skills)]
    avg_growth = round(my_growth["growth_rate"].mean(), 2)

    st.metric("최근 1개월 기술 성장률", f"{avg_growth}%")
    st.dataframe(
        my_growth[["name", "growth_rate"]].sort_values("growth_rate", ascending=False),
        use_container_width=True,
    )