import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from db import load_df

def get_network_data():
    query = """
    SELECT s1.name AS skill1, s2.name AS skill2, COUNT(*) AS freq
    FROM job_opening_skills jos1
    JOIN job_opening_skills jos2 ON jos1.job_opening_id = jos2.job_opening_id 
         AND jos1.skill_id < jos2.skill_id
    JOIN skills s1 ON jos1.skill_id = s1.id
    JOIN skills s2 ON jos2.skill_id = s2.id
    GROUP BY s1.name, s2.name
    ORDER BY freq DESC
    LIMIT 40  -- 데이터를 조금 더 확보하여 관계를 명확히 함
    """
    return load_df(query)

def render(user_skill_map):
    st.header("🔗 기술 연관성 네트워크")
    
    df = get_network_data()
    if df.empty: return

    G = nx.from_pandas_edgelist(df, 'skill1', 'skill2', ['freq'])
    pos = nx.spring_layout(G, k=0.5, seed=42) # k값 조절로 노드 간격 확보

    # 1. 엣지(선) 그리기: 빈도에 따라 굵기 조절
    edge_x, edge_y, edge_width = [], [], []
    for u, v, d in G.edges(data=True):
        edge_x.extend([pos[u][0], pos[v][0], None])
        edge_y.extend([pos[u][1], pos[v][1], None])
        edge_width.append(d['freq'] * 0.1) # 빈도에 따른 굵기

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#555'), mode='lines')

    # 2. 노드(점) 그리기: 내 기술이면 강조
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
    for node in G.nodes():
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        node_text.append(node)
        
        # 강조 로직: 내 기술이면 빨간색, 아니면 하늘색
        if node in user_skill_map:
            node_color.append('#FF4B4B') # 강조색
            node_size.append(20)          # 더 크게
        else:
            node_color.append('skyblue')
            node_size.append(12)

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text,
                            textposition="top center", marker=dict(size=node_size, color=node_color))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20),
                                     plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("🔴 빨간 점: 보유 중인 기술 | 🔵 파란 점: 함께 학습하면 좋은 기술")