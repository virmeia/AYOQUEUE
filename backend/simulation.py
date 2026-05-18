import numpy as np
import pandas as pd

def run_parallel_mm1_sim(arrival_avg, service_avg, num_students, num_windows, num_runs=1000):
    # Rates
    total_arrival_rate  = 1.0 / arrival_avg
    window_arrival_rate = total_arrival_rate / num_windows
    service_rate        = 1.0 / service_avg
    utilization         = window_arrival_rate / service_rate

    # Stability Check
    if utilization >= 1.0:
        return None, utilization, None

    # Steady-State Analytical Metrics (M/M/1 per window)
    lq = (window_arrival_rate ** 2) / (service_rate * (service_rate - window_arrival_rate))
    l  = window_arrival_rate / (service_rate - window_arrival_rate)
    wq = window_arrival_rate / (service_rate * (service_rate - window_arrival_rate))
    w  = 1.0 / (service_rate - window_arrival_rate)

    steady_state = {
        'Lq': round(lq, 4),  # Avg. students waiting in queue
        'L':  round(l,  4),  # Avg. students in system
        'Wq': round(wq, 4),  # Avg. wait time in queue (mins)
        'W':  round(w,  4),  # Avg. time in system (mins)
    }

    # Monte Carlo Loop
    window_arrival_avg = 1.0 / window_arrival_rate
    all_wait_runs = []

    for _ in range(num_runs):
        inter_arrival_times = np.random.exponential(window_arrival_avg, num_students)
        service_times       = np.random.exponential(service_avg,        num_students)
        arrival_times       = np.cumsum(inter_arrival_times)

        start_times  = np.zeros(num_students)
        finish_times = np.zeros(num_students)
        wait_times   = np.zeros(num_students)

        for i in range(num_students):
            if i == 0:
                start_times[i] = arrival_times[i]
            else:
                start_times[i] = max(arrival_times[i], finish_times[i - 1])

            wait_times[i]   = start_times[i] - arrival_times[i]
            finish_times[i] = start_times[i] + service_times[i]

        all_wait_runs.append(wait_times)

    # Average wait time per student position across all runs
    avg_wait_per_student = np.mean(all_wait_runs, axis=0)

    df = pd.DataFrame({
        'Student Number':   np.arange(1, num_students + 1),
        'Wait Time (Mins)': avg_wait_per_student,
    })

    return df, utilization, steady_state