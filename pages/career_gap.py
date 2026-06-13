import streamlit as st
import plotly.express as px
from db import load_df

def get_career_data():
    # 경력/신입 구분별 상위 5개 기술 분석
    query = """
    SELECT s.name AS skill_name, jo.experience, COUNT(*) AS frequency
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    WHERE jo.experience IS NOT NULL
    GROUP BY s.name, jo.experience
    ORDER BY frequency DESC
    """
    return load_df(query)

def render():
    st.header("📊 경력 단계별 핵심 스킬 분석")
    
    df = get_career_data()
    if df.empty:
        st.warning("경력 데이터가 없습니다.")
        return

    # 그래프 생성
    fig = px.bar(
        df, 
        x="skill_name", 
        y="frequency", 
        color="experience", 
        barmode="group",
        title="신입 vs 경력직 선호 기술 비교",
        labels={"frequency": "공고 언급 횟수", "skill_name": "기술 스택", "experience": "경력 구분"}
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.info("신입 공고에서 유독 빈도가 높은 기술을 파악하여 취업 준비의 우선순위를 결정하세요.")