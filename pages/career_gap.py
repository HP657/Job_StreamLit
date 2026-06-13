import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill=None):
    with engine.connect() as conn:
        if selected_skill:
            # 1. 선택한 기술과 같은 공고에 등장하는 기술들의 빈도 TOP 10만 추출
            sql = text("""
            SELECT s.name, jo.experience, COUNT(*) as count
            FROM job_opening_skills jos
            JOIN skills s ON s.id = jos.skill_id
            JOIN job_openings jo ON jo.id = jos.job_opening_id
            WHERE jos.job_opening_id IN (
                SELECT job_opening_id FROM job_opening_skills 
                JOIN skills ON skills.id = job_opening_skills.skill_id
                WHERE skills.name = :skill_name
            )
            GROUP BY s.name, jo.experience
            HAVING count > 0
            ORDER BY count DESC
            LIMIT 10
            """)
            return pd.read_sql(sql, conn, params={"skill_name": selected_skill})
        else:
            # 2. 전체 기술 중 공고 상위 10개만 추출
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
    
    # 3. 그래프 가독성 향상: barmode='group'으로 설정하여 막대가 겹치지 않게 함
    fig = px.bar(
        df.sort_values('exp_cat'), x="name", y="count", color="experience",
        title=f"{selected if selected != '전체' else '전체 기술'} TOP 10 연관 스택",
        template="plotly_dark",
        barmode="group",
        category_orders={"experience": exp_order}
    )
    
    # 그래프 너비 확보
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["name", "exp_cat"]).drop(columns=['exp_cat']), use_container_width=True)