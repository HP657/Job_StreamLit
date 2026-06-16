import streamlit as st
import plotly.express as px
import pandas as pd
from sqlalchemy import text
from db import engine

def get_career_skills(selected_skill, selected_exp):
    with engine.connect() as conn:
        # 데이터 누락 방지를 위해 CASE 문 보완 (신입 명확히 포함)
        exp_mapping = """
        CASE 
            WHEN experience = '신입' THEN '신입(0년)'
            WHEN experience IN ('1년 이상', '2년 이상') THEN '주니어(1~2년)'
            WHEN experience IN ('3년 이상', '4년 이상') THEN '미드(3~4년)'
            WHEN experience IN ('5년 이상', '6년 이상', '7년 이상', '8년 이상', '10년 이상', '11년 이상', '15년 이상') THEN '시니어(5년+)'
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
        """)
        df = pd.read_sql(sql, conn, params=params)
        
        if df.empty: return df

        # 기술 선택 시, 선택한 기술이 맨 왼쪽(첫 번째)에 오도록 정렬 로직 추가
        if selected_skill and selected_skill != "전체":
            unique_skills = [selected_skill] + [s for s in df['name'].unique() if s != selected_skill]
        else:
            unique_skills = df.groupby('name')['count'].sum().nlargest(8).index.tolist()
            
        return df[df['name'].isin(unique_skills[:8])]

def render(all_skills):
    st.header("📊 경력 단계별 분석")
    
    with st.expander("💡 분석 데이터 추출 로직 상세 안내"):
        st.markdown("""
        **1. 데이터 매핑 로직**
        - 채용 공고의 원시 경력 데이터를 5개 구간(신입~시니어)으로 표준화하여 누락 없는 그룹화 수행.
        
        **2. 추출 알고리즘**
        - **전체 조회**: 각 기술별 전체 빈도수를 합산하여 상위 8개 기술을 선정한 뒤 경력별 분포를 표시.
        - **기술 선택 시**: 선택한 기술을 축의 가장 왼쪽에 배치하고, 연관 기술들을 우선적으로 필터링.
        - **경력 선택 시**: 선택한 연차 구간에 해당하는 데이터만 추출하여 해당 구간의 핵심 스택 상위 10개 추출.
        
        **3. 시각화 원칙**
        - 선택하신 조건이 그래프의 정렬 순서 및 데이터 범위에 즉각 반영되어 커리어 로드맵을 투명하게 제시합니다.
        """)
    
    col1, col2 = st.columns(2)
    selected_skill = col1.selectbox("분석할 기술 선택", ["전체"] + all_skills)
    exp_order = ['신입(0년)', '주니어(1~2년)', '미드(3~4년)', '시니어(5년+)', '경력무관']
    selected_exp = col2.selectbox("경력 연차 선택", ["전체"] + exp_order)
    
    df = get_career_skills(selected_skill, selected_exp)
    
    if df.empty:
        st.warning("조건에 맞는 데이터가 없습니다.")
        return

    # 그래프 렌더링
    df['exp_group'] = pd.Categorical(df['exp_group'], categories=exp_order, ordered=True)
    
    # 선택 기술 우선순위 정렬 반영
    unique_names = [selected_skill] + [n for n in df['name'].unique() if n != selected_skill] if selected_skill != "전체" else df['name'].unique()
    
    fig = px.bar(
        df.sort_values('exp_group'), x="name", y="count", color="exp_group",
        template="plotly_dark", barmode="group",
        category_orders={"exp_group": exp_order, "name": unique_names}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 요청하신 상세 표 복구
    st.subheader("📋 상세 데이터")
    st.dataframe(df.sort_values(["exp_group", "count"], ascending=[True, False]), use_container_width=True)