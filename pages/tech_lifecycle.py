import plotly.graph_objects as go
import streamlit as st

from utils.analysis import render_sidebar_filters, safe_load_df


def render() -> None:
    st.header("🔄 기술 생애주기 분석")
    _, _, top_n = render_sidebar_filters(default_top_n=5)

    query = """
    SELECT
        s.name AS skill,
        DATE_TRUNC('month', jo.created_at) AS month,
        COUNT(*) AS demand_count
    FROM job_openings jo
    JOIN job_opening_skills jos ON jo.id = jos.job_opening_id
    JOIN skills s ON s.id = jos.skill_id
    GROUP BY 1, 2
    ORDER BY 1, 2
    """

    lifecycle_df = safe_load_df(query)
    if lifecycle_df.empty:
        st.info("기술 생애주기 데이터를 불러올 수 없습니다.")
        return

    top_skills = (
        lifecycle_df.groupby("skill", as_index=False)["demand_count"]
        .sum()
        .sort_values("demand_count", ascending=False)
        .head(top_n)["skill"]
        .tolist()
    )
    lifecycle_df = lifecycle_df[lifecycle_df["skill"].isin(top_skills)].copy()

    fig = go.Figure()
    for skill in top_skills:
        skill_df = lifecycle_df[lifecycle_df["skill"] == skill].sort_values("month")
        growth = skill_df["demand_count"].pct_change().fillna(0) * 100
        fig.add_trace(go.Scatter(x=skill_df["month"], y=skill_df["demand_count"], mode="lines+markers", name=f"{skill} 수요", yaxis="y1", hovertemplate="%{x}<br>공고 수: %{y}<extra></extra>"))
        fig.add_trace(go.Scatter(x=skill_df["month"], y=growth, mode="lines+markers", name=f"{skill} 성장률", yaxis="y2", line=dict(dash="dash"), hovertemplate="%{x}<br>성장률: %{y:.1f}%<extra></extra>"))

    fig.update_layout(title="기술 생애주기: 공고 수요 vs 성장률", yaxis=dict(title="공고 빈도"), yaxis2=dict(title="성장률 (%)", overlaying="y", side="right"), template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
