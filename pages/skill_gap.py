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

def render(user_skill_map):
    st.header("🎯 역량 갭 분석")

    # 1. 데이터 로드
    market_df = get_market_standard()
    
    # 2. 시장 요구량 정규화
    total_count = market_df['count'].sum()
    market_values = (market_df['count'] / total_count).tolist()
    
    categories = market_df['skill'].tolist()
    
    # 3. 숙련도 반영 (user_skill_map 딕셔너리에서 값 가져오기)
    # user_skill_map에는 {기술명: 점수} 형태로 데이터가 들어옵니다.
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
                showticklabels=False  # ★ 하얀 숫자 제거
            )
        ),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 분석 인사이트 추가
    st.write("### 💡 학습 우선순위 제언")
    
    # 컬럼이 확실히 존재하는지 확인하고 순회
    for i in range(len(market_df)):
        skill = market_df.iloc[i]['skill']
        percentage = market_df.iloc[i]['percentage']
        
        # 숙련도가 없거나 0.5(초급)일 경우 우선 학습 추천
        current_skill_level = user_skill_map.get(skill, 0.0)
        
        if current_skill_level < 1.0:
            level_text = "미보유" if current_skill_level == 0.0 else "초급"
            st.warning(f"**{skill}** ({level_text}): 시장 중요도 {percentage:.1%}인 핵심 기술입니다. 숙련도를 높이는 것을 추천합니다.")