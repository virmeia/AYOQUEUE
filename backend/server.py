from flask import Flask, render_template, request, redirect, jsonify
from simulation import run_parallel_mm1_sim
from charts import generate_wait_time_chart
import os, webbrowser

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form.get('staff_id')
        password   = request.form.get('password')

        users = {
            'REG-2025-001': {'password': 'registrar123', 'name': 'Anna Reyes', 'role': 'Head Registrar'},
            'REG-2025-002': {'password': 'registrar123', 'name': 'Carlos Santos', 'role': 'Registrar Staff'},
        }

        user = users.get(student_id)
        if user and user['password'] == password:
            # ✅ Successful login
            return redirect('/dashboard')
        else:
            # ❌ Failed login
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    results = None

    if request.method == 'POST':
        avg_arrival  = float(request.form['avg_arrival'])
        avg_service  = float(request.form['avg_service'])
        num_windows  = int(request.form['num_windows'])
        num_students = int(request.form['num_students'])

        df, utilization, steady_state = run_parallel_mm1_sim(
            avg_arrival, avg_service, num_students, num_windows
        )

        if df is not None:
            fig = generate_wait_time_chart(df)
            chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

            results = {
                'utilization': round(utilization * 100, 1),
                'avg_wait':    round(df['Wait Time (Mins)'].mean(), 2),
                'max_wait':    round(df['Wait Time (Mins)'].max(), 2),
                'pct_over_10': round((df['Wait Time (Mins)'] > 10).mean() * 100, 1),
                'chart':       chart_html,
                'lq': steady_state['Lq'],
                'l':  steady_state['L'],
                'wq': steady_state['Wq'],
                'w':  steady_state['W'],
            }
        else:
            results = {'unstable': True, 'utilization': round(utilization * 100, 1)}

    return render_template('dashboard.html', results=results)

@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        webbrowser.open('http://127.0.0.1:5000')
        
    app.run(debug=True)
