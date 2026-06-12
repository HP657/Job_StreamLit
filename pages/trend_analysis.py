import streamlit as st
import pandas as pd
import plotly.express as px
from db import load_df

def get_trend_data():
    # 쿼리: 날짜를 'YYYY-MM' 형식의 문자열로 확실히 변환합니다.
    query = """
    SELECT 
        TO_CHAR(jo.created_at, 'YYYY-MM') as month,
        s.name as skill_name,
        COUNT(*) as count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY month, skill_name
    ORDER BY month ASC
    """
    return load_df(query)

def render():
    st.header("📈 시장 기술 트렌드 추이")

    df = get_trend_data()
    
    if df.empty:
        st.warning("데이터가 아직 없습니다.")
        return

    # 피벗 테이블 생성
    pivot_df = df.pivot(index='month', columns='skill_name', values='count').fillna(0)
    
    # 상위 5개 기술만 남기기
    top_skills = pivot_df.sum().nlargest(5).index
    pivot_df = pivot_df[top_skills]
    """
    # X축을 인덱스(연도-월)로 명시하여 범주형으로 그립니다.
    # plotly.express.area는 데이터프레임의 index를 X축으로 사용합니다.
    fig = px.area(
        pivot_df, 
        x=pivot_df.index, 
        y=pivot_df.columns,
        labels={"value": "언급 빈도", "index": "연도-월", "skill_name": "기술 스택"},
        title="시간 흐름에 따른 상위 5개 기술 점유율 변화"
    )

    # 레이아웃 조정
    fig.update_layout(
        hovermode="x unified",
        xaxis_type="category" # X축을 날짜 타임스탬프가 아닌 범주형으로 강제 설정
    )

    st.plotly_chart(fig, use_container_width=True)
    """
    # 3. 시각화: area 대신 bar 사용 (누적 막대 그래프)
    # 데이터를 long format으로 변환해야 bar 차트에서 stack이 가능합니다.
    df_long = pivot_df.reset_index().melt(id_vars='month', var_name='기술 스택', value_name='언급 빈도')
    
    fig = px.bar(
        df_long, 
        x='month', 
        y='언급 빈도', 
        color='기술 스택',
        title="시간 흐름에 따른 상위 5개 기술 점유율 변화",
        barmode='stack' # 누적 막대 형태로 설정
    )

    fig.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("데이터 상세 보기"):
        st.dataframe(pivot_df)