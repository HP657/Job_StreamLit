import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill, selected_exp):
    with engine.connect() as conn:
        # 1. 경력 그룹화 표준화 (신입 데이터 누락 방지)
        exp_mapping = """
        CASE 
            WHEN experience IN ('신입', '0년 이상', '신입(0년)') THEN '신입(0년)'
            WHEN experience IN ('1년 이상', '2년 이상') THEN '주니어(1~2년)'
            WHEN experience IN ('3년 이상', '4년 이상') THEN '미드(3~4년)'
            WHEN experience IN ('5년 이상', '6년 이상', '7년 이상', '8년 이상', '10년 이상', '11년 이상', '15년 이상') THEN '시니어(5년+)'
            WHEN experience = '경력무관' THEN '경력무관'
            ELSE '경력무관' 
        END as exp_group
        """
        
        params = {}
        # 2. 연관 기술 추출 로직 (네트워크 방식 적용)
        if selected_skill and selected_skill != "전체":
            # 선택 기술과 같은 job_opening_id를 가진 다른 기술들을 찾음
            base_query = f"""
                SELECT s2.name, {exp_mapping}, COUNT(*) as count
                FROM job_opening_skills jos1
                JOIN skills s1 ON jos1.skill_id = s1.id
                JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id
                JOIN skills s2 ON jos2.skill_id = s2.id
                JOIN job_openings jo ON jos1.job_opening_id = jo.id
                WHERE s1.name = :skill_name
            """
        else:
            base_query = f"""
                SELECT s.name, {exp_mapping}, COUNT(*) as count
                FROM job_opening_skills jos
                JOIN skills s ON s.id = jos.skill_id
                JOIN job_openings jo ON jo.id = jos.job_opening_id
            """
            
        if selected_exp and selected_exp != "전체":
            base_query += f" AND {exp_mapping.replace('as exp_group', '')} = :exp "
            params["exp"] = selected_exp
        
        base_query += " GROUP BY s2.name, exp_group " if selected_skill != "전체" else " GROUP BY s.name, exp_group "
        
        df = pd.read_sql(text(base_query), conn, params=params if selected_skill != "전체" else {"exp": selected_exp} if selected_exp != "전체" else {})
        
        if df.empty: return df

        # 기술 선택 시, 연관 기술 중 빈도 높은 상위 10개 추출
        limit = 10
        top_skills = df.groupby('name')['count'].sum().nlargest(limit).index.tolist()
        return df[df['name'].isin(top_skills)]

def render(all_skills):
    st.header("📊 경력 단계별 분석")
    
    with st.expander("💡 분석 데이터 추출 로직 상세 안내"):
        st.markdown("""
        **1. 경력 표준화**: 원시 데이터를 5개 구간(신입, 주니어, 미드, 시니어, 경력무관)으로 표준화하여 신입 데이터 누락을 방지했습니다.
        **2. 연관 기술 추출 (Co-occurrence)**: 기술 선택 시, 해당 기술이 포함된 채용 공고에 함께 기재된 기술들만 연관 분석하여 추출합니다.
        **3. 조건부 로직**:
           - **기술 선택 시**: 선택 기술과 공고를 공유하는 연관 기술 상위 10개를 시각화합니다.
           - **경력 선택 시**: 해당 연차 구간의 데이터 비중을 유지하며 기술 수요를 집계합니다.
           - **둘 다 선택 시**: 필터링된 공고들 안에서 연관된 기술들만 재집계하여 랭킹을 산출합니다.
        """)
    
    col1, col2 = st.columns(2)
    selected_skill = col1.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    exp_order = ['신입(0년)', '주니어(1~2년)', '미드(3~4년)', '시니어(5년+)', '경력무관']
    selected_exp = col2.selectbox("경력 연차 선택", ["전체"] + exp_order)
    
    df = get_career_skills(selected_skill, selected_exp)
    
    if df.empty:
        st.warning("조건에 맞는 데이터가 없습니다.")
        return

    # 그래프 정렬 최적화
    df['exp_group'] = pd.Categorical(df['exp_group'], categories=exp_order, ordered=True)
    
    fig = px.bar(
        df.sort_values(['name', 'exp_group']), x="name", y="count", color="exp_group",
        template="plotly_dark", barmode="group",
        category_orders={"exp_group": exp_order}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["name", "exp_group"]), use_container_width=True)