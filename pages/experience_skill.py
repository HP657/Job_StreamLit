import plotly.express as px
import streamlit as st

from utils.analysis import render_sidebar_filters, safe_load_df


def render() -> None:
    st.header("📊 경력 단계별 핵심 스킬")
    _, _, top_n = render_sidebar_filters(default_top_n=5)

    query = """
    SELECT
        jo.experience_level AS career_level,
        s.name AS skill,
        COUNT(*) AS demand_count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    WHERE jo.experience_level IS NOT NULL
    GROUP BY 1, 2
    ORDER BY 1, 2
    """

    exp_df = safe_load_df(query)
    if exp_df.empty:
        st.info("경력 단계별 기술 데이터를 불러올 수 없습니다.")
        return

    top_skills = (
        exp_df.groupby("skill", as_index=False)["demand_count"]
        .sum()
        .sort_values("demand_count", ascending=False)
        .head(top_n)["skill"]
        .tolist()
    )
    bar_df = exp_df[exp_df["skill"].isin(top_skills)].copy()
    fig = px.bar(bar_df, x="skill", y="demand_count", color="career_level", barmode="group", text="demand_count", labels={"skill": "기술", "demand_count": "공고 수", "career_level": "경력 단계"})
    fig.update_layout(title="경력 단계별 핵심 스킬 비교", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
