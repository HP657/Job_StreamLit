import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from db import load_df

def get_market_standard():
    # 시장 요구 기술 상위 5개 추출 및 최대값 기준 정규화
    query = """
    SELECT s.name as skill, COUNT(*) as count
    FROM job_opening_skills jos
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY s.name
    ORDER BY count DESC
    LIMIT 5
    """
    df = load_df(query)
    # 최대값으로 나누어 0~1 사이 값으로 정규화 (최대 인기 기술이 1.0이 됨)
    max_count = df['count'].max()
    df['normalized_market'] = df['count'] / max_count
    # 원래 점유율 계산 (인사이트용)
    total_count = df['count'].sum()
    df['percentage'] = df['count'] / total_count
    return df

def render(user_skill_map):
    st.header("🎯 역량 갭 분석")

    # 1. 데이터 로드
    market_df = get_market_standard()
    categories = market_df['skill'].tolist()
    
    # 2. 시장 요구 역량 (정규화된 값)
    market_values = market_df['normalized_market'].tolist()
    
    # 3. 나의 보유 역량 (user_skill_map 딕셔너리에서 가져오기, 없으면 0.0)
    user_values = [user_skill_map.get(cat, 0.0) for cat in categories]

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
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1.0], 
                showticklabels=False  # 축의 숫자(눈금) 제거
            ),
            angularaxis=dict(tickfont=dict(size=14)) # 기술명 글자 크기
        ),
        showlegend=True,
        margin=dict(l=80, r=80, t=50, b=50) # 차트 영역 여백 조절
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 분석 인사이트 제언
    st.write("### 💡 학습 우선순위 제언")
    for idx, row in market_df.iterrows():
        skill = row['skill']
        percentage = row['percentage']
        current_val = user_skill_map.get(skill, 0.0)
        
        # 숙련도가 1.0(숙련) 미만일 경우 학습 제언
        if current_val < 1.0:
            level_text = "미보유" if current_val == 0.0 else "초급"
            st.warning(f"**{skill}** ({level_text}): 시장 점유율 {percentage:.1%}인 핵심 기술입니다. 숙련도를 높이는 것을 추천합니다.")