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
    query = """
    SELECT s.name as skill_name, 
           COUNT(*) as demand,
           (SELECT COUNT(*) FROM job_openings) as total_jobs
    FROM job_opening_skills jos
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY s.name
    """
    df = load_df(query)
    # 희소성 계산
    df['희소성'] = (1 - (df['demand'] / df['total_jobs'])) * 100
    return df

def render(user_skills: list[str], all_skills: list[str], market_dict: dict) -> None:
    st.header("📊 나의 시장 가치")

    if not user_skills:
        st.info("사이드바에서 보유 기술을 선택하면 시장 가치 분석이 표시됩니다.")
        return

    # 1. 🏆 시장 매칭률
    user_vec, market_vec = build_user_market_vectors(all_skills, user_skills, market_dict)
    match_score = calc_market_match_score(user_vec, market_vec)

    st.subheader("🏆 시장 매칭률")
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 기술 수", len(all_skills))
    col2.metric("선택 기술 수", len(user_skills))
    col3.metric("시장 매칭률", f"{match_score}%")
    st.progress(match_score / 100)

    # 2. 🚀 성장 가속도
    st.subheader("🚀 성장 가속도")
    growth_raw = load_df(SKILL_GROWTH)
    growth_df = calc_growth_rate(growth_raw)
    my_growth = growth_df[growth_df["name"].isin(user_skills)]
    avg_growth = round(my_growth["growth_rate"].mean(), 2)

    st.metric("보유 기술 평균 성장률", f"{avg_growth}%")
    st.dataframe(
        my_growth[["name", "growth_rate"]].sort_values("growth_rate", ascending=False),
        use_container_width=True
    )

    # 3. 💡 기술 시장 포지셔닝 (세련된 컬러 팔레트 적용)
    st.subheader("💡 기술 시장 포지셔닝")
    bubble_df = get_bubble_data()
    
    # 선택 여부 컬럼 추가
    bubble_df['선택 여부'] = bubble_df['skill_name'].apply(
        lambda x: '나의 기술' if x in user_skills else '기타 기술'
    )
    
    # 세련된 색상 매핑
    fig = px.scatter(
        bubble_df, 
        x="희소성", 
        y="demand", 
        size="demand", 
        color="선택 여부",
        hover_name="skill_name",
        color_discrete_map={'나의 기술': '#FF6B6B', '기타 기술': '#4ECDC4'}, 
        size_max=60,
        title="기술 희소성 vs 시장 수요",
        template="plotly_dark"
    )
    
    # 미적 요소 향상
    fig.update_traces(
        marker=dict(line=dict(width=1, color='white')),
        opacity=0.85
    )
    
    fig.update_layout(
        xaxis_title="기술 희소성 (우측으로 갈수록 전문가용)",
        yaxis_title="시장 수요 (채용 공고 수)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("강조된 색상은 현재 보유하신 기술을 나타냅니다.")