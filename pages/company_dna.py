import plotly.express as px
import streamlit as st

from utils.analysis import render_sidebar_filters, safe_load_df
from utils.queries import COMPANY_SKILLS


def render() -> None:
    st.header("🏢 기업별 기술 DNA")
    _, _, top_n = render_sidebar_filters(default_top_n=10)

    company_df = safe_load_df(COMPANY_SKILLS)
    if company_df.empty:
        st.info("기업별 기술 DNA 데이터를 불러올 수 없습니다.")
        return

    company_counts = company_df.groupby(["company_name", "name"]).size().reset_index(name="count")
    top_companies = company_counts.groupby("company_name", as_index=False)["count"].sum().sort_values("count", ascending=False).head(top_n)["company_name"]
    heatmap_df = company_counts[company_counts["company_name"].isin(top_companies)].pivot(index="company_name", columns="name", values="count").fillna(0)

    fig = px.imshow(heatmap_df, aspect="auto", color_continuous_scale="Blues", labels=dict(x="기술", y="기업", color="공고 수"))
    fig.update_layout(title="기업별 기술 선호도 히트맵", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
