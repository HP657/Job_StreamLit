import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from db import load_df

def get_network_data():
    # 동일 공고에서 함께 등장한 스킬 쌍 추출 (쿼리 [3]번 응용)
    query = """
    SELECT s1.name AS skill1, s2.name AS skill2, COUNT(*) AS freq
    FROM job_opening_skills jos1
    JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id 
         AND jos1.skill_id < jos2.skill_id
    JOIN skills s1 ON jos1.skill_id = s1.id
    JOIN skills s2 ON jos2.skill_id = s2.id
    GROUP BY s1.name, s2.name
    ORDER BY freq DESC
    LIMIT 30
    """
    return load_df(query)

def render():
    st.header("🔗 기술 연관성 네트워크")
    
    df = get_network_data()
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 네트워크 생성
    G = nx.from_pandas_edgelist(df, 'skill1', 'skill2', ['freq'])
    pos = nx.spring_layout(G, seed=42)

    # 엣지(선) 그리기
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

    # 노드(점) 그리기
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text,
                            textposition="top center", hoverinfo='text',
                            marker=dict(size=10, color='skyblue'))

    # 그래프 렌더링
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=0)))
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("선이 굵거나 가깝게 위치한 기술들은 함께 사용될 확률이 높습니다. 이를 통해 함께 배우면 좋은 스킬 패키지를 확인하세요!")