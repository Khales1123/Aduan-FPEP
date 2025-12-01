import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="FPEP Voice Wall", page_icon="📢", layout="centered")

# Initialize Session State to track votes (This runs once per user visit)
if "voted_posts" not in st.session_state:
    st.session_state.voted_posts = set()

# Custom CSS
st.markdown("""
    <style>
    :root { --primary-maroon: #800000; --light-maroon: #a31515; }
    h1 { color: var(--primary-maroon) !important; }
    
    /* Post Card Styling */
    .post-card-header {
        background-color: white;
        padding: 20px 20px 5px 20px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        border-left: 5px solid var(--primary-maroon);
        border-top: 1px solid #eee;
        border-right: 1px solid #eee;
    }
    .post-card-body {
        background-color: white;
        padding: 5px 20px 20px 20px;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        border-left: 5px solid var(--primary-maroon);
        border-bottom: 1px solid #eee;
        border-right: 1px solid #eee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .meta-text { font-size: 14px; color: #666; display: flex; justify-content: space-between; }
    .main-text { font-size: 16px; color: #333; margin-top: 10px; white-space: pre-wrap; }
    
    /* Status Badges */
    .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;}
    .status-New { background-color: #fff3cd; color: #856404; }
    .status-Reviewed { background-color: #d4edda; color: #155724; }
    .status-Solved { background-color: #cce5ff; color: #004085; }
    
    /* Customizing the Upvote Button */
    /* Normal State */
    .stButton button {
        background-color: white !important;
        color: var(--primary-maroon) !important;
        border: 1px solid var(--primary-maroon) !important;
        border-radius: 50px !important;
        font-size: 14px !important;
        padding: 4px 15px !important;
    }
    .stButton button:hover {
        background-color: #fcebeb !important;
    }
    /* Disabled State (Already Voted) */
    .stButton button:disabled {
        background-color: #eee !important;
        color: #888 !important;
        border: 1px solid #ccc !important;
        cursor: not-allowed;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA HANDLING ---
FILE_PATH = 'problems.csv'

def load_data():
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Timestamp", "Category", "Problem", "Status", "Upvotes"])
        df.to_csv(FILE_PATH, index=False)
        return df
    
    df = pd.read_csv(FILE_PATH)
    
    # SAFETY CHECK: If old CSV lacks 'Upvotes' column, add it
    if "Upvotes" not in df.columns:
        df["Upvotes"] = 0
        df.to_csv(FILE_PATH, index=False)
        
    return df

def save_problem(category, problem_text):
    df = load_data()
    new_data = pd.DataFrame({
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M")],
        "Category": [category],
        "Problem": [problem_text],
        "Status": ["New"],
        "Upvotes": [0]
    })
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

def update_vote(index):
    """Increments the vote for a specific row index."""
    df = load_data()
    df.at[index, 'Upvotes'] += 1
    df.to_csv(FILE_PATH, index=False)

# --- 3. PAGE LAYOUT ---
menu = st.sidebar.radio("Navigation", ["📢 Student Wall", "Admin Dashboard"])

if menu == "📢 Student Wall":
    st.title("FPEP Voice Wall")
    
    # --- COMPOSER SECTION ---
    with st.container():
        st.subheader("New Submission")
        col1, col2 = st.columns([3, 1])
        with col1:
            problem_text = st.text_area("Your Voice", height=100, placeholder="What's the problem?", label_visibility="collapsed")
        with col2:
            category = st.selectbox("Category", ["Facilities", "Academic", "Management", "Suggestion"])
            if st.button("Post", use_container_width=True):
                if problem_text:
                    save_problem(category, problem_text)
                    st.success("Posted!")
                    st.rerun()

    st.markdown("---")
    st.subheader("Recent History")

    # --- FEED SECTION ---
    df = load_data()
    if not df.empty:
        # Loop through reversed dataframe (newest first)
        for index, row in df.iloc[::-1].iterrows():
            
            # 1. VISUAL PART (HTML)
            status_class = f"status-{row['Status']}"
            st.markdown(f"""
            <div class="post-card-header">
                <div class="meta-text">
                    <span><strong>{row['Category']}</strong></span>
                    <span class="status-badge {status_class}">{row['Status']}</span>
                </div>
                <div class="main-text">{row['Problem']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. INTERACTIVE PART (Streamlit Columns)
            col_left, col_btn = st.columns([5, 1])
            
            with col_left:
                st.markdown(f"""
                <div class="post-card-body">
                    <small style='color:#888'>{row['Timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
            with col_btn:
                # --- NEW VOTING LOGIC ---
                
                # Check if this specific post (index) is in our 'voted' list
                has_voted = index in st.session_state.voted_posts
                
                # Change Label and Disable if voted
                btn_label = f"✅ {row['Upvotes']}" if has_voted else f"👍 {row['Upvotes']}"
                
                if st.button(btn_label, key=f"vote_{index}", disabled=has_voted):
                    # 1. Update Database
                    update_vote(index)
                    
                    # 2. Add this post to the session's "Voted List"
                    st.session_state.voted_posts.add(index)
                    
                    # 3. Refresh
                    st.rerun()

    else:
        st.info("No posts yet.")

elif menu == "Admin Dashboard":
    st.title("Admin Dashboard")
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "khales23":
        df = load_data()
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(df))
        c2.metric("New", len(df[df['Status'] == 'New']))
        c3.metric("Total Upvotes", df['Upvotes'].sum())
        
        st.markdown("---")
        
        # Editor
        if not df.empty:
            df["Delete"] = False
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn("Status", options=["New", "Reviewed", "Solved"], required=True),
                    "Delete": st.column_config.CheckboxColumn("Delete?", default=False),
                    "Upvotes": st.column_config.NumberColumn("Votes", disabled=True)
                },
                disabled=["Timestamp", "Category", "Problem", "Upvotes"],
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("Save Changes"):
                clean_df = edited_df[edited_df["Delete"] == False].drop(columns=["Delete"])
                clean_df.to_csv(FILE_PATH, index=False)
                st.success("Updated!")
                st.rerun()




