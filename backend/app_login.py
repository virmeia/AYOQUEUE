from flask import Flask, request, jsonify, session
from flask_cors import CORS
import numpy as np
import pandas as pd
import os, json

app = Flask(__name__)
app.secret_key = 'ayoqueue_secret_2025'
CORS(app, supports_credentials=True, origins=['null', 'http://localhost:*', 'http://127.0.0.1:*', 'file://'])

# ── In-memory user store (replace with DB in production) ──────────────────────
USERS = {
    "2021-00001": {"password": "student123", "name": "Juan dela Cruz",    "course": "BSIT",  "year": 3},
    "2021-00002": {"password": "student123", "name": "Maria Santos",      "course": "BSECE", "year": 2},
    "2022-00003": {"password": "student123", "name": "Jose Reyes",        "course": "BSME",  "year": 1},
    "admin":      {"password": "admin2025",  "name": "Admin User",        "course": "Staff", "year": 0},
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def exp_random(mean, n):
    return np.random.exponential(mean, n)

def run_simulation(arrival_avg, service_avg, num_students, num_windows):
    total_rate   = 1.0 / arrival_avg
    window_rate  = total_rate / num_windows
    service_rate = 1.0 / service_avg
    utilization  = window_rate / service_rate

    if utilization >= 1.0:
        return None, float(utilization)

    window_arrival_avg = 1.0 / window_rate
    inter_arrivals = exp_random(window_arrival_avg, num_students)
    service_times  = exp_random(service_avg, num_students)
    arrival_times  = np.cumsum(inter_arrivals)

    start_times  = np.zeros(num_students)
    wait_times   = np.zeros(num_students)
    finish_times = np.zeros(num_students)

    for i in range(num_students):
        start_times[i]  = arrival_times[i] if i == 0 else max(arrival_times[i], finish_times[i-1])
        wait_times[i]   = start_times[i] - arrival_times[i]
        finish_times[i] = start_times[i] + service_times[i]

    rows = [{"student": int(i+1),
             "interArrival": round(float(inter_arrivals[i]), 4),
             "arrival":      round(float(arrival_times[i]), 4),
             "service":      round(float(service_times[i]), 4),
             "start":        round(float(start_times[i]),  4),
             "wait":         round(float(wait_times[i]),   4),
             "finish":       round(float(finish_times[i]), 4)}
            for i in range(num_students)]

    return rows, float(utilization)

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    sid      = data.get('student_id', '').strip()
    password = data.get('password', '').strip()

    user = USERS.get(sid)
    if not user or user['password'] != password:
        return jsonify({'success': False, 'message': 'Invalid student ID or password.'}), 401

    session['user'] = sid
    return jsonify({
        'success': True,
        'name':    user['name'],
        'course':  user['course'],
        'year':    user['year'],
        'id':      sid,
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/me', methods=['GET'])
def me():
    sid = session.get('user')
    if not sid or sid not in USERS:
        return jsonify({'logged_in': False}), 401
    u = USERS[sid]
    return jsonify({'logged_in': True, 'name': u['name'], 'course': u['course'], 'year': u['year'], 'id': sid})

@app.route('/api/simulate', methods=['POST'])
def simulate():
    if not session.get('user'):
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    try:
        arrival_avg  = float(data['arrival_avg'])
        service_avg  = float(data['service_avg'])
        num_students = int(data['num_students'])
        num_windows  = int(data['num_windows'])
    except (KeyError, ValueError, TypeError):
        return jsonify({'error': 'Invalid parameters'}), 400

    rows, utilization = run_simulation(arrival_avg, service_avg, num_students, num_windows)

    if rows is None:
        return jsonify({'stable': False, 'utilization': utilization})

    waits   = [r['wait'] for r in rows]
    avg_wait = round(sum(waits) / len(waits), 4)
    max_wait = round(max(waits), 4)
    pct_over = round(sum(1 for w in waits if w > 10) / len(waits) * 100, 2)

    return jsonify({
        'stable':      True,
        'utilization': round(utilization, 4),
        'avg_wait':    avg_wait,
        'max_wait':    max_wait,
        'pct_over_10': pct_over,
        'data':        rows,
    })

if __name__ == '__main__':
    print("\n  AyoQueue API running → http://localhost:5000\n")
    app.run(debug=True, port=5000)
