import streamlit as st
import plotly.express as px
from db import load_df

def get_heatmap_data():
    # 기업별, 기술별 언급 빈도를 가져오는 쿼리
    query = """
    SELECT jo.company_name, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    WHERE jo.company_name IN (
        SELECT company_name FROM job_openings 
        GROUP BY company_name ORDER BY COUNT(*) DESC LIMIT 10
    )
    GROUP BY jo.company_name, s.name
    """
    return load_df(query)

def render():
    st.header("🏢 기업별 기술 DNA 분석")
    
    df = get_heatmap_data()
    if df.empty:
        st.warning("기업 데이터가 부족합니다.")
        return

    # 피벗 테이블 형태로 변환 (히트맵용)
    heatmap_df = df.pivot(index='company_name', columns='skill_name', values='count').fillna(0)

    # 히트맵 그리기
    fig = px.imshow(
        heatmap_df, 
        labels=dict(x="기술 스택", y="기업명", color="언급 빈도"),
        aspect="auto",
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(xaxis=dict(side="top"))
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("색상이 진할수록 해당 기업이 특정 기술을 많이 요구함을 의미합니다. 지원하려는 기업의 기술 환경을 파악해 보세요.")