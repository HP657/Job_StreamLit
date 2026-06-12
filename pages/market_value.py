import streamlit as st
import plotly.express as px
import pandas as pd
from db import load_df

def get_bubble_data():
    query = """
    SELECT s.name as skill_name, 
           COUNT(*) as demand,
           (SELECT COUNT(*) FROM job_openings) as total_jobs
    FROM job_opening_skills jos
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY s.name
    """
    df = load_df(query)
    df['희소성'] = (1 - (df['demand'] / df['total_jobs'])) * 100
    return df

def render(user_skills: list[str], all_skills: list[str], market_dict: dict) -> None:
    # ... (기존 매칭률 및 성장률 코드 유지) ...

    st.subheader("💡 기술 시장 포지셔닝")
    bubble_df = get_bubble_data()
    
    # 선택된 기술 강조를 위한 로직
    # 선택된 기술이면 '선택 기술', 아니면 '기타'로 구분
    bubble_df['선택 여부'] = bubble_df['skill_name'].apply(lambda x: '나의 기술' if x in user_skills else '기타 기술')
    
    fig = px.scatter(
        bubble_df, 
        x="희소성", 
        y="demand", 
        size="demand", 
        color="선택 여부", # 선택 여부에 따라 색상 구분
        hover_name="skill_name",
        color_discrete_map={'나의 기술': '#FF4B4B', '기타 기술': '#1f77b4'}, # 강조 색상
        size_max=60,
        title="기술 희소성 vs 시장 수요",
        template="plotly_dark"
    )
    
    fig.update_layout(
        xaxis_title="기술 희소성 (우측으로 갈수록 전문가용)",
        yaxis_title="시장 수요 (채용 공고 수)",
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("빨간색 버블은 현재 보유하신 기술을 나타냅니다.")