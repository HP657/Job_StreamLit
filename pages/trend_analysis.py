import streamlit as st
import pandas as pd
import plotly.express as px
from db import load_df

def get_trend_data():
    # 쿼리 수정: 날짜별로 정렬이 되도록 명시
    query = """
    SELECT 
        to_char(jo.created_at, 'YYYY-MM') as month,
        s.name as skill_name,
        COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    ORDER BY month ASC
    """
    return load_df(query)

def render():
    st.header("📈 시장 기술 트렌드 추이")

    df = get_trend_data()
    
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 피벗 테이블 생성 및 결측치 0 채움
    pivot_df = df.pivot(index='month', columns='skill_name', values='count').fillna(0)
    
    # 상위 5개 기술 추출
    top_skills = pivot_df.sum().nlargest(5).index
    pivot_df = pivot_df[top_skills]

    # 그래프 생성 (데이터 수치 표기 강화)
    fig = px.area(
        pivot_df, 
        x=pivot_df.index, 
        y=pivot_df.columns,
        labels={"value": "언급 빈도", "month": "연도-월", "skill_name": "기술 스택"},
        title="시간 흐름에 따른 상위 5개 기술 점유율 변화"
    )

    # Hover 정보 명확화 및 범례 설정
    fig.update_traces(mode="lines+markers", hovertemplate='%{y}')
    fig.update_layout(
        hovermode="x unified",  # 마우스 올렸을 때 해당 월의 모든 수치 한 번에 보기
        legend_title="기술 스택"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 디버깅용: 데이터가 실제로 있는지 확인
    with st.expander("데이터 상세 보기"):
        st.dataframe(pivot_df)