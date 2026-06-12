import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df

def get_heatmap_data(user_skill_map):
    selected_skills = list(user_skill_map.keys())
    
    # 파라미터(params) 없이 쿼리 문자열 안에 직접 안전하게 값을 삽입합니다.
    if selected_skills:
        # SQL Injection 방지를 위해 따옴표를 이스케이프 처리
        skill_name = str(selected_skills[0]).replace("'", "''")
        
        # 쿼리 안에서 직접 값을 삽입하므로 params가 필요 없습니다.
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
    
    # db.py의 원래 함수 규격에 맞춰 딱 query만 전달합니다.
    return load_df(query)

def render(user_skill_map):
    st.header("🏢 기업별 핵심 기술 DNA 분석")
    
    # 쿼리 실행
    df = get_heatmap_data(user_skill_map)
    
    if df.empty:
        st.warning("분석할 데이터가 부족합니다. 사이드바에서 다른 기술을 선택해 보세요.")
        return

    # 피벗 테이블 변환
    heatmap_df = df.pivot(index='company_name', columns='skill_name', values='count').fillna(0)

    # 히트맵 시각화
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
    st.info("💡 정렬 기준: 선택한 기술이 있을 경우 해당 기술 빈도순, 없을 경우 전체 공고 많은 순.")