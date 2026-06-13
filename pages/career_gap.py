import streamlit as st
import plotly.express as px
from db import load_df

def get_career_skills(selected_skill=None):
    if selected_skill:
        # 선택한 기술과 함께 등장하는 기술들(상위 15개)을 조회하는 쿼리
        query = f"""
        WITH RelatedJobs AS (
            SELECT job_opening_id FROM job_opening_skills 
            WHERE skill_id = (SELECT id FROM skills WHERE name = '{selected_skill}')
        )
        SELECT s.name, jo.experience_level, COUNT(*) as count
        FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        JOIN job_openings jo ON jo.id = jos.job_opening_id
        WHERE jo.id IN (SELECT job_opening_id FROM RelatedJobs)
        GROUP BY s.name, jo.experience_level
        """
    else:
        # 평소에는 전체 상위 15개 기술만 조회
        query = """
        SELECT s.name, jo.experience_level, COUNT(*) as count
        FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        JOIN job_openings jo ON jo.id = jos.job_opening_id
        WHERE s.name IN (SELECT name FROM skills ORDER BY id LIMIT 15)
        GROUP BY s.name, jo.experience_level
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