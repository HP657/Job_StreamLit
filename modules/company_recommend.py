import streamlit as st
import plotly.express as px
from db import load_df
from utils.queries import COMPANY_SKILLS
from utils.recommendation import get_recommended_companies

def render(user_skills: list[str]) -> None:
    st.header("🏢 추천 기업")

    # 설명 토글: 기술 선택 여부와 관계없이 항상 상단에 노출
    with st.expander("💡 기업 추천 알고리즘 로직 자세히 보기"):
        st.markdown("""
        이 대시보드는 다음과 같은 **4단계 데이터 과학 로직**을 통해 최적의 기업을 선정합니다.
        
        1. **데이터 정규화 (Vectorization)**
           - **사용자 벡터**: 보유 기술을 숙련도에 따라 0.5 ~ 1.0으로 매핑합니다.
           - **기업 벡터**: 기업 공고의 기술 스택 비중을 분석하여 수치화합니다.
           
        2. **코사인 유사도 계산 (Similarity Calculation)**
           - 두 벡터의 방향성을 측정하여 기술적 적합성을 계산합니다.
           - 수식: $\\text{similarity} = \\cos(\\theta) = \\frac{\\mathbf{A} \\cdot \\mathbf{B}}{\\|\\mathbf{A}\\| \\|\\mathbf{B}\\|}$
           
        3. **가중치 반영 (Weighting)**
           - '채용 공고의 최신성' 및 '기술 요구 빈도'를 계산하여 최신 트렌드를 반영합니다.
           
        4. **최종 랭킹 (Ranking)**
           - 계산된 점수를 100점 만점으로 환산하여 높은 순으로 정렬합니다.
        """)

    if not user_skills:
        st.info("사이드바에서 보유 기술을 선택하면 추천 기업이 표시됩니다.")
        return

    # 데이터 로드
    company_df = load_df(COMPANY_SKILLS)
    recommend_df = get_recommended_companies(user_skills, company_df)

    if recommend_df.empty:
        st.warning("추천 가능한 기업 데이터가 없습니다.")
        return

    # 매칭도 순 정렬
    recommend_df = recommend_df.sort_values(by="매칭도", ascending=False)

    # 결과 강조
    top = recommend_df.iloc[0]
    st.success(f"가장 적합한 기업: {top['회사']} (매칭도 {top['매칭도']}%)")

    # 매칭도 그래프
    st.subheader("📊 기업별 매칭도 비교")
    fig = px.bar(
        recommend_df.head(10), x="매칭도", y="회사", orientation='h',
        color="매칭도", color_continuous_scale="Blues", text="매칭도", template="plotly_dark"
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(yaxis=dict(autorange="reversed"), xaxis_title="매칭도 (%)", yaxis_title="기업명")
    st.plotly_chart(fig, use_container_width=True)

    # 상세 데이터 표
    st.subheader("📋 상세 분석 데이터")
    st.dataframe(recommend_df, use_container_width=True)