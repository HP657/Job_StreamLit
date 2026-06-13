import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill=None):
    with engine.connect() as conn:
        if selected_skill:
            # JOIN을 활용한 평탄화된 쿼리 (가장 안전한 방식)
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
            # 전체 상위 10개
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
    
    selected = st.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다.")
        return

    # 경력 순서 정렬
    exp_order = ['신입', '1년 이상', '2년 이상', '3년 이상', '4년 이상', '5년 이상', '10년 이상', '경력무관']
    df['exp_cat'] = pd.Categorical(df['experience'], categories=exp_order, ordered=True)
    
    # 그래프 생성
    fig = px.bar(
        df.sort_values('exp_cat'), x="name", y="count", color="experience",
        title=f"{selected if selected != '전체' else '전체 기술'} 관련 연관 스택 TOP 10",
        template="plotly_dark",
        barmode="group",
        category_orders={"experience": exp_order}
    )
    
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["name", "exp_cat"]).drop(columns=['exp_cat']), use_container_width=True)