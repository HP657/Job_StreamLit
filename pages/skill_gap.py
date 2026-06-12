import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from db import load_df

def get_market_standard():
    # 쿼리로 데이터 가져오기
    query = """
    SELECT s.name as skill, COUNT(*) as count
    FROM job_opening_skills jos
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY s.name
    ORDER BY count DESC
    LIMIT 5
    """
    df = load_df(query)
    # 여기서 percentage를 미리 계산해서 반환합니다!
    total_count = df['count'].sum()
    df['percentage'] = df['count'] / total_count
    return df

def render(user_skill_map):
    st.header("🎯 역량 갭 분석")

    # 1. 데이터 로드 (percentage가 포함된 상태로 들어옴)
    market_df = get_market_standard()
    
    categories = market_df['skill'].tolist()
    market_values = market_df['percentage'].tolist()
    
    # 2. 숙련도 반영
    user_values = [user_skill_map.get(cat, 0.0) for cat in categories]

    # 3. 레이더 차트 생성
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=market_values, theta=categories, fill='toself', name='시장 요구 중요도'
    ))
    fig.add_trace(go.Scatterpolar(
        r=user_values, theta=categories, fill='toself', name='나의 보유 역량'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.0], showticklabels=False)),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 4. 분석 인사이트 추가
    st.write("### 💡 학습 우선순위 제언")
    
    # market_df를 순회하며 경고 메시지 출력
    for idx, row in market_df.iterrows():
        skill = row['skill']
        percentage = row['percentage']
        
        # 숙련도가 1.0 미만(초급/미보유)이면 경고
        if user_skill_map.get(skill, 0.0) < 1.0:
            level_text = "미보유" if user_skill_map.get(skill, 0.0) == 0.0 else "초급"
            st.warning(f"**{skill}** ({level_text}): 시장 중요도 {percentage:.1%}인 핵심 기술입니다. 숙련도를 높이는 것을 추천합니다.")