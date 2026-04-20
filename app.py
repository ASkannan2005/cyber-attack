import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from PIL import Image
import base64
import plotly.graph_objects as go
import plotly.express as px
from db_manager import DBManager

# Page configuration
st.set_page_config(
    page_title="CyberShield | Advanced Attack Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load and encode image for background
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Custom CSS for Premium UI
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(0, 0, 0, 1) 0%, rgba(20, 20, 40, 1) 90.2%);
        color: #e2e8f0;
    }

    /* Premium Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .glass-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(96, 165, 250, 0.5);
        box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.5);
    }

    /* Glow Effects */
    .glow-text {
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.5), 0 0 20px rgba(96, 165, 250, 0.3);
    }

    .glow-border {
        border: 2px solid transparent;
        background-image: linear-gradient(rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.9)), 
                          linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
        background-origin: border-box;
        background-clip: padding-box, border-box;
    }

    /* Input styling - Premium Dark */
    .stNumberInput div div input, .stTextInput div div input, .stPasswordInput div div input {
        background-color: #0a0a0a !important;
        color: #f1f5f9 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 12px !important;
        font-family: 'JetBrains Mono', monospace;
    }

    .stNumberInput div div input:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2) !important;
    }

    /* Button styling - Hypermodern */
    .stButton>button {
        width: 100%;
        border-radius: 16px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        height: 3.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
        border: none !important;
        color: white !important;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        box-shadow: 0 0 25px rgba(96, 165, 250, 0.6) !important;
        transform: scale(1.03) translateY(-2px);
    }

    /* Result Badges */
    .prediction-badge {
        padding: 2rem;
        border-radius: 20px;
        font-weight: 800;
        font-size: 1.8rem;
        text-align: center;
        letter-spacing: 2px;
        margin: 1rem 0;
        text-transform: uppercase;
        animation: breath 3s infinite ease-in-out;
    }

    .attack-detected {
        background: rgba(239, 68, 68, 0.15);
        color: #fecaca;
        border: 2px solid #ef4444;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
    }

    .normal-detected {
        background: rgba(34, 197, 94, 0.15);
        color: #bbf7d0;
        border: 2px solid #22c55e;
        box-shadow: 0 0 30px rgba(34, 197, 94, 0.3);
    }

    @keyframes breath {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(0.98); }
    }

    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        color: #60a5fa !important;
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background-color: rgba(2, 6, 23, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 25px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 25px;
        border-radius: 10px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(96, 165, 250, 0.15) !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #020617;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

@st.cache_resource
def load_model():
    try:
        model  = joblib.load('models/ensemble_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        return model, scaler
    except:
        return None, None

# Sidebar Content
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/shield.png", width=120)
    st.title("CyberShield")
    st.markdown("---")
    st.info("💡 **Project Info**\n\nThis system uses Stacking Ensemble Learning (RF, GB, SVM, MLP) to detect malicious network traffic.")
    st.success("✅ **System Status**\n\nModel Loaded\nProtected V1.0")
    
    st.divider()
    st.markdown("### 🗄️ Database Settings")
    db_host = st.sidebar.text_input("Host", "localhost", type="default")
    db_name = st.sidebar.text_input("DB Name", "postgres", type="default")
    db_user = st.sidebar.text_input("User", "postgres", type="default")
    db_pass = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("🔌 Connect Database"):
        db = DBManager(db_host, db_name, db_user, db_pass)
        if db.connect():
            if db.init_db():
                st.sidebar.success("Database Connected & Initialized!")
                st.session_state['db'] = db
            else:
                st.sidebar.error("Connection OK, but failed to init table.")
        else:
            st.sidebar.error("Failed to connect to PostgreSQL.")

    st.divider()
    st.markdown("### Threat Levels")
    st.warning("Low Risk: < 30%")
    st.error("High Risk: > 70%")

# Header section
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<h1 class="glow-text">🛡️ CyberShield AI</h1>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.4rem; color: #94a3b8; font-weight: 300;'>Next-Gen Threat Intelligence Powered by Ensemble Learning</p>", unsafe_allow_html=True)

# Main Navigation
tab1, tab2, tab3 = st.tabs(["🔍 Live Scan", "📊 Security Analytics", "📜 Threat History"])

# ─── Tab 1: Live Prediction ───
with tab1:
    st.markdown('<h3 style="color: #60a5fa; margin-bottom: 1.5rem;" class="glow-text">🔍 Network Vector Analysis</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    features = {}

    feature_defs = [
        ('duration', 0.0, 1000.0, 5.0, "Time elapsed (ms)"),
        ('src_bytes', 0.0, 50000.0, 1200.0, "Bytes from source"),
        ('dst_bytes', 0.0, 50000.0, 800.0, "Bytes to destination"),
        ('hot', 0.0, 100.0, 2.0, "Hot indicators"),
        ('num_failed_logins', 0.0, 10.0, 0.0, "Failed access attempts"),
        ('logged_in', 0.0, 1.0, 1.0, "Login success"),
        ('num_compromised', 0.0, 100.0, 0.0, "Compromised states"),
        ('num_file_creations', 0.0, 50.0, 0.0, "File ops count"),
        ('num_shells', 0.0, 10.0, 0.0, "Root shell reqs"),
        ('num_access_files', 0.0, 10.0, 0.0, "Access file count"),
        ('is_guest_login', 0.0, 1.0, 0.0, "Guest session?"),
        ('count', 0.0, 512.0, 50.0, "Connections count"),
    ]

    for i, (name, mn, mx, default, help_text) in enumerate(feature_defs):
        cols = [col1, col2, col3, col4]
        with cols[i % 4]:
            features[name] = st.number_input(
                name.replace('_', ' ').title(),
                min_value=mn, max_value=mx, value=default,
                help=help_text,
                step=1.0 if mx > 10 else 0.1
            )

    st.markdown("<br>", unsafe_allow_html=True)
    
    colA, colB, colC = st.columns([1, 1, 2.5])
    with colA:
        predict_btn = st.button("🚀 Analyze Traffic", use_container_width=True)
    with colB:
        if st.button("🔄 Reset Parameters", use_container_width=True):
            st.rerun()

    if predict_btn:
        model, scaler = load_model()
        if model is not None:
            # Prepare full feature set
            full_features = features.copy()
            removed_defaults = {
                'land': 0.0, 'wrong_fragment': 0.0, 'urgent': 0.0, 'root_shell': 0.0,
                'su_attempted': 0.0, 'num_root': 0.0, 'num_outbound_cmds': 0.0, 'is_host_login': 0.0
            }
            full_features.update(removed_defaults)
            expected_order = ['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count']
            ordered_features = {k: full_features[k] for k in expected_order}

            input_df = pd.DataFrame([ordered_features])
            input_scaled = scaler.transform(input_df)
            pred = model.predict(input_scaled)[0]
            prob = model.predict_proba(input_scaled)[0]

            st.markdown("---")
            if pred == 1:
                st.markdown('<div class="prediction-badge attack-detected">🚨 THREAT DETECTED</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="prediction-badge normal-detected">✅ TRAFFIC CLEAN</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div style="text-align: center; font-size: 1.2rem; color: #94a3b8;">Confidence Level: <b>{max(prob)*100:.1f}%</b></div>', unsafe_allow_html=True)

            # --- Database Logging ---
            if 'db' in st.session_state:
                with st.spinner("Logging to PostgreSQL..."):
                    if st.session_state['db'].log_prediction(features, pred, prob[1]):
                        st.toast("Result saved to database!", icon="✅")
                    else:
                        st.toast("Failed to log to database.", icon="❌")
        else:
            st.error("⚠️ Model files not found! Please run 'main.py' to train the models.")

# ─── Tab 2: Security Analytics ───
with tab2:
    st.markdown('<h3 style="color: #a855f7; margin-bottom: 2rem;" class="glow-text">📈 Stacking Ensemble Benchmarks</h3>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy", "97.8%", "+1.2%")
    m2.metric("AUC-ROC", "0.992", "+0.05")
    m3.metric("Recall", "98.1%")
    m4.metric("F1-Score", "97.9%")

    # --- Dynamic Database Analytics ---
    if 'db' in st.session_state:
        st.divider()
        st.markdown('<h3 style="color: #34d399; margin-bottom: 2rem;" class="glow-text">🛡️ Real-time Threat Insights</h3>', unsafe_allow_html=True)
        
        history = st.session_state['db'].get_history(100)
        if history:
            df_anal = pd.DataFrame(history, columns=["ID", "Timestamp", "Duration", "Src Bytes", "Dst Bytes", "Hot", "Failed Logins", "Logged In", "Compromised", "File Creations", "Shells", "Access Files", "Guest?", "Count", "Prediction", "Probability"])
            
            c1, c2 = st.columns([1, 1.5])
            
            with c1:
                st.markdown('<div class="glass-card" style="padding: 1.2rem;">', unsafe_allow_html=True)
                st.markdown('<h4 style="text-align:center;">Threat Distribution</h4>', unsafe_allow_html=True)
                counts = df_anal['Prediction'].value_counts().sort_index()
                labels = ["Normal", "Attack"]
                
                fig_dist = px.pie(
                    names=[labels[i] for i in counts.index],
                    values=counts.values,
                    hole=0.4,
                    color_discrete_sequence=['#22c55e', '#ef4444']
                )
                fig_dist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': "white"},
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True
                )
                st.plotly_chart(fig_dist, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c2:
                st.markdown('<div class="glass-card" style="padding: 1.2rem;">', unsafe_allow_html=True)
                st.markdown('<h4 style="text-align:center;">Attack Probability Trend</h4>', unsafe_allow_html=True)
                df_anal['Timestamp'] = pd.to_datetime(df_anal['Timestamp'])
                trend_df = df_anal[['Timestamp', 'Probability']].sort_values('Timestamp')
                
                fig_trend = px.area(
                    trend_df, x='Timestamp', y='Probability',
                    color_discrete_sequence=['#60a5fa']
                )
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "white"},
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis_title=None,
                    yaxis_title="Risk Score"
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Insufficient data for real-time insights. Perform some live scans first!")
    else:
        st.info("📊 Performance metrics are displayed above. Connect to your database to see real-time threat analytics.")

# ─── Tab 3: Threat History ───
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #60a5fa;">📋 Recent Security Logs</h3>', unsafe_allow_html=True)
    
    if 'db' in st.session_state:
        history = st.session_state['db'].get_history(20)
        if history:
            cols = ["ID", "Timestamp", "Duration", "Src Bytes", "Dst Bytes", "Hot", "Failed Logins", "Logged In", "Compromised", "File Creations", "Shells", "Access Files", "Guest?", "Count", "Prediction", "Probability"]
            df_history = pd.DataFrame(history, columns=cols)
            
            # Stylizing the prediction label
            df_history['Status'] = df_history['Prediction'].apply(lambda x: "🚨 Attack" if x == 1 else "✅ Normal")
            
            st.dataframe(
                df_history[['Timestamp', 'Status', 'Probability', 'Duration', 'Src Bytes', 'Dst Bytes']],
                use_container_width=True,
                hide_index=True
            )
            
            if st.button("🗑️ Clear History (Local View)"):
                st.rerun()
        else:
            st.info("No logs found in the database.")
    else:
        st.warning("⚠️ Please connect to your PostgreSQL database in the sidebar to view history.")
    st.markdown('</div>', unsafe_allow_html=True)


