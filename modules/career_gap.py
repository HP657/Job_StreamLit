import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill, selected_exp):
    with engine.connect() as conn:
        # 연차 범위가 명시된 경력 그룹화 로직
        exp_mapping = """
        CASE 
            WHEN experience = '신입' THEN '신입(0년)'
            WHEN experience IN ('1년 이상', '2년 이상') THEN '주니어(1~2년)'
            WHEN experience IN ('3년 이상', '4년 이상') THEN '미드(3~4년)'
            WHEN experience IN ('5년 이상', '6년 이상', '7년 이상', '8년 이상', '10년 이상') THEN '시니어(5년+)'
            WHEN experience = '경력무관' THEN '경력무관'
            ELSE '경력무관' 
        END as exp_group
        """
        
        params = {}
        where_clauses = []
        if selected_skill and selected_skill != "전체":
            where_clauses.append("s1.name = :skill_name")
            params["skill_name"] = selected_skill
        if selected_exp and selected_exp != "전체":
            # 사용자가 선택한 경력 범위도 매핑된 그룹과 일치하도록 처리
            where_clauses.append(f"{exp_mapping.replace('as exp_group', '')} = :exp")
            params["exp"] = selected_exp

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        sql = text(f"""
            SELECT s2.name, {exp_mapping}, COUNT(*) as count
            FROM job_opening_skills jos1
            JOIN skills s1 ON jos1.skill_id = s1.id
            JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id
            JOIN skills s2 ON jos2.skill_id = s2.id
            JOIN job_openings jo ON jos1.job_opening_id = jo.id
            {where_sql}
            GROUP BY s2.name, exp_group
            ORDER BY count DESC
        """)
        df = pd.read_sql(sql, conn, params=params)
        
        if df.empty: return df

        # 경력 선택 여부에 따른 데이터 개수 제한
        limit = 10 if (selected_exp and selected_exp != "전체") else 8
        top_skills = df.groupby('name')['count'].sum().nlargest(limit).index.tolist()
        return df[df['name'].isin(top_skills)]

def render(all_skills):
    st.header("📊 경력 단계별 분석")
    
    with st.expander("💡 분석 로직 및 기준 안내"):
        st.markdown("""
        - **경력 구간 표준화**: 세분화된 경력 단계를 연차 범위로 통합하여 시각화합니다.
            - **신입(0년)**, **주니어(1~2년)**, **미드(3~4년)**, **시니어(5년+)**, **경력무관**
        - **분석 로직**: 
            - **전체 조회 시**: 시장 수요가 높은 상위 8개 기술을 추출하여 연차별 요구도를 비교합니다.
            - **특정 경력 선택 시**: 해당 연차 그룹에서 수요가 높은 상위 10개 기술을 집중 분석합니다.
        """)
    
    col1, col2 = st.columns(2)
    selected_skill = col1.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    
    exp_order = ['신입(0년)', '주니어(1~2년)', '미드(3~4년)', '시니어(5년+)', '경력무관']
    selected_exp = col2.selectbox("경력 연차 선택", ["전체"] + exp_order)
    
    df = get_career_skills(selected_skill, selected_exp)
    
    if df.empty:
        st.warning("조건에 맞는 데이터가 없습니다.")
        return

    df['exp_group'] = pd.Categorical(df['exp_group'], categories=exp_order, ordered=True)
    
    fig = px.bar(
        df.sort_values('exp_group'), x="name", y="count", color="exp_group",
        template="plotly_dark", barmode="group",
        category_orders={"exp_group": exp_order}
    )
    st.plotly_chart(fig, use_container_width=True)