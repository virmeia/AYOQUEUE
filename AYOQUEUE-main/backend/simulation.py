import numpy as np
import pandas as pd

def run_parallel_mm1_sim(arrival_avg, service_avg, num_students, num_windows):
    # Calculate arrival rate per window and utilization
    total_arrival_rate = 1.0 / arrival_avg
    window_arrival_rate = total_arrival_rate / num_windows
    service_rate = 1.0 / service_avg
    
    utilization = window_arrival_rate / service_rate
    
    # Return None if system is unstable (infinite line failure)
    if utilization >= 1.0:
        return None, utilization
        
    # Monte Carlo simulation for a single independent line
    window_arrival_avg = 1.0 / window_arrival_rate
    inter_arrival_times = np.random.exponential(window_arrival_avg, num_students)
    service_times = np.random.exponential(service_avg, num_students)
    
    arrival_times = np.cumsum(inter_arrival_times)
    start_times = np.zeros(num_students)
    finish_times = np.zeros(num_students)
    wait_times = np.zeros(num_students)
    
    for i in range(num_students):
        if i == 0:
            start_times[i] = arrival_times[i]
        else:
            start_times[i] = max(arrival_times[i], finish_times[i-1])
            
        wait_times[i] = start_times[i] - arrival_times[i]
        finish_times[i] = start_times[i] + service_times[i]
        
    return pd.DataFrame({
        'Student Number': np.arange(1, num_students + 1),
        'InterArrivalTime': inter_arrival_times,
        'ArrivalTime': arrival_times,
        'ServiceTime': service_times,
        'StartTime': start_times,
        'Wait Time (Mins)': wait_times,
        'FinishTime': finish_times
    }), utilization
