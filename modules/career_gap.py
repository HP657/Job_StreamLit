import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill, selected_exp):
    with engine.connect() as conn:
        # 경력 그룹화: 신입 제거, 경력무관 최우선 배치
        exp_mapping = """
        CASE 
            WHEN experience = '경력무관' THEN '경력무관'
            WHEN experience IN ('1년 이상', '2년 이상') THEN '주니어(1~2년)'
            WHEN experience IN ('3년 이상', '4년 이상') THEN '미드(3~4년)'
            WHEN experience IN ('5년 이상', '6년 이상', '7년 이상', '8년 이상', '10년 이상', '11년 이상', '15년 이상') THEN '시니어(5년+)'
            ELSE '0. 경력무관' 
        END as exp_group
        """
        
        params = {}
        if selected_skill and selected_skill != "전체":
            sql = f"""
                SELECT s2.name, {exp_mapping}, COUNT(*) as count
                FROM job_opening_skills jos1
                JOIN skills s1 ON jos1.skill_id = s1.id
                JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id
                JOIN skills s2 ON jos2.skill_id = s2.id
                JOIN job_openings jo ON jos1.job_opening_id = jo.id
                WHERE s1.name = :skill_name
            """
            params["skill_name"] = selected_skill
        else:
            sql = f"""
                SELECT s.name, {exp_mapping}, COUNT(*) as count
                FROM job_opening_skills jos
                JOIN skills s ON s.id = jos.skill_id
                JOIN job_openings jo ON jo.id = jos.job_opening_id
            """
            
        if selected_exp and selected_exp != "전체":
            sql += f" AND ({exp_mapping.replace('as exp_group', '')}) = :exp "
            params["exp"] = selected_exp
        
        sql += " GROUP BY 1, 2 ORDER BY count DESC "
        
        df = pd.read_sql(text(sql), conn, params=params)
        
        if df.empty: return df

        # 기술 선택 시 연관 기술 상위 10개 추출
        top_skills = df.groupby('name')['count'].sum().nlargest(10).index.tolist()
        return df[df['name'].isin(top_skills)]

def render(all_skills):
    st.header("📊 경력 단계별 분석")
    
    with st.expander("💡 상세 분석 및 데이터 추출 로직 안내"):
        st.markdown("""
        **1. 경력 그룹화 표준화**
        - 데이터의 일관성을 위해 파편화된 경력 데이터를 4개 핵심 구간으로 통합했습니다.
        - **우선순위 정렬**: '경력무관'을 가장 먼저 배치하여, 특정 연차 제한이 없는 채용 공고의 범용적 기술 수요를 가장 먼저 확인할 수 있게 설계했습니다.
        
        **2. 데이터 추출 알고리즘**
        - **전체 조회**: 모든 채용 공고를 대상으로 기술별 빈도수를 계산하여 시장 전체에서 가장 수요가 많은 상위 10개 기술을 추출합니다.
        - **기술 연관 분석 (Co-occurrence)**: 특정 기술을 선택하면, 해당 기술이 포함된 채용 공고를 찾고 그 안에 함께 기재된 기술들(연관 스택)의 경력별 분포를 재계산합니다.
        - **연차 필터링**: 사용자가 특정 경력 구간을 선택하면, 해당 구간의 기술 수요 데이터를 집중적으로 필터링하여 시각화합니다.
        
        **3. 시각화 가이드**
        - 선택하신 기술이 그래프의 가장 왼쪽에 배치되어 연관도 파악이 용이합니다.
        - `경력무관` 그룹은 데이터 범용성 판단의 기준점으로 활용됩니다.
        """)
    
    col1, col2 = st.columns(2)
    selected_skill = col1.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    exp_order = ['경력무관', '주니어(1~2년)', '미드(3~4년)', '시니어(5년+)']
    selected_exp = col2.selectbox("경력 연차 선택", ["전체"] + exp_order)
    
    df = get_career_skills(selected_skill, selected_exp)
    
    if df.empty:
        st.warning("조건에 맞는 데이터가 없습니다.")
        return

    df['exp_group'] = pd.Categorical(df['exp_group'], categories=exp_order, ordered=True)
    
    unique_names = [selected_skill] + [n for n in df['name'].unique() if n != selected_skill] if selected_skill != "전체" else df['name'].unique()
    
    fig = px.bar(
        df.sort_values(['exp_group', 'name']), x="name", y="count", color="exp_group",
        template="plotly_dark", barmode="group",
        category_orders={"exp_group": exp_order, "name": unique_names}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["exp_group", "count"], ascending=[True, False]), use_container_width=True)