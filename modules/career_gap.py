import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill=None):
    with engine.connect() as conn:
        if selected_skill:
            sql = text("""
            SELECT s2.name, jo.experience, COUNT(*) as count
            FROM job_opening_skills jos1
            JOIN skills s1 ON jos1.skill_id = s1.id
            JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id
            JOIN skills s2 ON jos2.skill_id = s2.id
            JOIN job_openings jo ON jos1.job_opening_id = jo.id
            WHERE s1.name = :skill_name
            GROUP BY s2.name, jo.experience
            ORDER BY count DESC
            LIMIT 10
            """)
            return pd.read_sql(sql, conn, params={"skill_name": selected_skill})
        else:
            sql = text("""
            SELECT s.name, jo.experience, COUNT(*) as count
            FROM job_opening_skills jos
            JOIN skills s ON s.id = jos.skill_id
            JOIN job_openings jo ON jo.id = jos.job_opening_id
            GROUP BY s.name, jo.experience
            ORDER BY count DESC
            LIMIT 10
            """)
            return pd.read_sql(sql, conn)

def render(all_skills):
    st.header("📈 경력 단계별 핵심 스킬 분석")
    st.header("📊 경력 단계별 분석")
    
    # [설명 추가] 로직 설명을 위한 expander
    with st.expander("💡 경력 단계별 역량 분석 로직 자세히 보기"):
        st.markdown("""
        경력 연차에 따라 요구되는 기술 스택의 변화를 분석하여 커리어 성장 경로를 제시합니다.
        
        1. **데이터 그룹화**: 채용 공고를 경력별(신입/주니어/시니어)로 분류합니다.
        2. **단계별 역량 추출**: 각 경력 단계에서 요구하는 상위 10개 핵심 기술을 집계합니다.
        3. **커리어 로드맵**: 경력 상승에 따라 새롭게 추가되거나 중요도가 높아지는 기술 스택을 추적하여 시각화합니다.
        
        이 분석을 통해 사용자는 현재 단계에서 다음 커리어로 넘어가기 위해 필요한 '기술적 문턱'을 확인할 수 있습니다.
        """)
    
    selected = st.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다.")
        return

    exp_order = ['신입', '1년 이상', '2년 이상', '3년 이상', '4년 이상', '5년 이상', '10년 이상', '경력무관']
    df['exp_cat'] = pd.Categorical(df['experience'], categories=exp_order, ordered=True)
    
    fig = px.bar(
        df.sort_values('exp_cat'), x="name", y="count", color="experience",
        title=f"{selected if selected != '전체' else '전체 기술'} 관련 스택",
        template="plotly_dark", barmode="group",
        category_orders={"experience": exp_order}
    )
    fig.update_layout(autosize=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    display_df = df.sort_values(["name", "exp_cat"]).drop(columns=['exp_cat'])
    st.dataframe(display_df, use_container_width=True)