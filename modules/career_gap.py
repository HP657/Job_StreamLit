import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill, selected_exp):
    with engine.connect() as conn:
        # 동적 SQL 조건문 생성
        params = {}
        where_clauses = []
        
        # '전체'가 아닐 때만 조건 추가
        if selected_skill and selected_skill != "전체":
            where_clauses.append("s1.name = :skill_name")
            params["skill_name"] = selected_skill
            
        if selected_exp and selected_exp != "전체":
            where_clauses.append("jo.experience = :exp")
            params["exp"] = selected_exp

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # 메인 쿼리 로직
        sql = text(f"""
            SELECT s2.name, jo.experience, COUNT(*) as count
            FROM job_opening_skills jos1
            JOIN skills s1 ON jos1.skill_id = s1.id
            JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id
            JOIN skills s2 ON jos2.skill_id = s2.id
            JOIN job_openings jo ON jos1.job_opening_id = jo.id
            {where_sql}
            GROUP BY s2.name, jo.experience
            ORDER BY count DESC
        """)
        
        df = pd.read_sql(sql, conn, params=params)
        
        if df.empty:
            return df

        # 로직: 전체 count 기준 상위 5개 기술 추출 후 필터링
        top_5_skills = df.groupby('name')['count'].sum().nlargest(5).index.tolist()
        return df[df['name'].isin(top_5_skills)]

def render(all_skills):
    st.header("📊 경력 단계별 분석")
    
    with st.expander("💡 경력 단계별 역량 분석 로직 자세히 보기"):
        st.markdown("""
        경력 연차별로 요구되는 핵심 기술 스택을 분석하여 커리어 성장 경로를 제시합니다.
        
        1. **데이터 필터링**: 선택된 기술 및 경력 조건에 따라 연관 기술 데이터를 추출합니다.
        2. **단계별 역량 추출**: 추출된 데이터 중 가장 수요가 많은 상위 5개 핵심 기술을 집계합니다.
        3. **커리어 로드맵**: 경력 상승에 따라 기술 스택의 요구 빈도를 추적하여 시각화합니다.
        """)
    
    # 1. UI 필터 생성
    col1, col2 = st.columns(2)
    selected_skill = col1.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    exp_order = ['신입', '1년 이상', '2년 이상', '3년 이상', '4년 이상', '5년 이상', '10년 이상', '경력무관']
    selected_exp = col2.selectbox("경력 선택", ["전체"] + exp_order)
    
    # 2. 데이터 분석
    df = get_career_skills(selected_skill, selected_exp)
    
    if df.empty:
        st.warning("조건에 맞는 데이터가 없습니다.")
        return

    # 3. 그래프 렌더링
    df['exp_cat'] = pd.Categorical(df['experience'], categories=exp_order, ordered=True)
    
    fig = px.bar(
        df.sort_values('exp_cat'), x="name", y="count", color="experience",
        title=f"필터 적용 기술 상위 5개 스택",
        template="plotly_dark", barmode="group",
        category_orders={"experience": exp_order}
    )
    fig.update_layout(autosize=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["name", "exp_cat"]).drop(columns=['exp_cat']), use_container_width=True)