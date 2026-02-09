

# 🛸 Drone Logistics Simulation & Analytics Dashboard

This is an AI-driven, interactive simulation and analytics platform for drone delivery operations in New York City. Built with **Python** and **Streamlit**, it enables realistic drone route simulations, mission analytics, and performance optimization insights.


## 🌟 Key Features

### Drone Delivery Simulation

* AI-powered delivery assignment using **Flan-T5 (Hugging Face Transformers)**.
* Realistic route planning with **battery constraints** and **blocked paths**.
* Simulation of **drone failures** and **maintenance schedules**.

### Interactive Visual Analytics

* Mission success/failure statistics.
* Detailed delivery outcome breakdown, including failure reasons.
* Geospatial visualization of deliveries with **heatmaps and Folium maps**.
* Drone utilization metrics and payload analysis.
* Real-time analytics dashboard powered by **Streamlit**.

### Multi-Run Statistical Analysis

* Run multiple simulations for comprehensive performance insights.
* Identify bottlenecks and optimize drone operations.

---

## 🚀 Technology Stack

| Component              | Technologies & Libraries                       |
| ---------------------- | ---------------------------------------------- |
| Programming Language   | Python                                         |
| Web Framework          | Streamlit                                      |
| Data Manipulation      | Pandas, NumPy                                  |
| Visualization          | Matplotlib, Seaborn, Folium                    |
| Geospatial & Mapping   | Geopy, GeoPandas, Shapely                      |
| Route Planning         | NetworkX (Dijkstra, A*)                        |
| Database               | SQLite                                         |
| Machine Learning & NLP | Hugging Face Transformers (Flan-T5), LangChain |

---

## ⚙️ Installation & Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-username/NYDroneAI-Streamlit-Dashboard.git
cd NYDroneAI-Streamlit-Dashboard
```

2. **Create and activate a virtual environment (recommended)**

```bash
python -m venv env
# Linux / MacOS
source env/bin/activate
# Windows
.\env\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

> Ensure all dependencies are included in `requirements.txt`.

---

## 🖥️ Running the Dashboard

Start the Streamlit app locally:

```bash
streamlit run Dashboard.py
```

Open your browser at [http://localhost:8501](http://localhost:8501).

---

## 🌐 Deployment

Deploy easily to **Streamlit Community Cloud**:

1. Push your repository to GitHub.
2. Connect your repository on Streamlit Cloud.
3. Deploy your dashboard with a few clicks.

---

## 🗂 Project Structure

```
.
├── Dashboard.py            # Main Streamlit dashboard script
├── requirements.txt        # Python dependencies
├── nydroneai.db            # SQLite database (runtime-generated)
├── data/                   # Simulation data and logs
└── README.md               # Project documentation
```

---


## 🚨 Disclaimer

This is a simulated drone logistics dashboard intended for **educational and demonstration purposes only**. It is **not designed for real-world drone operations**.


