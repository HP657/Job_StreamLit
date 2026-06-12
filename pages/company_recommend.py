import streamlit as st
import plotly.express as px
from db import load_df
from utils.queries import COMPANY_SKILLS
from utils.recommendation import get_recommended_companies

def render(user_skills: list[str]) -> None:
    st.header("🏢 추천 기업")

    if not user_skills:
        st.info("사이드바에서 보유 기술을 선택하면 추천 기업이 표시됩니다.")
        return

    # 1. 데이터 로드 및 정렬
    company_df = load_df(COMPANY_SKILLS)
    recommend_df = get_recommended_companies(user_skills, company_df)

    if recommend_df.empty:
        st.warning("추천 가능한 기업 데이터가 없습니다.")
        return

    recommend_df = recommend_df.sort_values(by="매칭도", ascending=False)

    # 2. 강조 문구
    top = recommend_df.iloc[0]
    st.success(f"가장 적합한 기업: {top['회사']} (매칭도 {top['매칭도']}%)")

    # 3. 매칭도 시각화 (상단 그래프)
    st.subheader("📊 기업별 매칭도 비교")
    fig = px.bar(
        recommend_df.head(10), 
        x="매칭도", 
        y="회사", 
        orientation='h',
        color="매칭도",
        color_continuous_scale="Blues",
        text="매칭도",
        template="plotly_dark"
    )
    
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="매칭도 (%)",
        yaxis_title="기업명",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4. 상세 데이터 표 (하단부 유지)
    st.subheader("📋 상세 분석 데이터")
    st.dataframe(recommend_df, use_container_width=True)