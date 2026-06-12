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
    LIMIT 35  -- 노드 수를 적절히 제한하여 가독성 확보
    """
    return load_df(query)

def render(user_skill_map):
    st.header("🔗 기술 연관성 네트워크")
    
    df = get_network_data()
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 네트워크 생성
    G = nx.from_pandas_edgelist(df, 'skill1', 'skill2', ['freq'])
    
    # 노드 간격과 배치 최적화 (k값이 클수록 노드가 멀어짐)
    pos = nx.spring_layout(G, k=1.0, iterations=100, seed=42)

    # 엣지(선) 그리기
    edge_x, edge_y = [], []
    for u, v in G.edges():
        edge_x.extend([pos[u][0], pos[v][0], None])
        edge_y.extend([pos[u][1], pos[v][1], None])
    
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.7, color='#777'), mode='lines', hoverinfo='none')

    # 노드(점) 그리기
    node_x, node_y, node_color, node_size, node_text = [], [], [], [], []
    my_skills = list(user_skill_map.keys())

    for node in G.nodes():
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        node_text.append(node)
        
        # 색상 및 크기 로직
        if node in my_skills:
            node_color.append('#FF4B4B') # 보유 기술: 빨강
            node_size.append(18)
        elif any(neighbor in my_skills for neighbor in G.neighbors(node)):
            node_color.append('#00FFCC') # 추천 기술: 민트
            node_size.append(14)
        else:
            node_color.append('#4A90E2') # 일반 기술: 파랑
            node_size.append(10)

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=node_text,
        textposition="top center", textfont=dict(size=13, color='white'),
        hoverinfo='text', marker=dict(size=node_size, color=node_color, line=dict(width=1.5, color='white'))
    )

    # 그래프 렌더링
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False, hovermode='closest', 
                        margin=dict(t=50, b=50, l=50, r=50),
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 구분 범례
    st.markdown("""
    <div style="display: flex; gap: 20px; justify-content: center; padding: 10px; background: #262730; border-radius: 10px;">
        <span>🔴 <b>보유 기술</b></span>
        <span>🟢 <b>추천 기술</b></span>
        <span>🔵 <b>기타 연관 기술</b></span>
    </div>
    """, unsafe_allow_html=True)