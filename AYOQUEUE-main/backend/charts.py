import plotly.express as px

def generate_wait_time_chart(df):
    # Create a copy to avoid SettingWithCopyWarning
    df_chart = df.copy()
    
    # Calculate dynamic rolling average based on number of students
    window_size = max(5, len(df) // 20)
    rolling_label = f'Rolling Avg ({window_size} Students)'
    df_chart[rolling_label] = df_chart['Wait Time (Mins)'].rolling(window=window_size, min_periods=1).mean()
    
    # Create line chart using plotly.express
    fig = px.line(
        df_chart,
        x='Student Number',
        y=['Wait Time (Mins)', rolling_label],
        title='Queue Simulation: Student Wait Times'
    )
    
    # Update traces for specific colors and widths
    fig.update_traces(
        selector=dict(name='Wait Time (Mins)'),
        line=dict(color='#df9ea9', width=1)
    )
    
    fig.update_traces(
        selector=dict(name=rolling_label),
        line=dict(color='#c51e3a', width=4)
    )
    
    # Update layout to match strict color palette
    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font=dict(color='#282320'),
        title=dict(
            font=dict(color='#c51e3a', size=20)
        ),
        xaxis=dict(
            title_font=dict(color='#282320'),
            tickfont=dict(color='#282320'),
            showgrid=True,
            gridcolor='#f0f0f0'  # subtle grid for readability
        ),
        yaxis=dict(
            title_font=dict(color='#282320'),
            tickfont=dict(color='#282320'),
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        legend=dict(
            font=dict(color='#282320'),
            title_text=''  # Remove legend title
        )
    )
    
    return fig
