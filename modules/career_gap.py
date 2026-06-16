import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill, selected_exp):
    with engine.connect() as conn:
        # 1. 경력 그룹화 매핑 (신입 데이터 누락 방지)
        exp_mapping = """
        CASE 
            WHEN experience IN ('신입', '0년 이상', '신입(0년)') THEN '신입(0년)'
            WHEN experience IN ('1년 이상', '2년 이상') THEN '주니어(1~2년)'
            WHEN experience IN ('3년 이상', '4년 이상') THEN '미드(3~4년)'
            WHEN experience IN ('5년 이상', '6년 이상', '7년 이상', '8년 이상', '10년 이상', '11년 이상', '15년 이상') THEN '시니어(5년+)'
            ELSE '경력무관' 
        END
        """
        
        # 2. 쿼리 구성
        params = {}
        where_clauses = []
        
        # 기술 선택 시 연관 분석을 위한 조인 조건 및 필터
        if selected_skill and selected_skill != "전체":
            sql = f"""
                SELECT s2.name, {exp_mapping} as exp_group, COUNT(*) as count
                FROM job_opening_skills jos1
                JOIN skills s1 ON jos1.skill_id = s1.id
                JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id
                JOIN skills s2 ON jos2.skill_id = s2.id
                JOIN job_openings jo ON jos1.job_opening_id = jo.id
                WHERE s1.name = :skill_name
            """
            params["skill_name"] = selected_skill
        else:
            # 전체 조회
            sql = f"""
                SELECT s.name, {exp_mapping} as exp_group, COUNT(*) as count
                FROM job_opening_skills jos
                JOIN skills s ON s.id = jos.skill_id
                JOIN job_openings jo ON jo.id = jos.job_opening_id
            """
            
        # 경력 조건 추가
        if selected_exp and selected_exp != "전체":
            sql += f" AND ({exp_mapping}) = :exp "
            params["exp"] = selected_exp
        
        sql += " GROUP BY 1, 2 ORDER BY count DESC "
        
        # 3. 데이터 로드
        df = pd.read_sql(text(sql), conn, params=params)
        
        if df.empty: return df

        # 4. 상위 10개 필터링
        top_skills = df.groupby('name')['count'].sum().nlargest(10).index.tolist()
        return df[df['name'].isin(top_skills)]

def render(all_skills):
    st.header("📊 경력 단계별 분석")
    
    with st.expander("💡 분석 로직 상세 안내"):
        st.markdown("""
        - **기술 연관 로직**: 특정 기술을 선택하면 해당 기술이 포함된 공고를 찾고, 그 공고에 같이 등장하는(Co-occurrence) 기술들의 경력별 분포를 분석합니다.
        - **경력 표준화**: 10개 이상의 파편화된 경력 데이터를 5개 그룹으로 통합하여 분석 신뢰도를 높였습니다.
        - **정렬 기준**: 선택한 기술이 있는 경우 해당 기술을 그래프의 최좌측에 배치하고, 전체 조회 시 빈도가 높은 순으로 정렬합니다.
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
    
    # 선택 기술 우선순위 정렬 반영
    unique_names = [selected_skill] + [n for n in df['name'].unique() if n != selected_skill] if selected_skill != "전체" else df['name'].unique()
    
    fig = px.bar(
        df.sort_values(['exp_group', 'name']), x="name", y="count", color="exp_group",
        template="plotly_dark", barmode="group",
        category_orders={"exp_group": exp_order, "name": unique_names}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["exp_group", "count"], ascending=[True, False]), use_container_width=True)