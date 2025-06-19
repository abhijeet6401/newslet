import plotly.graph_objects as go
import plotly.io as pio

# Define the architecture components with better positioning
components = [
    {
        "name": "Data Sources",
        "color": "#1FB8CD",
        "items": ["Yahoo Finance", "Reuters", "MarketWatch", "CNBC", "Benzinga"],
        "position": (1, 6),
        "width": 1.2,
        "height": 0.8
    },
    {
        "name": "Scraping Layer", 
        "color": "#FFC185",
        "items": ["Python Scraper", "BeautifulSoup", "RSS Parser"],
        "position": (1, 4.5),
        "width": 1.2,
        "height": 0.6
    },
    {
        "name": "AI Analysis",
        "color": "#ECEBD5",
        "items": ["FinBERT", "BART-CNN", "Sentiment", "Scoring"],
        "position": (1, 3),
        "width": 1.2,
        "height": 0.8
    },
    {
        "name": "Data Storage",
        "color": "#5D878F", 
        "items": ["SQLite DB", "Articles", "Results"],
        "position": (1, 1.5),
        "width": 1.2,
        "height": 0.6
    },
    {
        "name": "Web App",
        "color": "#D2BA4C",
        "items": ["Flask Server", "REST API", "Web Interface"],
        "position": (3.5, 1.5),
        "width": 1.2,
        "height": 0.6
    },
    {
        "name": "Output Gen",
        "color": "#B4413C",
        "items": ["Newsletter", "HTML/CSV/JSON", "Formatting"],
        "position": (6, 2.5),
        "width": 1.2,
        "height": 0.6
    },
    {
        "name": "Deployment",
        "color": "#964325",
        "items": ["Render.com", "Railway.app", "Fly.io"],
        "position": (6, 0.5),
        "width": 1.2,
        "height": 0.6
    }
]

# Create the figure
fig = go.Figure()

# Add component boxes
for comp in components:
    x, y = comp["position"]
    w, h = comp["width"], comp["height"]
    
    # Add rectangle for component
    fig.add_shape(
        type="rect",
        x0=x-w/2, y0=y-h/2,
        x1=x+w/2, y1=y+h/2,
        fillcolor=comp["color"],
        line=dict(color="white", width=2),
        opacity=0.9
    )
    
    # Add component title
    fig.add_annotation(
        x=x, y=y+h/4,
        text=f"<b>{comp['name']}</b>",
        showarrow=False,
        font=dict(size=14, color="black"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="black",
        borderwidth=1,
        borderpad=2
    )
    
    # Add component items as bullet points
    items_text = " • ".join(comp["items"])
    fig.add_annotation(
        x=x, y=y-h/4,
        text=items_text,
        showarrow=False,
        font=dict(size=10, color="black"),
        bgcolor="rgba(255,255,255,0.8)",
        borderwidth=0,
        width=w*80
    )

# Define flow connections with arrows
flows = [
    ((1, 6), (1, 4.5)),      # Sources -> Scraping
    ((1, 4.5), (1, 3)),      # Scraping -> AI
    ((1, 3), (1, 1.5)),      # AI -> Storage
    ((1, 1.5), (3.5, 1.5)),  # Storage -> Web App
    ((3.5, 1.5), (6, 2.5)),  # Web App -> Output
    ((3.5, 1.5), (6, 0.5))   # Web App -> Deployment
]

# Add flow arrows
for start, end in flows:
    # Calculate arrow positioning
    if start[0] == end[0]:  # Vertical arrow
        arrow_start_y = start[1] - 0.4
        arrow_end_y = end[1] + 0.3
        fig.add_annotation(
            x=end[0], y=arrow_end_y,
            ax=start[0], ay=arrow_start_y,
            arrowhead=3,
            arrowsize=2,
            arrowwidth=4,
            arrowcolor="#13343B",
            showarrow=True,
            text=""
        )
    else:  # Horizontal arrow
        arrow_start_x = start[0] + 0.6
        arrow_end_x = end[0] - 0.6
        fig.add_annotation(
            x=arrow_end_x, y=end[1],
            ax=arrow_start_x, ay=start[1],
            arrowhead=3,
            arrowsize=2,
            arrowwidth=4,
            arrowcolor="#13343B",
            showarrow=True,
            text=""
        )

# Add invisible scatter points for better spacing
fig.add_trace(go.Scatter(
    x=[comp["position"][0] for comp in components],
    y=[comp["position"][1] for comp in components],
    mode='markers',
    marker=dict(size=1, color='rgba(0,0,0,0)'),
    showlegend=False,
    hoverinfo='none'
))

# Update layout
fig.update_layout(
    title="Financial News System Flow",
    showlegend=False,
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[-0.5, 7.5]
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False, 
        showticklabels=False,
        range=[-0.5, 7]
    ),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white'
)

# Save the chart
fig.write_image("financial_news_system_architecture.png")