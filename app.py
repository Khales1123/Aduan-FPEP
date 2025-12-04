import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import time # Used for simulating delays

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="FPEP Voice Wall & Auth", page_icon="🔑", layout="centered")

# --- VIDEO BACKGROUND INJECTION ---

# CSS/HTML to set an MP4 file as a fixed, fullscreen background.
# NOTE: Replace 'YOUR_VIDEO_URL.mp4' with a direct link to your video file.
VIDEO_BACKGROUND_HTML = """
<style>
/* 1. Hide the default Streamlit background */
.stApp {
    background: transparent !important;
}

/* 2. Create the video container and place it on the lowest layer */
#video-background-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1000; /* Place it behind everything */
    overflow: hidden;
}

#video-background-container video {
    min-width: 100%; 
    min-height: 100%;
    width: auto;
    height: auto;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    /* Dim the video slightly to make text easier to read */
    opacity: 0.7; 
}

/* 3. Ensure the main Streamlit content remains readable over the video */
.stApp > header, 
.stApp > div:first-child > div:nth-child(2) > div:first-child,
.stApp > div:nth-child(1) > div:nth-child(1) { 
    background-color: rgba(255, 255, 255, 0.85); /* Semi-transparent white background for readability */
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>

<!-- HTML video injection -->
<div id="video-background-container">
    <video autoplay muted loop>
        <source src="YOUR_VIDEO_URL.mp4" type="video/mp4">
        Your browser does not support HTML5 video.
    </video>
</div>
"""
st.markdown(VIDEO_BACKGROUND_HTML, unsafe_allow_html=True)


# --- Custom App Styling (Post Styling UPDATED to Maroon Box with White Border) ---
st.markdown("""
    <style>
    :root { 
        --primary-maroon: #800000; 
        --light-maroon: #a31515; 
        --primary-blue: #1f50a2;
    }
    
    h1 { color: var(--primary-maroon) !important; }
    h2 { color: var(--primary-blue) !important; text-align: center; }
    
    /* Post Card Styling: Background is MAROON, Text is Light */
    [data-testid="stContainer"] {
        background-color: white !important; 
    }
    
    /* === BORDER & COLOR CHANGES START HERE === */
    .post-card-header {
        background-color: var(--primary-maroon) !important; /* MAROON BACKGROUND */
        padding: 20px 20px 5px 20px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        color: #F0F0F0; /* Light text color */
        
        /* Strong WHITE Border (3px) */
        border: 3px solid white !important; 
        border-bottom: none !important; /* Seamless connection */
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .post-card-body {
        background-color: var(--primary-maroon) !important; /* MAROON BACKGROUND */
        padding: 5px 20px 20px 20px;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        color: #F0F0F0; /* Light text color */
        
        /* Strong WHITE Border (3px) */
        border: 3px solid white !important;
        border-top: none !important; /* Seamless connection */
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    
    /* Ensure the metadata and main text are light colored */
    .meta-text { font-size: 14px; color: #F0F0F0; display: flex; justify-content: space-between; } 
    .main-text { font-size: 16px; color: white; margin-top: 10px; white-space: pre-wrap; }
    /* === BORDER & COLOR CHANGES END HERE === */

    
    /* Status Badges */
    .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;}
    .status-New { background-color: #fff3cd; color: #856404; }
    .status-Reviewed { background-color: #d4edda; color: #155724; }
    .status-Solved { background-color: #cce5ff; color: #004085; }
    
    /* Customizing Auth Buttons */
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
        width: 100%;
        margin-top: 15px;
    }
    
    </style>
""", unsafe_allow_html=True)


# --- 2. INITIALIZATION ---
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "voted_posts" not in st.session_state:
    st.session_state.voted_posts = set()
if "current_user" not in st.session_state:
    st.session_state.current_user = None


# --- 3. DATA HANDLING FUNCTIONS ---
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


# --- 4. AUTHENTICATION LOGIC ---

def handle_login(username, password):
    """
    Simulates user login.
    Credentials: admin/khales23, student/student123
    """
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
    """Displays only the Login form, centered."""
    
    st.title("Welcome to the FPEP Voice Wall")
    st.markdown("Please sign in to continue.")

    # Use Streamlit columns to center the single login form (2/4 width)
    col_center_left, col_form, col_center_right = st.columns([1, 2, 1])

    # --- SIGN IN FORM ---
    with col_form.container(border=True):
        st.markdown("<h2>Sign In</h2>", unsafe_allow_html=True)
        
        login_username = st.text_input("Username", key="login_user_auth", placeholder="admin or student")
        login_password = st.text_input("Password", type="password", key="login_pass_auth", placeholder="Enter your password (student123)")
        
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


# --- 5. MAIN APPLICATION VIEWS ---

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
            
            # --- POST CARD HEADER ---
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
                # --- POST CARD BODY LEFT (Timestamp text color set to light gray) ---
                st.markdown(f"""
                <div class="post-card-body">
                    <small style='color:#F0F0F0'>Posted: {row['Timestamp']}</small>
                </div>
                """, unsafe_allow_html=True) 
                
            with col_btn:
                # --- BUTTON COLUMN ---
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

    
    # Admin password check (Admin-specific, separate from the main login)
    admin_password = st.text_input("Admin Action Password", type="password", key="admin_action_pass")
    
    # Use the same admin password logic from the original code
    if admin_password == "khales23":
        df = load_data()
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Posts", len(df))
        c2.metric("New Posts", len(df[df['Status'] == 'New']))
        c3.metric("Total Upvotes", df['Upvotes'].sum())
        
        st.markdown("---")
        st.subheader("Manage Submissions")
        
        # Editor
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


# --- 6. MAIN APP FLOW ---

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
