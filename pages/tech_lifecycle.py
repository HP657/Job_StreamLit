import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from db import load_df

def get_lifecycle_data():
    # 월별/기술별 채용 공고 수 추출
    query = """
    SELECT DATE_TRUNC('month', jo.created_at) AS month, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    ORDER BY 1 ASC
    """
    return load_df(query)

def render():
    st.header("⏳ 기술 생애주기 분석")
    df = get_lifecycle_data()
    
    if df.empty:
        st.warning("데이터가 부족합니다.")
        return

    # 상위 5개 주요 기술만 필터링하여 시각화
    top_skills = df.groupby('skill_name')['count'].sum().nlargest(5).index
    df_filtered = df[df['skill_name'].isin(top_skills)]

    # 이중 축 차트 생성 (선 그래프)
    fig = go.Figure()
    for skill in top_skills:
        skill_data = df_filtered[df_filtered['skill_name'] == skill]
        fig.add_trace(go.Scatter(x=skill_data['month'], y=skill_data['count'], mode='lines+markers', name=skill))

    fig.update_layout(
        title="주요 기술 스택의 시간 흐름에 따른 수요 변화",
        xaxis_title="기간",
        yaxis_title="채용 공고 수",
        hovermode="x unified",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 **해석 가이드:** 우상향 곡선은 '성장기/성숙기' 기술, 하향 곡선은 '쇠퇴기' 기술로 판단하여 학습 우선순위를 조정하세요.")