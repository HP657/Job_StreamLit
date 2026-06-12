import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from db import load_df
from utils.analysis import render_sidebar_filters
from utils.queries import SKILL_NETWORK, SKILL_ID_MAP


def render() -> None:
    st.header("🕸️ 기술 연관성 네트워크")
    _, _, top_n = render_sidebar_filters(default_top_n=10)

    network_df = load_df(SKILL_NETWORK)
    id_map_df = load_df(SKILL_ID_MAP)
    if network_df.empty or id_map_df.empty:
        st.info("네트워크 데이터를 불러올 수 없습니다.")
        return

    id_to_name = dict(zip(id_map_df["id"], id_map_df["name"]))
    top_edges = network_df.sort_values("freq", ascending=False).head(top_n).copy()

    graph = nx.Graph()
    for _, row in top_edges.iterrows():
        graph.add_edge(
            id_to_name.get(row["base_skill"], str(row["base_skill"])),
            id_to_name.get(row["related_skill"], str(row["related_skill"])),
            weight=float(row["freq"]),
        )

    pos = nx.spring_layout(graph, seed=42)
    edge_x = []
    edge_y = []
    for u, v, data in graph.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = [pos[n][0] for n in graph.nodes()]
    node_y = [pos[n][1] for n in graph.nodes()]
    node_text = list(graph.nodes())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(color="lightgray", width=1), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", text=node_text, textposition="top center", marker=dict(size=18, color="rgba(31,119,180,0.85)"), hovertemplate="%{text}<extra></extra>"))
    fig.update_layout(title="기술 연관성 네트워크", xaxis=dict(showgrid=False, zeroline=False, visible=False), yaxis=dict(showgrid=False, zeroline=False, visible=False), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("※ 상위 N개 연결만 유지해 네트워크 밀도를 낮추고, 마우스 오버 시 기술 이름을 확인할 수 있습니다.")
