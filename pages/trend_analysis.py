import streamlit as st
import pandas as pd
import plotly.express as px
from db import load_df

st.set_page_config(page_title="기술 트렌드 분석", layout="wide")

st.title("📈 시장 기술 트렌드 추이")

# 1. 데이터 로드 (DB 쿼리)
@st.cache_data
def get_trend_data():
    # job_openings와 skills 테이블을 조인하여 월별 스킬 빈도를 가져오는 쿼리 (쿼리는 본인의 DB 구조에 맞게 수정)
    query = """
    SELECT 
        to_char(jo.created_at, 'YYYY-MM') as month,
        s.name as skill_name,
        COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    """
    df = load_df(query)
    return df

df = get_trend_data()

# 2. 데이터 전처리 (Stacked Area Chart용 피벗)
pivot_df = df.pivot(index='month', columns='skill_name', values='count').fillna(0)
# 상위 5개 기술만 추출
top_skills = pivot_df.sum().nlargest(5).index
pivot_df = pivot_df[top_skills]

# 3. 시각화
fig = px.area(
    pivot_df, 
    x=pivot_df.index, 
    y=pivot_df.columns,
    labels={"value": "언급 빈도", "month": "연도-월", "skill_name": "기술 스택"},
    title="시간 흐름에 따른 상위 5개 기술 점유율 변화"
)

st.plotly_chart(fig, use_container_width=True)

st.write("### 분석 인사이트")
st.info("시간이 지남에 따라 점유율이 상승하거나 하락하는 기술 트렌드를 확인하여, 현재 시장에서 가장 선호되는 기술을 파악할 수 있습니다.")