import streamlit as st
import plotly.express as px
from db import load_df

def get_company_analysis_data():
    # 기업별 요구 기술 개수(난이도)와 채용 공고 빈도(활성도) 계산
    query = """
    SELECT jo.company_name, 
           COUNT(DISTINCT jos.skill_id) as tech_difficulty,
           COUNT(jo.id) as recruitment_activity
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    GROUP BY jo.company_name
    """
    return load_df(query)

def render(user_skill_map):
    st.header("🏢 기업별 맞춤 채용 분석")
    df = get_company_analysis_data()
    
    if df.empty:
        st.warning("분석할 기업 데이터가 없습니다.")
        return

    # 1. 데이터 요약 표 유지
    st.subheader("📋 기업별 상세 분석 데이터")
    # 컬럼명을 보기 좋게 변경
    display_df = df.rename(columns={
        "company_name": "기업명", 
        "tech_difficulty": "기술 난이도", 
        "recruitment_activity": "채용 활성도"
    })
    st.dataframe(display_df.sort_values("채용 활성도", ascending=False), use_container_width=True)

    # 2. 산점도 그래프 (표 아래에 배치)
    st.subheader("💡 기업별 난이도 vs 활성도 시각화")
    fig = px.scatter(
        df, 
        x="tech_difficulty", 
        y="recruitment_activity", 
        text="company_name",
        size="recruitment_activity",
        color="tech_difficulty",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )
    
    fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
    fig.update_layout(
        xaxis_title="기술 요구 난이도 (요구 스택 수)",
        yaxis_title="채용 활성도 (공고 빈도)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    💡 **전략 가이드:**
    * **좌상단:** 주니어 친화적이며 합격률이 높은 '공략 추천 기업'.
    * **우상단:** 기술적 성장이 빠르고 수요가 많은 '성장형 핵심 기업'.
    * **우하단:** 특정 기술 전문가를 우대하는 '니치 마켓 기업'.
    """)