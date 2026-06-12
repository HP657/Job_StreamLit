import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df

def get_heatmap_data(user_skill_map):
    selected_skills = list(user_skill_map.keys())
    
    # 선택된 기술이 있다면 SQL injection 방지용 이스케이프 처리 후 쿼리 생성
    if selected_skills:
        skill_name = selected_skills[0].replace("'", "''")
        order_by = f"""
        (SELECT COUNT(*) FROM job_opening_skills jos2 
         JOIN skills s2 ON jos2.skill_id = s2.id 
         WHERE jos2.job_opening_id = jo.id AND s2.name = '{skill_name}') DESC, 
        COUNT(*) DESC
        """
    else:
        order_by = "COUNT(*) DESC"

    query = f"""
    WITH TargetCompanies AS (
        SELECT company_name FROM job_openings 
        GROUP BY company_name 
        ORDER BY {order_by} LIMIT 25
    ),
    TargetSkills AS (
        SELECT s.name FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        GROUP BY s.name ORDER BY COUNT(*) DESC LIMIT 30
    )
    SELECT jo.company_name, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    WHERE jo.company_name IN (SELECT company_name FROM TargetCompanies)
      AND s.name IN (SELECT name FROM TargetSkills)
    GROUP BY jo.company_name, s.name
    """
    
    # 이제 수정된 db.py의 load_df가 params 없이도 안전하게 쿼리만 받아 실행합니다.
    return load_df(query)

def render(user_skill_map):
    st.header("🏢 기업별 핵심 기술 DNA 분석")
    df = get_heatmap_data(user_skill_map)
    if df.empty:
        st.warning("분석할 데이터가 부족합니다.")
        return

    heatmap_df = df.pivot(index='company_name', columns='skill_name', values='count').fillna(0)
    fig = px.imshow(heatmap_df, color_continuous_scale='Blues', aspect="auto")
    fig.update_layout(height=700, xaxis=dict(side="top"))
    st.plotly_chart(fig, use_container_width=True)