import plotly.graph_objects as go
import json

# Use original data structure with proper totals
categories_abbrev = [
    "News API Sub",
    "AI/ML Analysis", 
    "Web Host/Infra",
    "Database Svc",
    "SSL Certs",
    "Domain Reg",
    "Monitoring",
    "TOTAL MONTHLY"
]

# Free solution costs (all zero)
free_costs = [0, 0, 0, 0, 0, 0, 0, 0]

# Paid alternatives costs (using high range from original data)
paid_costs = [500, 300, 200, 100, 50, 20, 100, 1270]

# Create the horizontal bar chart
fig = go.Figure()

# Add paid alternatives bars
fig.add_trace(go.Bar(
    y=categories_abbrev,
    x=paid_costs,
    name='Paid Alt',
    orientation='h', 
    marker_color='#B4413C',
    cliponaxis=False,
    text=[f'${x:,.0f}' if x >= 1000 else f'${x}' for x in paid_costs],
    textposition='auto'
))

# Add free solution bars (using green color as requested)
# Show as thin bars with clear $0 labels
fig.add_trace(go.Bar(
    y=categories_abbrev,
    x=[1 for _ in free_costs],  # Minimal visible width
    name='Free Solution',
    orientation='h',
    marker_color='#ECEBD5',  # Using light green from the brand colors
    cliponaxis=False,
    text=['$0' for _ in free_costs],
    textposition='auto'
))

# Update layout
fig.update_layout(
    title='Cost Breakdown: Free vs Paid Solutions',
    xaxis_title='Monthly Cost ($)',
    yaxis_title='Service Category',
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
    barmode='group'
)

# Format x-axis with proper scaling
fig.update_xaxes(
    tickformat='$,.0f'
)

# Reverse y-axis order so total is at bottom
fig.update_yaxes(
    categoryorder='array',
    categoryarray=categories_abbrev[::-1]
)

# Save the chart
fig.write_image('cost_comparison_chart.png')