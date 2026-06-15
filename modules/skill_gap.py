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
    max_count = df['count'].max()
    df['normalized_market'] = df['count'] / max_count
    total_count = df['count'].sum()
    df['percentage'] = df['count'] / total_count
    return df

def render(user_skill_map):
    st.header("🎯 역량 갭 분석")

    # --- 설명 부분 (태그 제거됨) ---
    with st.expander("💡 역량 갭 분석 로직 자세히 보기"):
        st.markdown("""
        사용자의 보유 기술과 시장에서 요구하는 핵심 기술 간의 격차를 분석합니다.
        
        1. **기술 스택 스코어링**: 사용자가 선택한 보유 기술을 숙련도(초급 0.5, 숙련 1.0)로 정량화합니다.
        2. **요구 역량 매핑**: 전체 채용 공고에 등장하는 기술의 빈도를 분석하여 시장 표준 역량 벡터를 도출합니다.
        3. **Gap 계산**: `시장 표준 역량`과 `사용자의 현재 역량`을 레이더 차트로 비교하여, 어떤 기술이 상대적으로 부족한지 시각화합니다.
        
        이 데이터를 통해 사용자는 현재 본인에게 가장 필요한 학습 우선순위를 확인할 수 있습니다.
        """)
    # ----------------------------

    market_df = get_market_standard()
    categories = market_df['skill'].tolist()
    market_values = market_df['normalized_market'].tolist()
    user_values = [user_skill_map.get(cat, 0.0) for cat in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=market_values, theta=categories, fill='toself', name='시장 요구 중요도'))
    fig.add_trace(go.Scatterpolar(r=user_values, theta=categories, fill='toself', name='나의 보유 역량'))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.0], showticklabels=False),
                   angularaxis=dict(tickfont=dict(size=14))),
        showlegend=True,
        margin=dict(l=80, r=80, t=50, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.write("### 💡 학습 우선순위 제언")
    for idx, row in market_df.iterrows():
        skill = row['skill']
        percentage = row['percentage']
        current_val = user_skill_map.get(skill, 0.0)
        
        if current_val < 1.0:
            level_text = "미보유" if current_val == 0.0 else "초급"
            st.warning(f"**{skill}** ({level_text}): 시장 점유율 {percentage:.1%}인 핵심 기술입니다. 숙련도를 높이는 것을 추천합니다.")