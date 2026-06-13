import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill=None):
    try:
        with engine.connect() as conn:
            if selected_skill:
                # 쿼리를 최대한 단순화하여 검증
                sql = text("""
                SELECT s.name, jo.experience_level, COUNT(*) as count
                FROM job_opening_skills jos
                JOIN skills s ON s.id = jos.skill_id
                JOIN job_openings jo ON jo.id = jos.job_opening_id
                WHERE jos.job_opening_id IN (
                    SELECT job_opening_id FROM job_opening_skills 
                    JOIN skills ON skills.id = job_opening_skills.skill_id
                    WHERE skills.name = :skill_name
                )
                GROUP BY s.name, jo.experience_level
                LIMIT 20
                """)
                return pd.read_sql(sql, conn, params={"skill_name": selected_skill})
            else:
                sql = text("""
                SELECT s.name, jo.experience_level, COUNT(*) as count
                FROM job_opening_skills jos
                JOIN skills s ON s.id = jos.skill_id
                JOIN job_openings jo ON jo.id = jos.job_opening_id
                GROUP BY s.name, jo.experience_level
                ORDER BY count DESC
                LIMIT 15
                """)
                return pd.read_sql(sql, conn)
    except Exception as e:
        st.error(f"데이터베이스 조회 실패: {str(e)}")
        return pd.DataFrame()

def render(all_skills):
    st.header("📈 경력 단계별 핵심 스킬 분석")
    
    selected = st.selectbox("분석할 기술 선택 (선택 안 하면 상위 기술 표시)", ["전체"] + all_skills)
    
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("데이터가 없거나 조회에 실패했습니다.")
        return

    # 그래프 생성
    fig = px.bar(
        df, x="name", y="count", color="experience_level",
        title=f"{selected if selected != '전체' else '전체 기술'} 관련 경력별 요구 스택",
        template="plotly_dark",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 경력 단계별 상세 데이터")
    st.dataframe(df, use_container_width=True)