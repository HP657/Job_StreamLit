import streamlit as st
import plotly.express as px
from db import load_df

def get_heatmap_data():
    # 1. 공고가 5건 이상인 활성 기업 중 상위 10개 선정
    # 2. 전체 기술 중 상위 20개 핵심 기술만 추출
    query = """
    WITH TopCompanies AS (
        SELECT company_name FROM job_openings 
        GROUP BY company_name 
        HAVING COUNT(*) >= 5
        ORDER BY COUNT(*) DESC LIMIT 10
    ),
    TopSkills AS (
        SELECT s.name FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        GROUP BY s.name ORDER BY COUNT(*) DESC LIMIT 20
    )
    SELECT jo.company_name, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    WHERE jo.company_name IN (SELECT company_name FROM TopCompanies)
      AND s.name IN (SELECT name FROM TopSkills)
    GROUP BY jo.company_name, s.name
    """
    return load_df(query)

def render():
    st.header("🏢 기업별 핵심 기술 DNA 분석")
    
    df = get_heatmap_data()
    if df.empty:
        st.warning("분석 가능한 기업 데이터가 부족합니다.")
        return

    # 데이터 피벗: 기업명(행) x 기술명(열)
    heatmap_df = df.pivot(index='company_name', columns='skill_name', values='count').fillna(0)

    # 히트맵 생성
    fig = px.imshow(
        heatmap_df, 
        labels=dict(x="핵심 기술", y="주요 기업", color="언급 빈도"),
        color_continuous_scale='Blues',
        aspect="auto"
    )
    
    # 레이아웃 조정으로 가독성 극대화
    fig.update_layout(
        xaxis=dict(side="top"),
        height=600,  # 차트 높이 고정
        margin=dict(l=150, r=50, t=100, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    💡 **분석 기준:**
    * **대상 기업:** 채용 공고가 5건 이상 등록된 활성 기업 상위 10곳.
    * **대상 기술:** 전체 채용 시장에서 가장 빈번하게 요구되는 핵심 기술 상위 20종.
    * **해석:** 색상이 진할수록 해당 기업이 특정 기술을 중점적으로 채용하고 있음을 의미합니다.
    """)