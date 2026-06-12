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
    df = load_df(query)
    total_count = df['count'].sum()
    df['percentage'] = df['count'] / total_count
    return df

def render(user_skill_map):
    st.header("🎯 역량 갭 분석")

    market_df = get_market_standard()
    categories = market_df['skill'].tolist()
    market_values = market_df['percentage'].tolist()
    user_values = [user_skill_map.get(cat, 0.0) for cat in categories]

    # 레이더 차트 생성
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=market_values, theta=categories, fill='toself', name='시장 점유율'))
    fig.add_trace(go.Scatterpolar(r=user_values, theta=categories, fill='toself', name='나의 보유 역량'))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.0], showticklabels=False),
            angularaxis=dict(tickfont=dict(size=14)) # 카테고리 글자 크기 키움
        ),
        showlegend=True,
        margin=dict(l=80, r=80, t=50, b=50) # 차트 영역 여백 조절하여 크게 보임
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 분석 인사이트 수정
    st.write("### 💡 학습 우선순위 제언")
    for idx, row in market_df.iterrows():
        skill = row['skill']
        percentage = row['percentage']
        current_val = user_skill_map.get(skill, 0.0)
        
        if current_val < 1.0:
            level_text = "미보유" if current_val == 0.0 else "초급"
            # 용어 변경: 시장 중요도 -> 시장 점유율
            st.warning(f"**{skill}** ({level_text}): 시장 점유율 {percentage:.1%}인 핵심 기술입니다. 숙련도를 높이는 것을 추천합니다.")