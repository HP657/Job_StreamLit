import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df

def get_heatmap_data(user_skill_map):
    selected_skills = list(user_skill_map.keys())
    
    # 1. 파라미터 바인딩을 위한 준비
    params = []
    if selected_skills:
        skill_name = selected_skills[0]
        # 기술이 포함된 정렬 쿼리 (파라미터 사용)
        order_by = """
        (SELECT COUNT(*) FROM job_opening_skills jos2 
         JOIN skills s2 ON jos2.skill_id = s2.id 
         WHERE jos2.job_opening_id = jo.id AND s2.name = ?) DESC, 
        COUNT(*) DESC
        """
        params.append(skill_name)
    else:
        order_by = "COUNT(*) DESC"

    # 2. 쿼리 구성
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
    
    # 3. load_df에 params 전달
    return load_df(query, params=params)

def render(user_skill_map):
    st.header("🏢 기업별 핵심 기술 DNA 분석")
    
    df = get_heatmap_data(user_skill_map)
    
    if df.empty:
        st.warning("분석할 데이터가 부족합니다.")
        return

    heatmap_df = df.pivot(index='company_name', columns='skill_name', values='count').fillna(0)

    fig = px.imshow(
        heatmap_df, 
        labels=dict(x="기술", y="기업", color="빈도"),
        color_continuous_scale='Blues',
        aspect="auto"
    )
    
    fig.update_layout(
        xaxis=dict(side="top"),
        height=700,
        margin=dict(l=150, r=50, t=100, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 선택한 기술이 있을 경우 해당 기술 빈도순, 없을 경우 전체 공고 많은 순으로 정렬됩니다.")