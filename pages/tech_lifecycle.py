import streamlit as st
import plotly.express as px
from db import load_df

def get_lifecycle_data():
    # PostgreSQL 기준, 날짜를 'YYYY-MM' 형식의 문자열로 변환하여 뭉침 현상 방지
    query = """
    SELECT TO_CHAR(jo.created_at, 'YYYY-MM') AS month, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    ORDER BY 1 ASC
    """
    return load_df(query)

def render():
    st.header("⏳ 기술 생애주기 분석")
    df = get_lifecycle_data()
    
    if df.empty:
        st.warning("데이터가 부족합니다.")
        return

    # 데이터 정렬 확인
    df = df.sort_values(by='month')

    # Plotly Express를 사용하여 훨씬 쉽게 선 그래프 생성
    # markers=True를 통해 추세를 더 명확히 함
    fig = px.line(
        df[df['skill_name'].isin(df.groupby('skill_name')['count'].sum().nlargest(5).index)],
        x="month", 
        y="count", 
        color="skill_name",
        markers=True,
        title="기술 스택별 채용 수요 추이 (월간)"
    )

    fig.update_layout(
        xaxis_title="기간 (월)",
        yaxis_title="공고 수",
        template="plotly_dark",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 **해석:** 그래프가 지속적으로 우상향하면 '성장 중', 하향 곡선을 그리면 '쇠퇴 중'인 기술로 판단할 수 있습니다.")