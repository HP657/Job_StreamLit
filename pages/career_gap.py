import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill=None):
    with engine.connect() as conn:
        if selected_skill:
            # 선택한 기술을 포함하여 연관 기술들과 함께 조회
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
            LIMIT 20
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
            LIMIT 15
            """)
            return pd.read_sql(sql, conn)

def render(all_skills):
    st.header("📈 경력 단계별 핵심 스킬 분석")
    
    selected = st.selectbox("분석할 기술 선택 (선택 안 하면 상위 기술 표시)", ["전체"] + all_skills)
    
    skill_name = None if selected == "전체" else selected
    df = get_career_skills(skill_name)
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다.")
        return

    # 경력 순서대로 정렬하기 위한 로직 (데이터프레임에 정렬 키 추가)
    # 실제 데이터의 'experience' 값에 따라 리스트를 조정하세요
    exp_order = ['신입', '1년 이상', '2년 이상', '3년 이상', '4년 이상', '5년 이상', '10년 이상', '경력무관']
    df['exp_cat'] = pd.Categorical(df['experience'], categories=exp_order, ordered=True)
    df = df.sort_values('exp_cat')

    # 그래프 생성 (너비를 100%로 설정)
    fig = px.bar(
        df, x="name", y="count", color="experience",
        title=f"{selected if selected != '전체' else '전체 기술'} 관련 경력별 요구 스택",
        template="plotly_dark",
        barmode="group",
        category_orders={"experience": exp_order} # 카테고리 순서 고정
    )
    
    # 레이아웃 너비 최적화
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 경력 단계별 상세 데이터")
    st.dataframe(df.drop(columns=['exp_cat']).sort_values(["name", "exp_cat"]), use_container_width=True)