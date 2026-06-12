import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df
from utils.queries import SKILL_GROWTH
from utils.recommendation import (
    build_user_market_vectors,
    calc_market_match_score,
    calc_growth_rate,
)

def get_bubble_data():
    # 기술별 시장 수요와 희소성을 계산하는 쿼리
    query = """
    SELECT s.name as skill_name, 
           COUNT(*) as demand,
           (SELECT COUNT(*) FROM job_openings) as total_jobs
    FROM job_opening_skills jos
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY s.name
    """
    df = load_df(query)
    # 희소성 점수 (전체 대비 비율이 낮을수록 우측으로)
    df['rarity'] = (1 - (df['demand'] / df['total_jobs'])) * 100
    return df

def render(user_skills: list[str], all_skills: list[str], market_dict: dict) -> None:
    st.header("📊 나의 시장 가치")

    if not user_skills:
        st.info("사이드바에서 보유 기술을 선택하면 시장 가치 분석이 표시됩니다.")
        return

    # 1. 기존 매칭률 로직
    user_vec, market_vec = build_user_market_vectors(all_skills, user_skills, market_dict)
    match_score = calc_market_match_score(user_vec, market_vec)

    st.subheader("🏆 시장 매칭률")
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 기술 수", len(all_skills))
    col2.metric("선택 기술 수", len(user_skills))
    col3.metric("시장 매칭률", f"{match_score}%")
    st.progress(match_score / 100)

    # 2. 기존 성장 가속도 로직
    st.subheader("🚀 성장 가속도")
    growth_raw = load_df(SKILL_GROWTH)
    growth_df = calc_growth_rate(growth_raw)
    my_growth = growth_df[growth_df["name"].isin(user_skills)]
    avg_growth = round(my_growth["growth_rate"].mean(), 2)

    st.metric("보유 기술 평균 성장률", f"{avg_growth}%")
    st.dataframe(my_growth[["name", "growth_rate"]].sort_values("growth_rate", ascending=False), use_container_width=True)

    # 3. 추가된 버블 차트 시각화
    st.subheader("💡 기술 시장 포지셔닝")
    bubble_df = get_bubble_data()
    fig = px.scatter(
        bubble_df, x="rarity", y="demand", size="demand", color="skill_name",
        hover_name="skill_name", size_max=60, title="기술 희소성 vs 시장 수요",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("희소성 점수가 높을수록 시장에서 찾기 힘든 전문 기술이며, 수요가 높을수록 채용 기회가 많습니다.")