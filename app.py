import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Student Voice Wall", page_icon="📢", layout="centered")

# Custom CSS to force the Maroon Design
st.markdown("""
    <style>
    /* Global Variables */
    :root {
        --primary-maroon: #800000;
        --light-maroon: #a31515;
    }
    
    /* Title Styling */
    h1 { color: var(--primary-maroon) !important; }
    
    /* Button Styling */
    div.stButton > button {
        background-color: var(--primary-maroon);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
    }
    div.stButton > button:hover {
        background-color: var(--light-maroon);
        color: white;
        border-color: white;
    }

    /* The "Card" Design for the Wall */
    .post-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid var(--primary-maroon);
    }
    .post-header {
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
    }
    .post-content {
        font-size: 16px;
        color: #333;
        margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
    }
    /* Status Colors */
    .status-New { background-color: #ffeeba; color: #856404; }
    .status-Reviewed { background-color: #d4edda; color: #155724; }
    .status-Solved { background-color: #cce5ff; color: #004085; }
    
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA HANDLING (DATABASE) ---
FILE_PATH = 'problems.csv'

def load_data():
    """Loads data from CSV. Creates file if it doesn't exist."""
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Timestamp", "Category", "Problem", "Status", "Upvotes"])
        df.to_csv(FILE_PATH, index=False)
        return df
    return pd.read_csv(FILE_PATH)

def save_problem(category, problem_text):
    """Saves a new problem to the CSV."""
    df = load_data()
    new_data = pd.DataFrame({
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M")],
        "Category": [category],
        "Problem": [problem_text],
        "Status": ["New"], # Default status
        "Upvotes": [0]
    })
    # Append properly using concat
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)

# --- 3. SIDEBAR (NAVIGATION & ADMIN) ---
menu = st.sidebar.radio("Navigation", ["📢 Student Wall", "🛡️ Founder Dashboard"])

st.sidebar.markdown("---")
st.sidebar.info("This app saves data to `problems.csv` in the same folder.")

# --- 4. PAGE: STUDENT WALL ---
if menu == "📢 Student Wall":
    
    # Header
    st.title("Student Voice Wall")
    st.markdown("Share your problems. We listen, track, and solve.")
    
    # Input Form (Composer)
    with st.container():
        st.subheader("New Submission")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            problem_text = st.text_area("What issue are you facing?", height=100, placeholder="Type your problem here...")
        
        with col2:
            category = st.selectbox("Category", ["Facilities", "Academic", "Management", "Suggestion"])
            if st.button("Post to Wall"):
                if problem_text:
                    save_problem(category, problem_text)
                    st.success("Posted successfully!")
                    st.rerun() # Refresh page to show new post
                else:
                    st.error("Please write something first.")

    st.markdown("---")
    st.subheader("Recent History")

    # Display The Feed
    df = load_data()
    
    if not df.empty:
        # Show newest first
        for index, row in df.iloc[::-1].iterrows():
            
            # Determine Badge Color
            status_class = f"status-{row['Status']}"
            
            # Create HTML Card
            card_html = f"""
            <div class="post-card">
                <div class="post-header">
                    <span><strong>Category:</strong> {row['Category']}</span>
                    <span>{row['Timestamp']}</span>
                </div>
                <div class="post-content">
                    {row['Problem']}
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="status-badge {status_class}">Status: {row['Status']}</span>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No posts yet. Be the first to share a problem!")

# --- 5. PAGE: FOUNDER DASHBOARD ---
elif menu == "🛡️ Founder Dashboard":
    st.title("Founder Dashboard")
    
    # Simple Password Check
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123": 
        st.success("Logged in as Founder")
        
        # Load Data
        df = load_data()
        
        # 1. Metrics Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Problems", len(df))
        col2.metric("Pending Review", len(df[df['Status'] == 'New']))
        col3.metric("Resolved", len(df[df['Status'] == 'Solved']))
        
        st.markdown("---")
        
        # 2. Editable Data Table
        st.subheader("Manage Problems")
        st.caption("Change Status or check 'Delete' box to remove a post.")
        
        if not df.empty:
            # Add a temporary "Delete" column for the UI (default is False/Unchecked)
            df["Delete"] = False

            # Configure the Table
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["New", "Reviewed", "Solved"],
                        required=True,
                    ),
                    "Delete": st.column_config.CheckboxColumn(
                        "Delete?",
                        help="Check this box and click Save to remove the post",
                        default=False,
                    )
                },
                disabled=["Timestamp", "Category", "Problem", "Upvotes"], # Prevent editing text, only allow Status/Delete
                num_rows="fixed", # Disable adding new empty rows manually
                use_container_width=True,
                hide_index=True
            )
            
            # Save changes button
            if st.button("Save Changes"):
                # 1. Filter out rows where Delete is True
                # We keep only rows where Delete is False
                clean_df = edited_df[edited_df["Delete"] == False]
                
                # 2. Remove the temporary 'Delete' column before saving to CSV
                clean_df = clean_df.drop(columns=["Delete"])
                
                # 3. Save to file
                clean_df.to_csv(FILE_PATH, index=False)
                st.success("Database updated successfully!")
                st.rerun() # Reload page to show changes
        else:
            st.info("No problems submitted yet.")
            
    else:
        st.warning("Please enter the admin password in the sidebar to access the dashboard.")
