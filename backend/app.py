import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from simulation import run_parallel_mm1_sim
from charts import generate_wait_time_chart

# Page Config
st.set_page_config(
    page_title='AyoQueue',
    page_icon='⏳',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown("""
<style>
    /* Existing Risk Box CSS */
    .risk-box {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .risk-green  { background: #d4edda; color: #155724; border-left: 5px solid #28a745; }
    .risk-yellow { background: #fff3cd; color: #856404; border-left: 5px solid #ffc107; }
    .risk-red    { background: #f8d7da; color: #721c24; border-left: 5px solid #dc3545; }
    .summary-box {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border-left: 5px solid #4361ee;
        margin-top: 1rem;
        font-size: 0.95rem;
        color: #1a1a2e;
    }
    
    /* Custom Red Theming for Button */
    button[kind="primary"] {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #c82333 !important;
        border-color: #c82333 !important;
    }
    
    /* Custom Red Theming for Slider */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1>Ayo<span style="color: #dc3545;">Queue</span></h1>', unsafe_allow_html=True)

st.markdown('### University Registrar · M/M/1 Queue Simulation')

st.markdown('This simulation models the university registrar as a queuing system. It helps visualize student wait times, server utilization, and bottleneck risks to effectively optimize staffing and improve overall service efficiency.')
st.divider()

# Sidebar
with st.sidebar:
    st.header('Simulation Parameters')
    st.caption('Configure the queuing model inputs below:')
    avg_arrival = st.number_input(
        'Avg. Inter-Arrival Time (mins)', 
        value=2.45, step=0.01,
        help='Average time between student arrivals at Window 1'
    )
    avg_service = st.number_input(
        'Avg. Service Time (mins)', 
        value=3.18, step=0.01,
        help='Average time staff takes to process one transaction'
    )
    st.markdown('**Scenario Settings**')
    num_windows = st.slider(
        'Active Windows (Staff)', 
        min_value=1, max_value=5, value=1,
        help='Number of parallel staff serving students'
    )
    num_students = st.number_input(
        'Students to Simulate', 
        value=100, step=10, min_value=10
    )
    run_btn = st.button('▶ Run Simulation', use_container_width=True, type='primary')

# Helper: Risk Label
def risk_label(rho):
    pct = rho * 100
    if rho >= 1:
        return 'red', '🔴 UNSTABLE — Queue will grow infinitely at this rate.'
    elif rho >= 0.9:
        return 'red', f'🔴 CRITICAL RISK ({pct:.1f}%) — Severe delays are almost certain.'
    elif rho >= 0.7:
        return 'yellow', f'🟡 MODERATE RISK ({pct:.1f}%) — System is under stress. Consider adding staff during peak hours.'
    else:
        return 'green', f'🟢 STABLE ({pct:.1f}%) — Current staffing can handle the load comfortably.'

# Helper: Plain Language Summary
def plain_summary(rho, avg_wait, num_windows, num_students):
    staff_word = 'window' if num_windows == 1 else 'windows'
    if rho >= 1:
        return (
            f"With <b>{num_windows} {staff_word}</b> and the current arrival and service rates, "
            f"the queue is mathematically unstable — it will grow without bound. "
            f"At minimum, add one more staff member during peak hours."
        )
    return (
        f"With <b>{num_windows} active {staff_word}</b>, the registrar can handle the observed student load "
        f"at <b>{rho*100:.1f}% capacity</b>. Across {num_students} simulated students, "
        f"the average wait time is <b>{avg_wait:.2f} minutes</b>. "
        f"{'This setup has a healthy buffer before delays become severe.' if rho < 0.7 else 'The system is close to its limit — a sudden surge could cause significant delays.'}"
    )

# Session State
if 'results' not in st.session_state:
    st.session_state.results = None

# Run Simulation
if run_btn:
    with st.spinner('Running 1,000 simulation runs...'):
        df, utilization, steady_state = run_parallel_mm1_sim(
            avg_arrival, avg_service, num_students, num_windows
        )
    st.session_state.results = (df, utilization, steady_state)

# Display Results
if st.session_state.results:
    df, utilization, steady_state = st.session_state.results
    color, label = risk_label(utilization)
    st.markdown(f'<div class="risk-box risk-{color}">{label}</div>', unsafe_allow_html=True)

    if df is None:
        st.stop()

    avg_wait = df['Wait Time (Mins)'].mean()
    max_wait = df['Wait Time (Mins)'].max()
    pct_over_10 = (df['Wait Time (Mins)'] > 10).mean() * 100

    st.subheader('System Performance Metrics')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Server Utilization (ρ)', f"{utilization * 100:.1f}%")
    col2.metric('Avg. Wait Time', f"{avg_wait:.2f} mins")
    col3.metric('Max Wait Time', f"{max_wait:.2f} mins")
    col4.metric('Students Waiting >10 mins', f"{pct_over_10:.1f}%")

    # Steady-state metrics row
    if steady_state:
        st.subheader('Steady-State Analytical Metrics')
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Avg. Students in Queue (Lq)', f"{steady_state['Lq']:.4f}")
        c2.metric('Avg. Students in System (L)', f"{steady_state['L']:.4f}")
        c3.metric('Avg. Wait in Queue (Wq)', f"{steady_state['Wq']:.4f} mins")
        c4.metric('Avg. Time in System (W)', f"{steady_state['W']:.4f} mins")

    st.divider()

    st.subheader('Wait Time Visualization')
    
    # Chart
    fig = generate_wait_time_chart(df)
    st.plotly_chart(fig, use_container_width=True)

    # Plain language summary
    summary = plain_summary(utilization, avg_wait, num_windows, num_students)
    st.markdown(f'<div class="summary-box">💡 <b>Summary:</b> {summary}</div>', unsafe_allow_html=True)

    st.divider()