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
    
    with st.expander("💡 시장 가치 및 수요 분석 로직 자세히 보기"):
        st.markdown("""
        현재 보유한 기술 스택이 시장에서 가지는 경제적 가치와 수요를 분석합니다.
        
        1. **수요 점수 산출**: 채용 공고 내 각 기술의 출현 빈도를 카운팅하여 시장의 표준 수요도를 수치화합니다.
        2. **개인 가치 측정**: 사용자의 기술 스택 점수와 시장 수요도를 결합하여, 보유 기술이 시장에서 차지하는 경쟁력을 계산합니다.
        3. **시장 가치 가중치**: 채용 규모가 큰 기업에서 요구하는 기술에 가중치를 부여하여 실질적인 시장 가치를 도출합니다.
        
        이 데이터를 통해 사용자는 현재 나의 기술들이 시장에서 어느 정도의 입지를 가지고 있는지 파악할 수 있습니다.
        """)

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

    # 3. 💡 기술 시장 포지셔닝
    st.subheader("💡 기술 시장 포지셔닝")
    bubble_df = get_bubble_data()
    
    # 선택 여부 컬럼 추가 (색상 구분을 위해)
    bubble_df['선택 여부'] = bubble_df['skill_name'].apply(
        lambda x: '나의 기술' if x in user_skills else '기타 기술'
    )
    
    # 버블 차트 생성
    fig = px.scatter(
        bubble_df, 
        x="희소성", 
        y="demand", 
        size="demand", 
        color="선택 여부",
        hover_name="skill_name",
        # 이전의 보기 편한 색상으로 복구
        color_discrete_map={'나의 기술': '#FF4B4B', '기타 기술': '#1f77b4'}, 
        size_max=50,
        template="plotly_dark",
        title="기술 희소성 vs 시장 수요"
    )
    
    # 테두리 강조만 유지
    fig.update_traces(
        marker=dict(sizemin=10, line=dict(width=2, color='white')),
        opacity=0.8
    )
    
    fig.update_layout(
        xaxis_title="기술 희소성 (낮을수록 보편적, 높을수록 희귀함)",
        yaxis_title="시장 수요 (채용 공고 수)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("빨간색 버블로 표시된 항목이 현재 보유하신 기술입니다.")