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
        이 분석은 사용자의 기술 스택이 시장에서 어느 정도의 경쟁력을 갖는지 입체적으로 평가합니다.
        
        **1. 🏆 시장 매칭률 (Market Match Score)**
        - **의미**: 전체 시장에서 요구하는 핵심 기술 스택 분포와 사용자의 기술 분포가 얼마나 일치하는지를 나타내는 지표입니다.
        - **분석 방식**: 시장 전체의 기술 요구 벡터와 사용자의 보유 기술 벡터를 코사인 유사도(Cosine Similarity)로 계산합니다. 100%에 가까울수록 시장 트렌드에 최적화된 기술 조합을 갖추고 있음을 의미합니다.
        
        **2. 🚀 성장 가속도 (Growth Acceleration)**
        - **의미**: 현재 보유한 기술들이 시장에서 채용 공고가 늘어나는 속도(성장률)의 평균치입니다.
        - **분석 방식**: 최근 기간 동안의 공고 데이터 변화량을 기반으로, 정체된 기술인지 아니면 시장에서 급격히 수요가 폭발하는 기술인지를 판별합니다. 높은 값은 미래 가치가 높은 기술을 보유하고 있음을 시사합니다.
        
        **3. 💡 기술 시장 포지셔닝 (Bubble Map)**
        - **의미**: 기술의 '희소성'과 '시장 수요(범용성)'를 2차원 평면에서 비교합니다.
        - **해석**: 
            - 우상단(고수요·고희소성): 시장에서 매우 가치가 높은 '핵심 전략 기술'
            - 좌상단(보편적·고수요): 안정적인 취업을 위한 '기본 필수 기술'
            - 우하단(희소기술): 특정 분야에서만 쓰이는 '니치(Niche) 기술'
        
        
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