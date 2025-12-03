import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import time # Used for simulating delays

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="FPEP Voice Wall & Auth", page_icon="🔑", layout="centered")

# --- INITIALIZATION ---
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "voted_posts" not in st.session_state:
    st.session_state.voted_posts = set()
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Custom CSS
st.markdown("""
    <style>
    /* Menggunakan warna maroon dari CSS asal anda (#7e0000) */
    :root { 
        --primary-maroon: #7e0000; 
        --light-maroon: #a31515; 
        --primary-blue: #1f50a2;
    }
    
    h1 { color: var(--primary-maroon) !important; }
    h2 { color: var(--primary-maroon) !important; text-align: center; font-size: 32px; }
    
    /* Post Card Styling (retained from Voice Wall) */
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

    /* Customizing Auth Buttons (Maroon color from the CSS) */
    .stButton>button {
        background-color: var(--primary-maroon);
        color: white;
        border: none;
        border-radius: 40px; /* Matching the 40px radius from your CSS */
        padding: 10px;
        width: 100%;
        margin-top: 15px;
        box-shadow: 0 0 10px rgba(0, 0, 0, .3); 
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: var(--light-maroon);
    }
    .stContainer {
        /* Styling the background of the auth form area */
        background-color: #f7f9fc; 
        border-radius: 15px;
        padding: 20px;
    }
    
    </style>
""", unsafe_allow_html=True)


# --- DATA HANDLING FUNCTIONS ---
FILE_PATH = 'problems.csv'

def load_data():
    """Loads or initializes the problems CSV file."""
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Timestamp", "Category", "Problem", "Status", "Upvotes"])
        df.to_csv(FILE_PATH, index=False)
        return df
    
    df = pd.read_csv(FILE_PATH)
    if "Upvotes" not in df.columns:
        df["Upvotes"] = 0
        df.to_csv(FILE_PATH, index=False)
    df['Upvotes'] = df['Upvotes'].fillna(0).astype(int)
    return df

def save_problem(category, problem_text):
    """Saves a new problem submission."""
    df = load_data()
    malaysia_offset = timezone(timedelta(hours=8))
    current_time_my = datetime.now(malaysia_offset).strftime("%Y-%m-%d %H:%M")
    
    new_data = pd.DataFrame({
        "Timestamp": [current_time_my],
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
    if index in df.index:
        df.loc[index, 'Upvotes'] += 1
        df.to_csv(FILE_PATH, index=False)
    else:
        st.error(f"Error: Post index {index} not found.")


# --- AUTHENTICATION LOGIC ---

# Credentials for demonstration
# Admin: admin / khales23 (same as Admin Action Password)
# Student: student / student123
def handle_login(username, password):
    """Simulates user login."""
    if username == "admin" and password == "khales23":
        st.session_state.is_logged_in = True
        st.session_state.current_user = "admin"
        return True
    elif username == "student" and password == "student123":
        st.session_state.is_logged_in = True
        st.session_state.current_user = "student"
        return True
    return False

def handle_logout():
    """Logs the user out and resets state."""
    st.session_state.is_logged_in = False
    st.session_state.current_user = None
    st.session_state.voted_posts = set()
    st.rerun()

def show_auth_form():
    """Displays the combined Login/Sign Up forms side-by-side."""
    
    st.title("Welcome to the FPEP Voice Wall")
    st.markdown("Please sign in or register to continue.")
    
    # Use columns to mimic the side-by-side layout 
    col1, col2 = st.columns(2)

    # --- SIGN IN FORM (Equivalent to form-box login) ---
    with col1.container(border=True):
        st.markdown("<h2>Sign In</h2>", unsafe_allow_html=True)
        
        login_username = st.text_input("Username", key="login_user_auth", placeholder="admin (khales23) or student (student123)")
        login_password = st.text_input("Password", type="password", key="login_pass_auth", placeholder="Password")
        
        if st.button("Login", key="login_btn_auth", use_container_width=True):
            if login_username and login_password:
                with st.spinner('Logging in...'):
                    time.sleep(1) 
                if handle_login(login_username, login_password):
                    st.success(f"Successfully logged in as **{login_username}**!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.warning("Please enter both username and password.")
        
        st.markdown("<h3 style='text-align:center; margin-top: 30px; color:#555;'>Welcome Back!</h3>", unsafe_allow_html=True)


    # --- SIGN UP FORM (Equivalent to form-box register) ---
    with col2.container(border=True):
        st.markdown("<h2>Sign Up</h2>", unsafe_allow_html=True)
        
        register_username = st.text_input("Username", key="reg_user_auth", placeholder="Choose a username")
        register_email = st.text_input("Email", key="reg_email_auth", placeholder="Enter your email")
        register_password = st.text_input("Password", type="password", key="reg_pass_auth", placeholder="Choose a secure password")
        
        # Placeholder for registration logic (no actual saving)
        if st.button("Sign Up", key="register_btn_auth", use_container_width=True):
            if register_username and register_email and register_password:
                with st.spinner('Registering user...'):
                    time.sleep(1)
                st.success(f"Registration simulated for **{register_username}**. Please use 'student' to login.")
            else:
                st.warning("Please fill in all registration fields.")
                
        st.markdown("<h3 style='text-align:center; margin-top: 30px; color:#555;'>Hello, Friend!</h3>", unsafe_allow_html=True)
        st.caption("Register with your details to use all features.")


# --- MAIN APPLICATION VIEWS (Retained from previous version) ---

def show_student_wall():
    """Displays the main student submission and voting wall."""
    st.title("📢 FPEP Voice Wall")
    
    st.sidebar.button("Logout", on_click=handle_logout)
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.current_user}`")

    with st.container(border=True):
        st.subheader("New Submission")
        col1, col2 = st.columns([3, 1])
        with col1:
            problem_text = st.text_area("Your Voice", height=100, placeholder="What's the problem?", label_visibility="collapsed")
        with col2:
            category = st.selectbox("Category", ["Facilities", "Academic", "Management", "Suggestion"])
            if st.button("Post", use_container_width=True, key="post_btn"):
                if problem_text:
                    save_problem(category, problem_text)
                    st.success("Posted!")
                    st.rerun()

    st.markdown("---")
    st.subheader("Recent History (Upvote the problems you agree with)")

    df = load_data()
    if not df.empty:
        df_display = df.reset_index().iloc[::-1]
        
        for original_index, row in df_display.iterrows():
            post_id = row['index'] 
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
            
            col_left, col_btn = st.columns([5, 1])
            
            with col_left:
                st.markdown(f"""
                <div class="post-card-body">
                    <small style='color:#888'>Posted: {row['Timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
            with col_btn:
                has_voted = post_id in st.session_state.voted_posts
                btn_label = f"✅ {row['Upvotes']}" if has_voted else f"👍 {row['Upvotes']}"
                
                if st.button(btn_label, key=f"vote_{post_id}", disabled=has_voted, use_container_width=True):
                    update_vote(post_id)
                    st.session_state.voted_posts.add(post_id)
                    st.rerun()

    else:
        st.info("No posts yet. Be the first to submit a problem or suggestion!")


def show_admin_dashboard():
    """Displays the admin dashboard for managing posts."""
    st.title("🔒 Admin Dashboard")
    st.sidebar.button("Logout", on_click=handle_logout)
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.current_user}`")

    admin_password = st.text_input("Admin Action Password", type="password", key="admin_action_pass")
    
    if admin_password == "khales23":
        df = load_data()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Posts", len(df))
        c2.metric("New Posts", len(df[df['Status'] == 'New']))
        c3.metric("Total Upvotes", df['Upvotes'].sum())
        
        st.markdown("---")
        st.subheader("Manage Submissions")
        
        if not df.empty:
            df["Delete"] = False
            df_editable = df.reset_index(drop=False)
            
            edited_df = st.data_editor(
                df_editable,
                column_config={
                    "index": st.column_config.NumberColumn("Post ID", disabled=True),
                    "Status": st.column_config.SelectboxColumn("Status", options=["New", "Reviewed", "Solved"], required=True),
                    "Delete": st.column_config.CheckboxColumn("Delete?", default=False),
                    "Upvotes": st.column_config.NumberColumn("Votes", disabled=True)
                },
                disabled=["Timestamp", "Category", "Problem", "Upvotes", "index"],
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("Save Changes", key="admin_save_btn"):
                posts_to_keep = edited_df[edited_df["Delete"] == False]
                original_indices_to_keep = posts_to_keep['index'].tolist()
                
                for idx in original_indices_to_keep:
                    new_status = posts_to_keep[posts_to_keep['index'] == idx]['Status'].iloc[0]
                    df.loc[idx, 'Status'] = new_status
                
                df_final = df.loc[original_indices_to_keep].drop(columns=["Delete"], errors='ignore')
                
                df_final.to_csv(FILE_PATH, index=False)
                st.success("Changes saved successfully (Statuses updated and deletions processed)!")
                st.rerun()

        else:
            st.info("The Voice Wall is empty.")
            
    else:
        st.warning("Enter the Admin Action Password to manage posts.")


# --- MAIN APP FLOW ---

if not st.session_state.is_logged_in:
    show_auth_form()
else:
    if st.session_state.current_user == "admin":
        menu = st.sidebar.radio("Navigation", ["📢 Student Wall", "🔒 Admin Dashboard"], index=1)
        if menu == "📢 Student Wall":
            show_student_wall()
        elif menu == "🔒 Admin Dashboard":
            show_admin_dashboard()
    else:
        show_student_wall()
