# dash_app/app.py
import dash
import os
from dash import html, dcc, Input, Output
from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import networkx as nx
import scipy as sp
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, requests_pathname_prefix='/mastodondash/')

mongo_uri = os.getenv('MONGO_URI')
mongo_db_name = os.getenv('MONGO_DB_A')

# MongoDB client setup
client = MongoClient(mongo_uri)
analytics_db = client[mongo_db_name]

# Collections
postsperday_collection = analytics_db['postsperday']
dailyactiveusers_collection = analytics_db['dailyactiveusers']
averageuseractivity_collection = analytics_db['averageuseractivity']

# Metadata for instances
instance_metadata = {
    'https://mstdn.social': {'Language': 'English'},
    'https://mastodon.social': {'Language': 'English'},
    'https://mas.to': {'Language': 'English'},
    'https://mastodon.world': {'Language': 'English'},
    'https://mstdn.jp': {'Language': 'Japanese'},
    'https://hachyderm.io': {'Language': 'English'},
    'https://infosec.exchange': {'Language': 'English'},
    'https://planet.moe': {'Language': 'Korean'},
    'https://social.vivaldi.net': {'Language': 'English'},
    'https://techhub.social': {'Language': 'English'},
    'https://piaille.fr': {'Language': 'French'},
    'https://mastodon.gamedev.place': {'Language': 'English'},
    'https://mastodon.nl': {'Language': 'Dutch'},
    'https://norden.social': {'Language': 'English'},
    'https://alive.bar': {'Language': 'Chinese'},
    'https://mathstodon.xyz': {'Language': 'English'},
    'https://kolektiva.social': {'Language': 'English'},
    'https://universeodon.com': {'Language': 'English'},
    'https://mastodonapp.uk': {'Language': 'English'},
    'https://mastodon.uno': {'Language': 'Italian'},
}

instance_tag_metadata = {
    'https://mstdn.social': {'Tag': 'General'},
    'https://mastodon.social': {'Tag': 'General'},
    'https://mas.to': {'Tag': 'General'},
    'https://mstdn.jp': {'Tag': 'General'},
    'https://hachyderm.io': {'Tag': 'Technology'},
    'https://infosec.exchange': {'Tag': 'Technology'},
    'https://planet.moe': {'Tag': 'None'},
    'https://social.vivaldi.net': {'Tag': 'General'},
    'https://techhub.social': {'Tag': 'Technology'},
    'https://piaille.fr': {'Tag': 'General'},
    'https://mastodon.gamedev.place': {'Tag': 'Gaming'},
    'https://mastodon.nl': {'Tag': 'General'},
    'https://norden.social': {'Tag': 'Regional'},
    'https://alive.bar': {'Tag': 'None'},
    'https://mathstodon.xyz': {'Tag': 'Technology'},
    'https://kolektiva.social': {'Tag': 'Activism'},
    'https://universeodon.com': {'Tag': 'General'},
    'https://mastodonapp.uk': {'Tag': 'Regional'},
    'https://mastodon.uno': {'Tag': 'General'},
}

language_color_map = {
    'English': '#1f77b4',
    'Japanese': '#ff7f0e',
    'Korean': '#2ca02c',
    'French': '#d62728',
    'Dutch': '#9467bd',
    'Chinese': '#8c564b',
    'German': '#e377c2',
    'Italian': '#7f7f7f'
}

tag_color_map = {
    'General': '#1f77b4',
    'Technology': '#ff7f0e',
    'Gaming': '#2ca02c',
    'Regional': '#d62728',
    'Activism': '#9467bd',
    'None': '#8c564b'
}


app.layout = html.Div(children=[

    html.Div([
        html.A(
            html.Img(
                src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                style={"height": "25px", "margin-right": "10px"}
            ),
            href="https://github.com/dremyyy/mastodon_master",
            target="_blank"
        ),
        html.H1(
            "Mastodon Data Dashboard",
            style={"textAlign": "center", "flex": "1", "font-family": "Arial, sans-serif", "font-size": "25px", "margin": "0"}
        )
    ], style={
        "display": "flex",
        "align-items": "center",
        "justify-content": "center",
        "gap": "10px",
        "margin-bottom": "10px"
    }),


    dcc.Tabs(
        id="tabs",
        value="data-tab",
        children=[
            dcc.Tab(label="Data", value="data-tab"),
            dcc.Tab(label="Correlation", value="correlation-tab"),
        ],
        style={"font-size": "16px", "font-family": "Arial, sans-serif", "line-height": "0px"}
    ),


    html.Div(id="tab-content")
])


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab_content(selected_tab):
    """Render the selected tab content dynamically."""
    if selected_tab == "data-tab":
        return html.Div([
            # Centered Date Picker
            html.Div([
                dcc.DatePickerRange(
                    id="date-range-picker",
                    min_date_allowed=datetime(2024, 10, 24),
                    max_date_allowed=(datetime.now() - timedelta(days=1)),
                    start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    end_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                ),
            ], style={"textAlign": "center", "margin-bottom": "0px", "margin-top": "15px", "padding": "0px 0px", "height": "5px", "font-family": "Arial, sans-serif"}),

            # Checkbox for SMA selection (Only in Data Tab)
            html.Div([
                dcc.Checklist(
                    id="data-ema-toggle",
                    options=[{"label": " Use 7-Day SMA", "value": "ema"}],
                    value=[],  # Default: unchecked
                    inline=True
                ),
            ], style={"textAlign": "center", "margin-top": "50px", "font-family": "Arial, sans-serif"}),

            # Graphs
            dcc.Graph(id="posts-line-chart", style={"width": "100%", "height": "600px"}),
            dcc.Graph(id="active-users-line-chart", style={"width": "100%", "height": "600px"}),
            dcc.Graph(id="avg-user-activity-line-chart", style={"width": "100%", "height": "600px"})
        ])

    elif selected_tab == "correlation-tab":
        return html.Div([
            #html.H3("Correlation Analysis",
             #       style={"textAlign": "center", "margin-top": "20px", "font-family": "Arial, sans-serif"}),

            # Data Selection Dropdown


            # Date Picker for correlation analysis
            html.Div([
                dcc.DatePickerRange(
                    id="correlation-date-picker",
                    min_date_allowed=datetime(2024, 10, 24),
                    max_date_allowed=(datetime.now() - timedelta(days=1)),
                    start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    end_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                ),
            ], style={"font-size": "5px", "textAlign": "center", "margin-bottom": "0px", "margin-top": "15px", "padding": "0px 0px", "height": "5px", "font-family": "Arial, sans-serif"}),

            # Checkbox for SMA selection
            html.Div([
                dcc.Checklist(
                    id="ema-toggle",
                    options=[{"label": " Use 7-Day SMA", "value": "ema"}],
                    value=[],
                    inline=True
                ),
            ], style={"textAlign": "center", "margin-top": "50px", "font-family": "Arial, sans-serif"}),


            html.Div([
                dcc.Dropdown(
                    id="data-type-selector",
                    options=[
                        {"label": "Number of Active Users", "value": "active_users"},
                        {"label": "Number of Posts", "value": "post_count"},
                        {"label": "Average Posts Per User", "value": "avg_posts_per_user"}
                    ],
                    value="active_users",  # Default to Active Users
                    clearable=False
                ),
            ], style={"width": "15%", "margin": "auto", "margin-top": "10px", "margin-bottom": "0px", "font-family": "Arial, sans-serif"}),

            # Correlation Matrix Graph
            dcc.Graph(id="correlation-matrix", style={"width": "100%", "height": "800px"}),

            # Network Graph for Correlation
            dcc.Graph(id="correlation-network", style={"width": "100%", "height": "500px"}),

            dcc.Graph(id="correlation-network-tag", style={"width": "100%", "height": "500px"})
        ])


@app.callback(
    [Output("posts-line-chart", "figure"),
     Output("active-users-line-chart", "figure"),
     Output("avg-user-activity-line-chart", "figure")],
    [Input("date-range-picker", "start_date"),
     Input("date-range-picker", "end_date"),
     Input("data-ema-toggle", "value")]
)
def update_data_charts(start_date, end_date, ema_option):
    """Fetch precomputed post counts, active users, and avg user activity per day with optional SMA."""
    if not start_date or not end_date:
        empty_fig = go.Figure().update_layout(title="No Data Available", height=600)
        return empty_fig, empty_fig, empty_fig

    # Fetch Data
    cursor = postsperday_collection.find({"date": {"$gte": start_date, "$lte": end_date}})
    df_posts = pd.DataFrame(list(cursor))

    cursor = dailyactiveusers_collection.find({"date": {"$gte": start_date, "$lte": end_date}})
    df_users = pd.DataFrame(list(cursor))

    cursor = averageuseractivity_collection.find({"date": {"$gte": start_date, "$lte": end_date}})
    df_avg_activity = pd.DataFrame(list(cursor))

    for df in [df_posts, df_users, df_avg_activity]:
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])

    # Pivot Data
    posts_per_day = df_posts.pivot(index="date", columns="instance", values="post_count").fillna(0) if not df_posts.empty else None
    active_users_per_day = df_users.pivot(index="date", columns="instance", values="active_users").fillna(0) if not df_users.empty else None
    avg_user_activity_per_day = df_avg_activity.pivot(index="date", columns="instance", values="avg_posts_per_user").fillna(0) if not df_avg_activity.empty else None

    # Apply 7-day SMA if checkbox is checked
    if "ema" in ema_option:
        if posts_per_day is not None:
            posts_per_day = posts_per_day.rolling(window=7, min_periods=7).mean().dropna()
        if active_users_per_day is not None:
            active_users_per_day = active_users_per_day.rolling(window=7, min_periods=7).mean().dropna()
        if avg_user_activity_per_day is not None:
            avg_user_activity_per_day = avg_user_activity_per_day.rolling(window=7, min_periods=7).mean().dropna()

    # Create Figures
    fig_posts, fig_users, fig_avg_activity = go.Figure(), go.Figure(), go.Figure()

    for df, fig, title, y_title in [
        (posts_per_day, fig_posts, "Number of Posts per Day", "Number of Posts"),
        (active_users_per_day, fig_users, "Number of Active Users per Day", "Active Users"),
        (avg_user_activity_per_day, fig_avg_activity, "Avg Posts Per User Per Day", "Avg Posts Per User"),
    ]:
        if df is not None:
            for instance in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[instance],
                    mode="lines+markers",
                    name=instance,
                    hovertemplate=f"<b>{instance}</b><br>Date: %{{x}}<br>Value: %{{y}}<extra></extra>"

                ))
            fig.update_layout(title=title, yaxis_title=y_title, height=600)

    return fig_posts, fig_users, fig_avg_activity


@app.callback(
    [Output("correlation-matrix", "figure"),
     Output("correlation-network", "figure"),
     Output("correlation-network-tag", "figure")],
    [Input("correlation-date-picker", "start_date"),
     Input("correlation-date-picker", "end_date"),
     Input("ema-toggle", "value"),
     Input("data-type-selector", "value")]
)
def update_correlation_analysis(start_date, end_date, ema_option, data_type):
    if not start_date or not end_date:
        return {}, {}

    collection_map = {
        "active_users": dailyactiveusers_collection,
        "post_count": postsperday_collection,
        "avg_posts_per_user": averageuseractivity_collection
    }
    selected_collection = collection_map[data_type]

    cursor = selected_collection.find(
        {"date": {"$gte": start_date, "$lte": end_date}},
        {"_id": 0, "date": 1, "instance": 1, data_type: 1}
    )
    df_data = pd.DataFrame(list(cursor))

    if df_data.empty:
        return {}, {}

    df_data["date"] = pd.to_datetime(df_data["date"])
    selected_data_per_day = df_data.pivot(index="date", columns="instance", values=data_type).fillna(0)

    if "ema" in ema_option:
        selected_data_per_day = selected_data_per_day.rolling(window=7, min_periods=7).mean().dropna()

    correlation_matrix = selected_data_per_day.corr(method='spearman')

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns.tolist(),
        y=correlation_matrix.index.tolist(),
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        colorbar=dict(title="Correlation"),
        hoverongaps=False
    ))

    annotations = []
    for i in range(len(correlation_matrix.index)):
        for j in range(len(correlation_matrix.columns)):
            value = correlation_matrix.iloc[i, j]
            annotations.append(
                dict(
                    x=correlation_matrix.columns[j],
                    y=correlation_matrix.index[i],
                    text=f"{value:.2f}",
                    showarrow=False,
                    font=dict(color="black" if abs(value) < 0.5 else "white"),
                )
            )

    fig_heatmap.update_layout(
        title=f"Spearman Correlation Matrix ({data_type.replace('_', ' ').title()}) {(' (7-Day SMA)' if 'ema' in ema_option else '')} ({start_date} to {end_date})",
        xaxis_title="Instance",
        yaxis_title="Instance",
        annotations=annotations,
        height=800
    )

    G = nx.Graph()
    correlation_matrix_clipped = correlation_matrix.clip(lower=0)

    epsilon = 0.01
    for i, instance1 in enumerate(correlation_matrix_clipped.columns):
        for j, instance2 in enumerate(correlation_matrix_clipped.columns):
            if i != j:
                weight = correlation_matrix_clipped.iloc[i, j]
                if weight > 0:
                    transformed_weight = 1 / (abs(weight) + epsilon)
                    G.add_edge(instance1, instance2, weight=transformed_weight)

    pos = nx.kamada_kawai_layout(G, weight="weight")

    edge_x, edge_y = [], []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x, node_y, node_text, node_color = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        lang = instance_metadata.get(node, {}).get('Language', 'English')
        color = language_color_map.get(lang, '#1f77b4')  # default blue

        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_color.append(color)

    fig_network = go.Figure()

    fig_network.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=0.5, color="gray"),
        hoverinfo="none",
        showlegend=False
    ))

    # Add nodes grouped by language for legend
    from collections import defaultdict
    grouped_nodes = defaultdict(list)
    grouped_coords = defaultdict(list)

    for i, node in enumerate(G.nodes()):
        lang = instance_metadata.get(node, {}).get('Language', 'English')
        grouped_nodes[lang].append(node)
        grouped_coords[lang].append((node_x[i], node_y[i]))

    for lang, nodes in grouped_nodes.items():
        coords = grouped_coords[lang]
        fig_network.add_trace(go.Scatter(
            x=[x for x, y in coords],
            y=[y for x, y in coords],
            mode="markers+text",
            marker=dict(size=20, color=language_color_map.get(lang, '#1f77b4')),
            text=nodes,
            textposition="top center",
            hoverinfo="text",
            name=lang
        ))

    fig_network.update_layout(
        title="Network Graph of Spearman Correlations (Language Colored)",
        showlegend=True,
        legend=dict(title="Language", orientation="h", yanchor="bottom"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )

    #TAG BASED

    fig_network_tag = go.Figure()

    # node_color_tag = []
    grouped_tag_nodes = defaultdict(list)
    grouped_tag_coords = defaultdict(list)

    for i, node in enumerate(G.nodes()):
        tag = instance_tag_metadata.get(node, {}).get('Tag', 'None')
        grouped_tag_nodes[tag].append(node)
        grouped_tag_coords[tag].append((node_x[i], node_y[i]))

    fig_network_tag.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=0.5, color="gray"),
        hoverinfo="none",
        showlegend=False
    ))

    for tag, nodes in grouped_tag_nodes.items():
        coords = grouped_tag_coords[tag]
        fig_network_tag.add_trace(go.Scatter(
            x=[x for x, y in coords],
            y=[y for x, y in coords],
            mode="markers+text",
            marker=dict(size=20, color=tag_color_map.get(tag, '#1f77b4')),
            text=nodes,
            textposition="top center",
            hoverinfo="text",
            name=tag
        ))

    fig_network_tag.update_layout(
        title="Network Graph of Spearman Correlations (Tag Colored)",
        showlegend=True,
        legend=dict(title="Tag", orientation="h", yanchor="bottom"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )

    return fig_heatmap, fig_network, fig_network_tag

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)
