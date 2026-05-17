import os
from simulation import run_parallel_mm1_sim
from charts import generate_wait_time_chart

if __name__ == '__main__':
    # Baseline time study data
    avg_arrival = 2.45
    avg_service = 3.18
    num_students = 100
    num_windows = 2  # Change to 2 to test successful export
    
    print(f"Running simulation with {num_windows} window(s)...")
    
    df, utilization, steady_state = run_parallel_mm1_sim(
        arrival_avg=avg_arrival,
        service_avg=avg_service,
        num_students=num_students,
        num_windows=num_windows
    )
    
    # Error Handling
    if df is None:
        print("Bottleneck detected, unable to export stable chart.")
    else:
        print(f"Simulation stable (Utilization: {utilization:.1%}). Generating chart...")
        
        fig = generate_wait_time_chart(df)

        # Use absolute path for output to prevent CWD issues
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, 'ayoqueue_report.html')
        
        fig.write_html(output_filename, include_plotlyjs='cdn')
        print(f"Chart successfully exported to {output_filename}.")
