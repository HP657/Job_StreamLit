import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df

def get_heatmap_data(user_skill_map):
    # 1. 사용자가 선택한 기술
    selected_skills = list(user_skill_map.keys())
    
    # 2. 아주 단순화된 쿼리 구조로 변경 (복잡한 WITH 절 제거)
    # 정렬 기준을 쿼리 내에서 복잡하게 처리하지 않고 데이터를 가져온 후 파이썬에서 정렬
    query = """
    SELECT jo.company_name, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY jo.company_name, s.name
    """
    
    df = load_df(query)
    if df.empty:
        return df

    # 3. 파이썬(Pandas)에서 정렬 수행 (SQL 문법 오류 방지)
    if selected_skills:
        # 선택한 기술을 가장 많이 쓰는 기업 상위 25개 선정
        target_skill = selected_skills[0]
        df_skill = df[df['skill_name'] == target_skill]
        top_companies = df_skill.groupby('company_name')['count'].sum().sort_values(ascending=False).head(25).index
    else:
        # 전체 공고 많은 기업 상위 25개 선정
        top_companies = df.groupby('company_name')['count'].sum().sort_values(ascending=False).head(25).index

    # 4. 상위 기술 30개 선정
    top_skills = df.groupby('skill_name')['count'].sum().sort_values(ascending=False).head(30).index

    # 5. 필터링된 최종 데이터 반환
    final_df = df[df['company_name'].isin(top_companies) & df['skill_name'].isin(top_skills)]
    return final_df

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
        height=700,
        margin=dict(l=150, r=50, t=100, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 선택한 기술이 있을 경우 해당 기술 빈도순, 없을 경우 전체 공고 많은 순으로 정렬됩니다.")