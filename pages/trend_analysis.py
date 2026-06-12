import streamlit as st
import pandas as pd
import plotly.express as px
from db import load_df
# 쿼리는 utils/queries.py에 있는 것을 사용하거나, 직접 작성할 수 있습니다.
# 여기서는 예시로 작성된 쿼리를 사용합니다.

def get_trend_data():
    query = """
    SELECT 
        to_char(jo.created_at, 'YYYY-MM') as month,
        s.name as skill_name,
        COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    """
    return load_df(query)

def render():
    st.header("📈 시장 기술 트렌드 추이")

    # 데이터 로드 및 전처리
    df = get_trend_data()
    
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 피벗 테이블 생성
    pivot_df = df.pivot(index='month', columns='skill_name', values='count').fillna(0)
    
    # 상위 5개 기술만 추출
    top_skills = pivot_df.sum().nlargest(5).index
    pivot_df = pivot_df[top_skills]

    # 시각화
    fig = px.area(
        pivot_df, 
        x=pivot_df.index, 
        y=pivot_df.columns,
        labels={"value": "언급 빈도", "month": "연도-월", "skill_name": "기술 스택"},
        title="시간 흐름에 따른 상위 5개 기술 점유율 변화"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("시간이 지남에 따라 점유율이 상승하거나 하락하는 기술 트렌드를 확인하여, 현재 시장에서 가장 선호되는 기술을 파악할 수 있습니다.")