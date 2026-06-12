import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df

def get_heatmap_data(user_skill_map):
    # 사용자가 선택한 기술이 있는지 확인 (가장 많이 선택된 기술 하나를 기준으로 정렬)
    selected_skills = list(user_skill_map.keys())
    
    # 정렬 기준 SQL 로직
    if selected_skills:
        # 내가 선택한 기술을 가장 많이 사용하는 기업 순으로 정렬
        order_by = f"""
        (SELECT COUNT(*) FROM job_opening_skills jos2 
         JOIN skills s2 ON jos2.skill_id = s2.id 
         WHERE jos2.job_opening_id = jo.id AND s2.name = '{selected_skills[0]}') DESC, 
        COUNT(*) DESC
        """
    else:
        # 선택 안 했으면 전체 공고 많은 순으로 정렬
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
    return load_df(query)

def render(user_skill_map):
    st.header("🏢 기업별 핵심 기술 DNA 분석")
    
    df = get_heatmap_data(user_skill_map)
    if df.empty:
        st.warning("분석할 데이터가 부족합니다.")
        return

    # 피벗 테이블 생성
    heatmap_df = df.pivot(index='company_name', columns='skill_name', values='count').fillna(0)

    # 히트맵 생성 (정렬 보장)
    fig = px.imshow(
        heatmap_df, 
        labels=dict(x="핵심 기술", y="주요 기업", color="언급 빈도"),
        color_continuous_scale='Blues',
        aspect="auto"
    )
    
    # 그래프 크기 대폭 확장
    fig.update_layout(
        xaxis=dict(side="top"),
        height=800,  # 높이 증가
        margin=dict(l=200, r=50, t=100, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **정렬 기준:** 선택한 기술이 있을 경우 해당 기술 사용 빈도 순, 없을 경우 기업 전체 채용 규모 순으로 정렬됩니다.")