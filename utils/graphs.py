import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_radar_chart(user_skills: list[str], market_dict: dict, all_skills: list[str]) -> go.Figure:
    """사용자 역량 대비 시장 수요를 보여주는 레이더 차트."""
    top_skills = sorted(market_dict, key=market_dict.get, reverse=True)[:6]
    max_demand = max(market_dict.values()) if market_dict else 1

    categories = top_skills
    user_values = [1 if skill in user_skills else 0 for skill in categories]
    market_values = [market_dict.get(skill, 0) / max_demand * 100 for skill in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=user_values, theta=categories, fill='toself', name='보유 기술'))
    fig.add_trace(go.Scatterpolar(r=market_values, theta=categories, fill='toself', name='시장 요구'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='역량 갭 분석 (Radar Chart)',
        margin=dict(l=30, r=30, t=60, b=30),
    )
    return fig


def build_trend_area_chart(trend_df: pd.DataFrame) -> go.Figure:
    """상위 5개 기술의 월별 언급 빈도 추이를 보여주는 누적 영역 차트."""
    if trend_df.empty:
        return go.Figure().update_layout(title='시장 기술 트렌드 추이')

    top_skills = (
        trend_df.groupby('name', as_index=False)['skill_count']
        .sum()
        .sort_values('skill_count', ascending=False)
        .head(5)['name']
        .tolist()
    )
    filtered = trend_df[trend_df['name'].isin(top_skills)].copy()
    pivot = filtered.pivot_table(index='month', columns='name', values='skill_count', aggfunc='sum').fillna(0)

    fig = go.Figure()
    for skill in pivot.columns:
        fig.add_trace(go.Scatter(x=pivot.index, y=pivot[skill], mode='lines', stackgroup='one', name=skill))

    fig.update_layout(
        title='시장 기술 트렌드 추이 (Stacked Area Chart)',
        xaxis_title='월',
        yaxis_title='공고 언급 빈도',
        template='plotly_white',
        margin=dict(l=30, r=30, t=60, b=30),
    )
    return fig


def build_network_graph(network_df: pd.DataFrame, id_to_name: dict) -> go.Figure:
    """기술 간 연관성을 보여주는 네트워크 그래프."""
    if network_df.empty:
        return go.Figure().update_layout(title='기술 연관성 네트워크')

    top_edges = network_df.sort_values('freq', ascending=False).head(25).copy()
    top_edges['source'] = top_edges['base_skill'].map(id_to_name)
    top_edges['target'] = top_edges['related_skill'].map(id_to_name)

    nodes = sorted(set(top_edges['source']).union(set(top_edges['target'])))
    node_pos = {name: (i % 5, i // 5) for i, name in enumerate(nodes)}

    fig = go.Figure()

    for _, row in top_edges.iterrows():
        x0, y0 = node_pos[row['source']]
        x1, y1 = node_pos[row['target']]
        fig.add_trace(go.Scatter(x=[x0, x1, None], y=[y0, y1, None], mode='lines', line=dict(width=max(1, row['freq'] / 5)), hoverinfo='skip', showlegend=False))

    fig.add_trace(go.Scatter(
        x=[pos[0] for pos in node_pos.values()],
        y=[pos[1] for pos in node_pos.values()],
        mode='markers+text',
        text=list(node_pos.keys()),
        textposition='top center',
        marker=dict(size=18, color='lightseagreen'),
        hovertemplate='%{text}<extra></extra>',
        showlegend=False,
    ))

    fig.update_layout(
        title='기술 연관성 네트워크 (Network Graph)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template='plotly_white',
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


def build_company_heatmap(company_df: pd.DataFrame) -> go.Figure:
    """기업별 핵심 기술을 보여주는 히트맵."""
    if company_df.empty:
        return go.Figure().update_layout(title='기업별 기술 DNA 분석')

    pivot = pd.crosstab(company_df['company_name'], company_df['name']).fillna(0).astype(int)
    fig = px.imshow(
        pivot,
        labels=dict(x='기술', y='회사', color='언급 횟수'),
        color_continuous_scale='Blues',
        aspect='auto',
    )
    fig.update_layout(title='기업별 기술 DNA 분석 (Heatmap)', margin=dict(l=20, r=20, t=60, b=20))
    return fig


def build_experience_bar_chart(experience_df: pd.DataFrame) -> go.Figure:
    """경력 단계별 핵심 스킬 비교 막대 그래프."""
    if experience_df.empty:
        return go.Figure().update_layout(title='경력 단계별 핵심 스킬 비교')

    top_by_exp = []
    for exp, grp in experience_df.groupby('experience', sort=False):
        top = grp.sort_values('skill_count', ascending=False).head(5)
        top_by_exp.extend(top.to_dict('records'))

    chart_df = pd.DataFrame(top_by_exp)
    fig = px.bar(
        chart_df,
        x='name',
        y='skill_count',
        color='experience',
        barmode='group',
        labels={'name': '기술', 'skill_count': '언급 빈도', 'experience': '경력 단계'},
    )
    fig.update_layout(title='경력 단계별 핵심 스킬 비교 (Grouped Bar Chart)', template='plotly_white', margin=dict(l=30, r=30, t=60, b=30))
    return fig


def build_lifecycle_chart(growth_df: pd.DataFrame, skill_name=None) -> go.Figure:
    """기술 생애주기(언급 빈도 + 성장률)를 보여주는 이중 축 선 그래프."""
    if growth_df.empty:
        return go.Figure().update_layout(title='기술 생애주기 분석')

    target = growth_df if skill_name is None else growth_df[growth_df['name'] == skill_name]
    if target.empty:
        target = growth_df.head(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=target['name'], y=target['recent_count'], name='최근 1개월 언급 빈도', mode='lines+markers', yaxis='y1'))
    fig.add_trace(go.Scatter(x=target['name'], y=target['growth_rate'], name='성장률(%)', mode='lines+markers', yaxis='y2'))

    fig.update_layout(
        title='기술 생애주기 분석 (Dual-Axis Line Chart)',
        xaxis_title='기술',
        yaxis=dict(title='공고 언급 빈도'),
        yaxis2=dict(title='성장률(%)', overlaying='y', side='right'),
        template='plotly_white',
        margin=dict(l=30, r=30, t=60, b=30),
    )
    return fig
