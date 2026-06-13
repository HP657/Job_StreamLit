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

def render(all_skills): # app.py에서 all_skills 리스트를 넘겨줘야 합니다
    st.header("📈 경력 단계별 핵심 스킬 분석")
    
    # 사이드바에서 기술 선택
    selected = st.selectbox("분석할 기술 선택 (선택 안 하면 상위 기술 표시)", ["전체"] + all_skills)
    
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 그래프 그리기
    fig = px.bar(
        df, x="name", y="count", color="experience_level",
        title=f"{selected} 관련 핵심 스킬 비교",
        template="plotly_dark",
        barmode="stack"
    )
    
    st.plotly_chart(fig, use_container_width=True)