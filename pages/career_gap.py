import streamlit as st
import plotly.express as px
from db import load_df

def get_career_skills(selected_skill=None):
    if selected_skill:
        # 선택한 기술과 관련된 기술들 조회 (연관 분석 로직)
        query = f"""
        SELECT s.name, jo.experience_level, COUNT(*) as count
        FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        JOIN job_openings jo ON jo.id = jos.job_opening_id
        WHERE jo.id IN (
            SELECT job_opening_id FROM job_opening_skills 
            WHERE skill_id = (SELECT id FROM skills WHERE name = '{selected_skill}')
        )
        GROUP BY s.name, jo.experience_level
        LIMIT 20
        """
    else:
        # 평소에는 전체 상위 15개 기술만 조회
        query = """
        SELECT s.name, jo.experience_level, COUNT(*) as count
        FROM job_opening_skills jos
        JOIN skills s ON s.id = jos.skill_id
        JOIN job_openings jo ON jo.id = jos.job_opening_id
        GROUP BY s.name, jo.experience_level
        ORDER BY count DESC
        LIMIT 15
        """
    return load_df(query)

def render(all_skills):
    st.header("📈 경력 단계별 핵심 스킬 분석")
    
    # 기술 선택
    selected = st.selectbox("분석할 기술 선택 (선택 안 하면 상위 기술 표시)", ["전체"] + all_skills)
    
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다.")
        return

    # 그래프 그리기
    fig = px.bar(
        df, x="name", y="count", color="experience_level",
        title=f"{selected if selected != '전체' else '전체 기술'} 관련 경력별 요구 스택",
        template="plotly_dark",
        barmode="group" # 그룹화된 막대 그래프로 가독성 개선
    )
    
    fig.update_layout(
        xaxis_title="기술 스택",
        yaxis_title="공고 수",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 상세 데이터 표
    st.subheader("📋 경력 단계별 상세 데이터")
    st.dataframe(df.sort_values("count", ascending=False), use_container_width=True)