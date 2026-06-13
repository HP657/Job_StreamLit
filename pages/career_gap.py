import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df, engine # engine도 import해야 합니다.

def get_career_skills(selected_skill=None):
    if selected_skill:
        # 안전하게 쿼리 실행을 위해 쿼리와 파라미터를 분리하는 것이 좋지만, 
        # 우선 안전하게 작은따옴표 문제를 피하도록 수정합니다.
        query = f"""
        SELECT s.name, jo.experience_level, COUNT(*) as count
        FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        JOIN job_openings jo ON jo.id = jos.job_opening_id
        WHERE jo.id IN (
            SELECT job_opening_id FROM job_opening_skills 
            JOIN skills ON skills.id = job_opening_skills.skill_id
            WHERE skills.name = :skill_name
        )
        GROUP BY s.name, jo.experience_level
        LIMIT 20
        """
        # pd.read_sql에 params를 전달하여 안전하게 실행
        return pd.read_sql(query, engine, params={"skill_name": selected_skill})
    else:
        query = """
        SELECT s.name, jo.experience_level, COUNT(*) as count
        FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        JOIN job_openings jo ON jo.id = jos.job_opening_id
        GROUP BY s.name, jo.experience_level
        ORDER BY count DESC
        LIMIT 15
        """
        return pd.read_sql(query, engine)

def render(all_skills):
    st.header("📈 경력 단계별 핵심 스킬 분석")
    
    selected = st.selectbox("분석할 기술 선택 (선택 안 하면 상위 기술 표시)", ["전체"] + all_skills)
    
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다.")
        return

    fig = px.bar(
        df, x="name", y="count", color="experience_level",
        title=f"{selected} 관련 경력별 요구 스택",
        template="plotly_dark",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 경력 단계별 상세 데이터")
    st.dataframe(df, use_container_width=True)