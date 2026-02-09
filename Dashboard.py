import streamlit as st
import random
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import seaborn as sns
st.set_page_config(
    layout="wide",
    page_title="Drone Logistics Analytics Suite",
    page_icon="🛸"
)
HUBS = {
    "Manhattan": (40.7549, -73.9840),
    "Brooklyn": (40.6500, -73.9500),
    "Queens": (40.7300, -73.8200),
    "Bronx": (40.8500, -73.8662),
    "Staten Island": (40.5795, -74.1502),
}
HUB_NAMES = list(HUBS.keys())
st.sidebar.title("Simulation Controls")
FAILURE_RATE = st.sidebar.slider("Base Failure Rate (%)", 0, 25, 9) / 100
BLOCKED_ROUTE_FAIL_PROB = st.sidebar.slider("Blocked Segment Fail Rate (%)", 0, 100, 20) / 100
BATTERY_FAIL_THRESHOLD = st.sidebar.slider("Battery Failure Threshold (%)", 50, 100, 90) / 100
NUM_DRONES = st.sidebar.slider("Number of Drones", 10, 200, 70)
NUM_DELIVERIES = st.sidebar.slider("Number of Deliveries", 50, 1500, 350)
PROGRESS_MODE = st.sidebar.radio("Simulation Mode", ["Instant", "Real-time Progress"])
MULTI_RUNS = st.sidebar.number_input("Multi-Run Simulation (for stats, set >1)", min_value=1, max_value=20, value=1, step=1)
HUB_FILTER = st.sidebar.multiselect("Filter by Hub", HUB_NAMES, default=HUB_NAMES)
SHOW_ADVANCED = st.sidebar.checkbox("Show Advanced Analytics", value=True)
def gen_drones(num):
    return {
        f"D{i}": {
            "id": f"D{i}",
            "hub": random.choice(HUB_NAMES),
            "battery": random.randint(60, 100),
            "payload_capacity_kg": round(random.uniform(1.0, 5.0), 2),
            "status": "idle",
            "deliveries_completed": 0
        }
        for i in range(1, num + 1)
    }
def gen_deliveries(num):
    deliveries = []
    for i in range(1, num + 1):
        hub = random.choice(HUB_NAMES)
        deliveries.append({
            "delivery_id": f"D{i:04}",
            "assigned_hub": hub,
            "payload_kg": round(random.uniform(0.5, 4.5), 2),
            "location": (
                HUBS[hub][0] + random.uniform(-0.02, 0.02),
                HUBS[hub][1] + random.uniform(-0.02, 0.02)
            )
        })
    return deliveries
def simulate_route_metadata(drone, delivery):
    blocked = random.random() < 0.1
    path = [] if blocked else [drone['id'], delivery['delivery_id']]
    energy_cost = random.uniform(5, 40)
    return {
        "path": path,
        "distance_m": random.uniform(500, 8000),
        "eta_min": random.uniform(5, 30),
        "energy_cost_percent": energy_cost,
        "detour": blocked
    }
def evaluate_delivery(drone, delivery, route, fail_rate, block_fail_prob, battery_thresh):
    if not route["path"]:
        if random.random() < block_fail_prob:
            return False, "no path available"
    if route["energy_cost_percent"] > drone["battery"] * battery_thresh:
        return False, "battery too low"
    if random.random() < fail_rate:
        return False, random.choice(["weather", "drone malfunction", "unknown error", "GPS loss", "bird strike"])
    return True, None
def update_drone_post_delivery(drone):
    drone["deliveries_completed"] += 1
    if drone["deliveries_completed"] % 10 == 0:
        drone["status"] = "maintenance"
    else:
        drone["status"] = "idle"
def resolve_maintenance(drones):
    for drone in drones.values():
        if drone["status"] == "maintenance":
            drone["status"] = "idle"
def log_delivery_result(drone_id, delivery, success, reason, log=[]):
    status = "delivered" if success else "failed"
    log.append({
        "drone_id": drone_id,
        "delivery_id": delivery["delivery_id"],
        "status": status,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        "delivery_lat": delivery["location"][0],
        "delivery_lon": delivery["location"][1],
        "assigned_hub": delivery["assigned_hub"],
        "payload_kg": delivery["payload_kg"]
    })
def run_simulation(deliveries, drones, fail_rate, block_fail_prob, battery_thresh, progress_mode="Instant"):
    log = []
    n = len(deliveries)
    if progress_mode == "Real-time Progress":
        progress = st.progress(0)
    for i, delivery in enumerate(deliveries):
        eligible = [
            d for d in drones.values()
            if d['hub'] == delivery['assigned_hub'] and
               d['battery'] > 50 and
               d['status'] == 'idle' and
               d['payload_capacity_kg'] >= delivery['payload_kg']
        ]
        if not eligible:
            log_delivery_result("N/A", delivery, False, "ineligible drone", log)
            continue
        drone = random.choice(eligible)
        route = simulate_route_metadata(drone, delivery)
        success, reason = evaluate_delivery(drone, delivery, route, fail_rate, block_fail_prob, battery_thresh)
        log_delivery_result(drone['id'], delivery, success, reason, log)
        if success:
            update_drone_post_delivery(drone)
        resolve_maintenance(drones)
        if progress_mode == "Real-time Progress":
            progress.progress((i+1)/n)
    return log
def filter_log_by_hub(log, selected_hubs):
    return [r for r in log if r["assigned_hub"] in selected_hubs]
def show_sim_params():
    st.markdown(f"""
    **Simulation Parameters**
    - Base Failure Rate: `{FAILURE_RATE*100:.1f}%`
    - Blocked Segment Fail Rate: `{BLOCKED_ROUTE_FAIL_PROB*100:.1f}%`
    - Battery Failure Threshold: `{BATTERY_FAIL_THRESHOLD*100:.1f}%`
    - Number of Drones: `{NUM_DRONES}`
    - Number of Deliveries: `{NUM_DELIVERIES}`
    - Filtered Hubs: `{', '.join(HUB_FILTER)}`
    """)
def summarize_simulation_results(log):
    total = len(log)
    delivered = sum(1 for r in log if r['status'] == 'delivered')
    failed = total - delivered
    rate = (delivered / total) * 100 if total else 0
    reasons = [r["reason"] for r in log if r["status"] == "failed"]
    top_reason = Counter(reasons).most_common(1)[0][0] if reasons else "None"
    st.subheader("📊 Simulation Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Deliveries", total)
    col2.metric("Delivered", delivered)
    col3.metric("Failed", failed)
    col4.metric("Success Rate", f"{rate:.2f}%")
    st.write(f"**Most Common Failure:** {top_reason}")
    return delivered, failed
def plot_delivery_outcome_pie(log):
    statuses = [r["status"] for r in log]
    counter = Counter(statuses)
    labels = counter.keys()
    sizes = counter.values()
    colors = ['lightgreen' if label == 'delivered' else 'salmon' for label in labels]
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors
    )
    ax.set_title("Mission Success vs. Failure", fontsize=14)
    st.pyplot(fig)
    plt.close(fig)
def plot_failure_reasons(log):
    fail_log = [r for r in log if r["status"] == "failed"]
    if not fail_log:
        st.info("No failures to show. Congratulations on your luck-based QA process.")
        return
    reason_counts = Counter([r["reason"] for r in fail_log])
    reasons, counts = zip(*reason_counts.items())
    fig, ax = plt.subplots(figsize=(5, 2.5))
    ax.bar(reasons, counts, color='tomato')
    ax.set_title("Breakdown of Failure Reasons")
    ax.set_ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)
    plt.close(fig)
def plot_deliveries_by_hub(log):
    df = pd.DataFrame(log)
    summary = df.groupby(['assigned_hub', 'status']).size().unstack(fill_value=0)
    for col in ['delivered', 'failed']:
        if col not in summary.columns:
            summary[col] = 0
    fig, ax = plt.subplots(figsize=(7, 3))
    summary[['delivered', 'failed']].plot(
        kind="bar", stacked=True, ax=ax, color=['lightgreen', 'salmon']
    )
    ax.set_title("Deliveries by Hub and Status")
    ax.set_ylabel("Count")
    st.pyplot(fig)
    plt.close(fig)
def plot_delivery_map(log):
    points = log if len(log) <= 200 else random.sample(log, 200)
    m = folium.Map(location=[40.75, -73.98], zoom_start=12, control_scale=True)
    for name, loc in HUBS.items():
        folium.Marker(
            location=loc, popup=f"{name} Hub",
            icon=folium.Icon(color='blue', icon='home', prefix='fa')
        ).add_to(m)
    for r in points:
        color = "green" if r["status"] == "delivered" else "red"
        folium.CircleMarker(
            location=(r["delivery_lat"], r["delivery_lon"]),
            radius=4,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"{r['delivery_id']} ({r['assigned_hub']}): {r['status']} ({r['reason']})"
        ).add_to(m)
    st_folium(m, width=720, height=430)
def plot_delivery_heatmap(log):
    points = [(r["delivery_lat"], r["delivery_lon"]) for r in log if r["status"] == "delivered"]
    m = folium.Map(location=[40.75, -73.98], zoom_start=12)
    if len(points) > 0:
        HeatMap(points, radius=11, blur=14, min_opacity=0.32).add_to(m)
    else:
        folium.Marker([40.75, -73.98], tooltip="No deliveries").add_to(m)
    st_folium(m, width=720, height=430)
def plot_payload_distribution(log):
    df = pd.DataFrame(log)
    fig, ax = plt.subplots(figsize=(5, 2.5))
    sns.histplot(df["payload_kg"], kde=True, color="orange", ax=ax, bins=15)
    ax.set_title("Distribution of Delivery Payload Weights (kg)")
    st.pyplot(fig)
    plt.close(fig)
def plot_deliveries_over_time(log):
    df = pd.DataFrame(log)
    df['dt'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['dt'].dt.hour
    fig, ax = plt.subplots(figsize=(5.5, 2.5))
    df.groupby('hour').size().plot(kind='bar', color='slateblue', ax=ax)
    ax.set_title("Deliveries per Hour")
    ax.set_xlabel("Hour of Day")
    st.pyplot(fig)
    plt.close(fig)
def show_drone_utilization(drones):
    drone_df = pd.DataFrame([
        {
            "ID": d["id"],
            "Hub": d["hub"],
            "Deliveries Completed": d["deliveries_completed"],
            "Final Battery": d["battery"],
            "Status": d["status"]
        }
        for d in drones.values()
    ])
    st.dataframe(drone_df.sort_values("Deliveries Completed", ascending=False), use_container_width=True)
def show_log_table(log):
    log_df = pd.DataFrame(log)
    if len(log_df) > 500:
        st.write("Showing first 500 deliveries only (download for full data).")
        log_df = log_df.head(500)
    st.dataframe(log_df)
def show_download(log):
    log_df = pd.DataFrame(log)
    st.download_button(
        label="Download Delivery Log as CSV",
        data=log_df.to_csv(index=False),
        file_name="drone_delivery_log.csv",
        mime="text/csv",
    )
def multi_run_stats(num_runs, deliveries, drones, fail_rate, block_fail_prob, battery_thresh):
    rates = []
    for i in range(num_runs):
        drones_copy = gen_drones(len(drones))
        log = run_simulation(deliveries, drones_copy, fail_rate, block_fail_prob, battery_thresh)
        delivered = sum(1 for r in log if r['status'] == 'delivered')
        rate = (delivered / len(deliveries)) * 100
        rates.append(rate)
    fig, ax = plt.subplots()
    ax.hist(rates, bins=10, color="skyblue", edgecolor="black")
    ax.set_title("Success Rate Distribution Over Runs")
    ax.set_xlabel("Success Rate (%)")
    ax.set_ylabel("Number of Runs")
    st.pyplot(fig)
    plt.close(fig)
    st.write(f"Average Success Rate: {sum(rates)/len(rates):.2f}%")
st.title("🛸 NYDroneAI: Full Enterprise Drone Analytics Suite")
if st.button("Run Simulation"):
    show_sim_params()
    drones = gen_drones(NUM_DRONES)
    deliveries = gen_deliveries(NUM_DELIVERIES)
    if MULTI_RUNS > 1:
        st.subheader("📈 Multi-Run Simulation Stats")
        multi_run_stats(
            MULTI_RUNS, deliveries, drones, FAILURE_RATE, BLOCKED_ROUTE_FAIL_PROB, BATTERY_FAIL_THRESHOLD
        )
    else:
        result_log = run_simulation(
            deliveries, drones, FAILURE_RATE, BLOCKED_ROUTE_FAIL_PROB, BATTERY_FAIL_THRESHOLD, PROGRESS_MODE
        )
        result_log = filter_log_by_hub(result_log, HUB_FILTER)
        delivered, failed = summarize_simulation_results(result_log)
        plot_delivery_outcome_pie(result_log)
        plot_failure_reasons(result_log)
        plot_deliveries_by_hub(result_log)
        with st.expander("🗺️ Show Map of Deliveries"):
            plot_delivery_map(result_log)
        with st.expander("🔥 Show Delivery Heatmap"):
            plot_delivery_heatmap(result_log)
        with st.expander("⚖️ Show Payload Weight Distribution"):
            plot_payload_distribution(result_log)
        with st.expander("⏰ Deliveries Per Hour"):
            plot_deliveries_over_time(result_log)
        with st.expander("📋 Drone Utilization Table"):
            show_drone_utilization(drones)
        with st.expander("🗒️ Full Delivery Log / Download"):
            show_log_table(result_log)
            show_download(result_log)
        if SHOW_ADVANCED:
            st.markdown("**Advanced: Under-the-hood summary:**")
            st.write(pd.DataFrame(result_log).groupby(["assigned_hub","status"]).size().unstack(fill_value=0))
else:
    st.info("Set parameters in the sidebar and click **Run Simulation**.")
st.markdown("---")
st.markdown(
    "<center><sub><i>NYDroneAI Analytics Suite &copy; 2025<br>For demo use only. Not for actual drone deployment.<br>Dashboard so comprehensive, you’ll forget it’s just a simulation.</i></sub></center>",
    unsafe_allow_html=True,
)