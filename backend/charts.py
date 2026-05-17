import plotly.graph_objects as go

def generate_wait_time_chart(df):
    # Create a copy to avoid SettingWithCopyWarning
    df_chart = df.copy()
    
    # Calculate dynamic rolling average based on number of students
    window_size = max(5, len(df) // 20)
    rolling_label = f'Rolling Avg ({window_size} Students)'
    df_chart[rolling_label] = df_chart['Wait Time (Mins)'].rolling(window=window_size, min_periods=1).mean()
    
    # Create line chart using plotly.graph_objects for better customization
    fig = go.Figure()
    
    # Raw wait times with area fill
    fig.add_trace(go.Scatter(
        x=df_chart['Student Number'],
        y=df_chart['Wait Time (Mins)'],
        mode='lines',
        name='Wait Time',
        line=dict(color='#df9ea9', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(223, 158, 169, 0.2)',
        hovertemplate='Student %{x}<br>Wait: %{y:.2f} mins<extra></extra>'
    ))
    
    # Rolling average line
    fig.add_trace(go.Scatter(
        x=df_chart['Student Number'],
        y=df_chart[rolling_label],
        mode='lines',
        name=rolling_label,
        line=dict(color='#c51e3a', width=3),
        hovertemplate='Student %{x}<br>Avg: %{y:.2f} mins<extra></extra>'
    ))
    
    # Update layout to match strict color palette and improve UI
    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#282320'),
        title=dict(
            text='Queue Simulation: Student Wait Times',
            font=dict(color='#c51e3a', size=20)
        ),
        xaxis=dict(
            title='Student Number',
            title_font=dict(color='#282320'),
            tickfont=dict(color='#282320'),
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title='Wait Time (Minutes)',
            title_font=dict(color='#282320'),
            tickfont=dict(color='#282320'),
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        legend=dict(
            font=dict(color='#282320'),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified'
    )
    
    return fig
