import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from db import load_df

def get_market_standard():
    # 시장에서 요구하는 상위 5개 기술과 빈도를 가져오는 쿼리
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
    st.write("나의 보유 기술과 시장의 요구 수준을 비교합니다.")

    if not user_skills:
        st.info("사이드바(혹은 메인)에서 보유 기술을 먼저 선택해주세요.")
        return

    # 데이터 로드
    market_df = get_market_standard()
    categories = market_df['skill'].tolist()
    
    # 정규화된 시장 수치 (최대값을 1로)
    max_val = market_df['count'].max()
    market_values = (market_df['count'] / max_val).tolist()
    
    # 사용자의 보유 기술 수치 (선택했으면 1, 없으면 0)
    user_values = [1 if cat in user_skills else 0 for cat in categories]

    # 레이더 차트 생성
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=market_values,
        theta=categories,
        fill='toself',
        name='시장 요구 수준 (상위 5개)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=user_values,
        theta=categories,
        fill='toself',
        name='나의 보유 역량'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 학습 조언
    st.subheader("💡 학습 우선순위")
    gap_skills = [cat for i, cat in enumerate(categories) if user_values[i] == 0]
    if gap_skills:
        st.warning(f"다음 기술들을 먼저 학습하는 것을 추천합니다: {', '.join(gap_skills)}")
    else:
        st.success("시장 요구 기술을 모두 보유하고 계시네요!")