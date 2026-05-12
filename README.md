# AYOQUEUE

AyoQueue is a decision-support dashboard for a university registrar. It uses a Monte Carlo simulation of an M/M/1 queuing system to model student wait times and server utilization based on arrival and service rates.

## Technologies
- Python
- Streamlit
- Plotly
- Pandas
- NumPy

## Project Structure
The application logic is located in the `backend/` folder:
- `app.py`: Streamlit frontend dashboard.
- `simulation.py`: Monte Carlo M/M/1 mathematical simulation.
- `charts.py`: Data visualization module.
- `export.py`: Script to export simulation results to an interactive HTML file.

## Usage

**Run the Streamlit Dashboard:**
```bash
cd backend
streamlit run app.py
```

**Generate an HTML Report:**
```bash
cd backend
python export.py
```
