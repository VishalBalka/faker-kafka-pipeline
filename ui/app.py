import streamlit as st
import pandas as pd
import psycopg2
import time
import os

# Set page configuration
st.set_page_config(
    page_title="Real-Time Data Pipeline Monitor",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-value {
        font-size: 3rem !important;
        font-weight: 700;
        color: #1E88E5;
    }
    .status-active {
        color: #4CAF50;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🚀 Real-Time Pipeline Dashboard")
st.markdown("Watching the live data flow from **Kafka** ➡️ **PySpark** ➡️ **PostgreSQL**")
st.markdown("---")

# PostgreSQL Connection settings
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5433") # Localport exposed to docker
DB_NAME = os.environ.get("DB_NAME", "pipelinedb")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASS = os.environ.get("DB_PASS", "password")

@st.cache_resource
def get_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
    except Exception as e:
        st.error(f"Failed to connect to PostgreSQL: {e}")
        return None

# Fetch data function
def fetch_data(conn):
    if not conn:
        return pd.DataFrame(), 0
        
    try:
        # Get total count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions;")
        total_count = cursor.fetchone()[0]
        
        # Get latest 100 transactions
        query = "SELECT * FROM transactions ORDER BY transaction_timestamp DESC LIMIT 100;"
        df = pd.read_sql_query(query, conn)
        return df, total_count
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(), 0

# Dashboard layout
st.markdown("### 📊 Live Operations Center")

# Initialize session state for tracking rate
if 'last_count' not in st.session_state:
    st.session_state.last_count = 0
if 'last_time' not in st.session_state:
    st.session_state.last_time = time.time()

# Main update loop
conn = get_connection()

if conn:
    st.sidebar.markdown(f"### Connection Status: <span class='status-active'>Connected</span>", unsafe_allow_html=True)
    st.sidebar.markdown(f"**Host**: {DB_HOST}:{DB_PORT}")
    st.sidebar.markdown(f"**Database**: {DB_NAME}")
    st.sidebar.markdown("---")
    
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh Live Stream", value=True)
    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)
    
    if st.button("Manual Refresh"):
        pass # Streamlit natively reruns on button click
        
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()
    data_placeholder = st.empty()
        
    while auto_refresh:
        df, current_count = fetch_data(conn)
        
        # Calculate messages per second
        current_time = time.time()
        time_diff = current_time - st.session_state.last_time
        count_diff = current_count - st.session_state.last_count
        
        rate = 0
        if time_diff > 0 and count_diff >= 0:
            rate = count_diff / time_diff
            
        with metrics_placeholder.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Transactions Stored", value=f"{current_count:,}", delta=f"+{count_diff} new records")
            with col2:
                st.metric(label="Ingestion Rate", value=f"{rate:.1f} msg/sec", delta=f"{rate:.1f} avg", delta_color="off")
            with col3:
                st.metric(label="System Status", value="Streaming Live ✨", delta="Active Connection", delta_color="normal")
            
        st.write("---")
            
        col_chart, col_data = st.columns([1, 1])
        
        with col_chart:
            with chart_placeholder.container():
                if not df.empty:
                    st.subheader("📈 Recent Transaction Amounts")
                    st.area_chart(df.set_index('transaction_timestamp')['amount'], color="#00C4B4")
                    
        with col_data:
            with data_placeholder.container():
                if not df.empty:
                    st.subheader("📋 Raw Live Feed (Latest)")
                    # Style the dataframe
                    st.dataframe(
                        df.style.highlight_max(axis=0, subset=['amount'], color='#ff4b4b')
                               .format({'amount': '${:.2f}'}),
                        use_container_width=True,
                        height=350
                    )
                
        # Update state safely at the very end
        if time_diff > 5:
            st.session_state.last_count = current_count
            st.session_state.last_time = current_time
        else:
            st.session_state.last_count = current_count
            st.session_state.last_time = current_time
            
        time.sleep(refresh_rate)
        st.rerun()
else:
    st.warning("⚠️ Waiting for Database Connection...")
    if st.button("Retry Connection"):
        st.rerun()
