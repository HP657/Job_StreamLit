import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from db import load_df

def get_market_standard():
    query = """
    SELECT s.name as skill, COUNT(*) as count
    FROM job_opening_skills jos
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY s.name
    ORDER BY count DESC
    LIMIT 5
    """
    return load_df(query)

def render(user_skills):
    st.header("🎯 역량 갭 분석")

    # 1. 데이터 로드
    market_df = get_market_standard()
    
    # 2. 시장 요구량을 백분율(0~1)로 정규화
    # 각 기술의 공고 빈도를 전체 합계로 나누거나, 최댓값으로 나누어 상대적 중요도 도출
    total_count = market_df['count'].sum()
    market_df['percentage'] = market_df['count'] / total_count
    
    categories = market_df['skill'].tolist()
    market_values = market_df['percentage'].tolist()
    
    # 3. 나의 보유 역량 매핑
    # 선택한 기술은 1.0(숙련), 선택 안 한 기술은 0.0
    user_values = [1.0 if cat in user_skills else 0.0 for cat in categories]

    # 4. 레이더 차트 생성
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=market_values,
        theta=categories,
        fill='toself',
        name='시장 요구 중요도'
    ))
    fig.add_trace(go.Scatterpolar(
        r=user_values,
        theta=categories,
        fill='toself',
        name='나의 보유 역량'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(market_values) * 1.2])),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 분석 인사이트 추가
    st.write("### 💡 학습 우선순위 제언")
    # 시장 중요도가 높은데(상위권) 내가 선택하지 않은 기술 찾기
    for i, row in market_df.iterrows():
        if row['skill'] not in user_skills:
            st.warning(f"**{row['skill']}**: 시장에서 중요도가 {row['percentage']:.1%}인 핵심 기술입니다. 학습을 우선 고려하세요.")