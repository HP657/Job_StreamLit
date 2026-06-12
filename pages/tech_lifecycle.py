import streamlit as st
import plotly.express as px
from db import load_df

def get_lifecycle_data():
    # 'YYYY-"Q"Q' 형식으로 분기(Quarter) 추출
    query = """
    SELECT TO_CHAR(jo.created_at, 'YYYY-"Q"Q') AS period, s.name as skill_name, COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    ORDER BY 1 ASC
    """
    return load_df(query)

def render():
    st.header("⏳ 기술 생애주기 분석 (분기별)")
    df = get_lifecycle_data()
    
    if df.empty:
        st.warning("분석할 데이터가 부족합니다.")
        return

    # 데이터 정렬 및 상위 기술 필터링
    df = df.sort_values(by='period')
    top_skills = df.groupby('skill_name')['count'].sum().nlargest(5).index
    df_filtered = df[df['skill_name'].isin(top_skills)]

    # x축을 'period'로 명확히 지정하여 선 그래프 생성
    fig = px.line(
        df_filtered, 
        x="period", 
        y="count", 
        color="skill_name",
        markers=True,
        title="주요 기술 스택의 분기별 수요 변화"
    )

    fig.update_layout(
        xaxis_title="기간 (분기)",
        yaxis_title="공고 수",
        template="plotly_dark",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 **해석:** 분기 단위로 기술 수요를 파악하여 단기적 유행이 아닌 장기적 기술 성장세를 확인하세요.")