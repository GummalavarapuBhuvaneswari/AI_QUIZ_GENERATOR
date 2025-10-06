import streamlit as st
import sqlite3
import hashlib
import time
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Smart Quizzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with better button styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* Header */
    .main-title {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        color: white;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        margin-bottom: 1rem;
        padding: 40px 0 20px 0;
    }

    .sub-title {
        font-size: 1.5rem;
        text-align: center;
        color: white;
        font-weight: 500;
        margin-bottom: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    /* Navigation container */
    .nav-container {
        position: fixed;
        top: 15px;
        right: 20px;
        z-index: 999999;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        border-radius: 25px;
        border: 2px solid rgba(255,255,255,0.5);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    /* NAVIGATION buttons - teal/green */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
        margin: 2px !important;
        min-width: 100px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="column"] button:hover {
        background: linear-gradient(135deg, #0072ff 0%, #00c6ff 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
    }

    /* Main action buttons (Login/Register/Start/Submit) - opposite warm gradient */
    .stButton button {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: bold;
        width: 100%;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #ffd200 0%, #f7971e 100%);
        color: #333;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    
    /* NAVIGATION buttons (Home, Login, Register, Dashboard, Logout) */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;  /* blue gradient */
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
        margin: 2px !important;
        min-width: 100px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="column"] button:hover {
        background: linear-gradient(135deg, #0072ff 0%, #00c6ff 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
    }

    /* MAIN ACTION buttons (Login, Register, Start Quiz, Submit Quiz) */
    .stButton button {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);  /* orange-gold gradient */
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: bold;
        width: 100%;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #ffd200 0%, #f7971e 100%);
        color: #333;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }

    /* Cards */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        height: 100%;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #667eea;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.5;
    }
    
    .timer {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff6b6b;
        text-align: center;
        padding: 10px;
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .instructions {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    
    .question-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border-left: 5px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)


# Database setup
def init_db():
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT,
            subtopic TEXT,
            skill_level TEXT,
            score INTEGER,
            total_questions INTEGER,
            time_taken INTEGER,
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id INTEGER,
            question TEXT,
            user_answer TEXT,
            correct_answer TEXT,
            is_correct BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, email="", full_name=""):
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), email, full_name)
        )
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def verify_user(username, password):
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, username, full_name FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
    user = c.fetchone()
    conn.close()
    return user

def record_session(user_id, topic, subtopic, skill_level, score=0, total_questions=0, time_taken=0):
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    c.execute(
        """INSERT INTO user_sessions (user_id, topic, subtopic, skill_level, score, total_questions, time_taken) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, topic, subtopic, skill_level, score, total_questions, time_taken)
    )
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_quiz_result(user_id, session_id, question, user_answer, correct_answer, is_correct):
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    c.execute(
        """INSERT INTO quiz_results (user_id, session_id, question, user_answer, correct_answer, is_correct) 
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, session_id, question, user_answer, correct_answer, is_correct)
    )
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_sessions WHERE user_id = ?", (user_id,))
    total = c.fetchone()[0]
    
    c.execute("SELECT AVG(score) FROM user_sessions WHERE user_id = ?", (user_id,))
    avg_score = c.fetchone()[0] or 0
    
    conn.close()
    return total, round(avg_score, 1)

# Quiz questions database
def get_questions(topic, subtopic, level, count=10):
    # Sample questions database
    questions_db = {
        "Computer Science": {
            "Python": {
                "Beginner": [
                    {
                        "question": "Which keyword is used to define a function in Python?",
                        "options": ["function", "def", "define", "func"],
                        "correct": 1
                    },
                    {
                        "question": "What is the output of print(2 ** 3)?",
                        "options": ["6", "8", "9", "5"],
                        "correct": 1
                    },
                    {
                        "question": "Which data type is mutable in Python?",
                        "options": ["tuple", "string", "list", "int"],
                        "correct": 2
                    }
                ],
                "Intermediate": [
                    {
                        "question": "What does the 'self' parameter represent in Python class methods?",
                        "options": ["The class itself", "The instance of the class", "A static method", "A decorator"],
                        "correct": 1
                    },
                    {
                        "question": "Which method is used to add an element to a set?",
                        "options": ["append()", "add()", "insert()", "push()"],
                        "correct": 1
                    }
                ],
                "Advanced": [
                    {
                        "question": "What is the time complexity of searching in a Python dictionary?",
                        "options": ["O(n)", "O(log n)", "O(1)", "O(n²)"],
                        "correct": 2
                    }
                ]
            },
            "Java": {
                "Beginner": [
                    {
                        "question": "What is the entry point of a Java program?",
                        "options": ["main() method", "start() method", "run() method", "execute() method"],
                        "correct": 0
                    },
                    {
                        "question": "Which keyword is used to inherit a class in Java?",
                        "options": ["implements", "extends", "inherits", "super"],
                        "correct": 1
                    }
                ],
                "Intermediate": [
                    {
                        "question": "What is method overloading in Java?",
                        "options": [
                            "Same method name with different return types",
                            "Same method name with different parameters",
                            "Same method name in different classes",
                            "Same method name with different access modifiers"
                        ],
                        "correct": 1
                    }
                ],
                "Advanced": [
                    {
                        "question": "What is the purpose of the 'volatile' keyword in Java?",
                        "options": [
                            "To make variable constant",
                            "To indicate variable may be changed by multiple threads",
                            "To improve performance",
                            "To prevent garbage collection"
                        ],
                        "correct": 1
                    }
                ]
            },
            "C++": {
                "Beginner": [
                    {
                        "question": "Which operator is used for dynamic memory allocation in C++?",
                        "options": ["malloc", "new", "alloc", "create"],
                        "correct": 1
                    }
                ],
                "Intermediate": [
                    {
                        "question": "What is a virtual function in C++?",
                        "options": [
                            "A function that doesn't exist",
                            "A function that can be overridden in derived classes",
                            "A function that runs faster",
                            "A function that uses virtual memory"
                        ],
                        "correct": 1
                    }
                ]
            }
        },
        "Mathematics": {
            "Algebra": {
                "Beginner": [
                    {
                        "question": "Solve for x: 2x + 5 = 15",
                        "options": ["5", "10", "7.5", "8"],
                        "correct": 0
                    }
                ]
            }
        }
    }
    
    # Get questions for the selected topic, subtopic and level
    try:
        questions = questions_db[topic][subtopic][level]
        return random.sample(questions, min(count, len(questions)))
    except:
        # Return some default questions if specific ones not found
        return [
            {
                "question": f"Sample question for {subtopic} ({level})",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0
            }
        ] * min(count, 5)

# Initialize database
init_db()

# Main app
def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'quiz_start_time' not in st.session_state:
        st.session_state.quiz_start_time = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None

    # Main header - ALWAYS VISIBLE
    st.markdown('<div class="main-title">🧠 Smart Quizzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI-Powered Adaptive Learning Platform</div>', unsafe_allow_html=True)

    # CREATE NAVIGATION BUTTONS AFTER THE HEADER
    create_navigation()

    # Page routing - FAST AND SIMPLE
    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'register':
        show_register_page()
    elif st.session_state.page == 'dashboard':
        show_dashboard()
    elif st.session_state.page == 'quiz':
        show_quiz_page()
    elif st.session_state.page == 'results':
        show_results_page()

# IMPROVED NAVIGATION WITH BETTER PLACEMENT AND COLORS
def create_navigation():
    # Create a fixed navigation container at top right - MORE VISIBLE
    st.markdown("""
    <div class="nav-container">
        <div class="nav-btn-container">
    """, unsafe_allow_html=True)
    
    # Store the next page in a variable to handle navigation properly
    next_page = st.session_state.page
    
    # Create compact navigation buttons in a row
    if st.session_state.user is None:
        # For non-logged in users - COMPACT BUTTONS
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🏠 Home", key="nav_home_top", use_container_width=True):
                next_page = 'home'
        with col2:
            if st.button("🔐 Login", key="nav_login_top", use_container_width=True):
                next_page = 'login'
        with col3:
            if st.button("📝 Register", key="nav_register_top", use_container_width=True):
                next_page = 'register'
    else:
        # For logged in users - COMPACT BUTTONS
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🏠 Home", key="nav_home_auth_top", use_container_width=True):
                next_page = 'home'
        with col2:
            if st.button("📊 Dashboard", key="nav_dashboard_top", use_container_width=True):
                next_page = 'dashboard'
        with col3:
            if st.button("🚪 Logout", key="nav_logout_top", use_container_width=True):
                st.session_state.user = None
                next_page = 'home'
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Apply navigation if page changed
    if next_page != st.session_state.page:
        st.session_state.page = next_page
        st.rerun()

def show_home_page():
    st.markdown("""
    <div style='text-align: center; color: white; font-size: 1.3rem; margin: 2rem 0;'>
        Transform your learning experience with AI-powered adaptive quizzes that adjust to your skill level.
    </div>
    """, unsafe_allow_html=True)

    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Powered</div>
            <div class="feature-desc">Intelligent question generation using advanced algorithms</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Adaptive Learning</div>
            <div class="feature-desc">Difficulty adjusts based on your performance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Progress Tracking</div>
            <div class="feature-desc">Monitor your learning journey with analytics</div>
        </div>
        """, unsafe_allow_html=True)

    # CTA
    st.markdown("""
    <div style='text-align: center; color: white; font-size: 1.2rem; margin: 3rem 0;'>
        Ready to start your learning journey?
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started For Free", use_container_width=True, key="get_started_home"):
            if st.session_state.user:
                st.session_state.page = 'dashboard'
            else:
                st.session_state.page = 'register'
            st.rerun()

def show_login_page():
    st.markdown("""
    <div style='text-align: center; color: white; font-size: 1.5rem; margin: 2rem 0;'>
        Welcome Back!
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
            
            submit = st.form_submit_button("🚀 Sign In", use_container_width=True)
            if submit:
                if username and password:
                    user = verify_user(username, password)
                    if user:
                        st.session_state.user = {
                            'id': user[0],
                            'username': user[1],
                            'full_name': user[2]
                        }
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please fill all fields")
            
            st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <p>Don't have an account? <strong>Click Register button above</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_register_page():
    st.markdown("""
    <div style='text-align: center; color: white; font-size: 1.5rem; margin: 2rem 0;'>
        Create Your Account
    </div>
    """, unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            full_name = st.text_input("👤 Full Name", placeholder="Enter your full name", key="reg_fullname")
            email = st.text_input("📧 Email", placeholder="Enter your email", key="reg_email")
            username = st.text_input("👤 Username", placeholder="Choose a username", key="reg_username")
            password = st.text_input("🔒 Password", type="password", placeholder="Create a password", key="reg_password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")
            
            submit = st.form_submit_button("🚀 Create Account", use_container_width=True)
            if submit:
                if all([full_name, username, password, confirm_password]):
                    if password == confirm_password:
                        if add_user(username, password, email, full_name):
                            st.success("Account created successfully! Please login.")
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error("Username already exists")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill all fields")
            
            st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <p>Already have an account? <strong>Click Login button above</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    if not st.session_state.user:
        st.session_state.page = 'login'
        st.rerun()
        return

    user_stats, avg_score = get_user_stats(st.session_state.user['id'])
    
    st.markdown(f"""
    <div style='text-align: center; color: white; font-size: 1.5rem; margin: 2rem 0;'>
        Welcome, {st.session_state.user['full_name'] or st.session_state.user['username']}!
    </div>
    """, unsafe_allow_html=True)

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>📊 Total Quizzes</h3>
            <p style='font-size: 2rem; color: #3B82F6;'>{user_stats}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>⭐ Average Score</h3>
            <p style='font-size: 2rem; color: #3B82F6;'>{avg_score}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h3>🎯 Ready to Learn?</h3>
            <p>Start a new quiz session</p>
        </div>
        """, unsafe_allow_html=True)

    # Quiz start
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Start New Quiz")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        topic = st.selectbox("Subject", ["Computer Science", "Mathematics", "Science", "History", "Geography"], key="topic_select")
    with col2:
        if topic == "Computer Science":
            subtopic = st.selectbox("Sub-topic", ["Python", "Java", "C++", "JavaScript", "Data Structures"], key="cs_subtopic")
        elif topic == "Mathematics":
            subtopic = st.selectbox("Sub-topic", ["Algebra", "Calculus", "Geometry", "Statistics"], key="math_subtopic")
        else:
            subtopic = st.selectbox("Sub-topic", ["Fundamentals", "Advanced Concepts"], key="other_subtopic")
    with col3:
        level = st.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"], key="level_select")
    
    # Instructions
    st.markdown("""
    <div class="instructions">
        <h4>📝 Quiz Instructions:</h4>
        <ul>
            <li>You will have <strong>10 minutes</strong> to complete the quiz</li>
            <li>Total questions: <strong>10</strong></li>
            <li>Each question carries equal marks</li>
            <li>No negative marking for wrong answers</li>
            <li>Timer will start once you begin the quiz</li>
            <li>You cannot pause or restart the quiz once started</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎯 Start Quiz", use_container_width=True, key="start_quiz_btn"):
        # Initialize quiz session
        st.session_state.quiz_started = True
        st.session_state.quiz_questions = get_questions(topic, subtopic, level, 10)
        st.session_state.current_question = 0
        st.session_state.user_answers = [None] * len(st.session_state.quiz_questions)
        st.session_state.quiz_start_time = datetime.now()
        st.session_state.session_id = record_session(
            st.session_state.user['id'], 
            topic, 
            subtopic, 
            level
        )
        st.session_state.page = 'quiz'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_quiz_page():
    if not st.session_state.user or not st.session_state.quiz_started:
        st.session_state.page = 'dashboard'
        st.rerun()
        return

    # Timer calculation
    elapsed_time = datetime.now() - st.session_state.quiz_start_time
    remaining_time = max(600 - elapsed_time.total_seconds(), 0)  # 10 minutes = 600 seconds
    
    if remaining_time <= 0:
        # Time's up - auto submit
        st.session_state.page = 'results'
        st.rerun()
        return
    
    # Display timer
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    st.markdown(f"""
    <div class="timer">
        ⏰ Time Remaining: {minutes:02d}:{seconds:02d}
    </div>
    """, unsafe_allow_html=True)

    # Current question
    question_data = st.session_state.quiz_questions[st.session_state.current_question]
    
    st.markdown(f"""
    <div class="question-card">
        <h3>Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}</h3>
        <p style='font-size: 1.2rem;'>{question_data['question']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Answer options
    selected_option = st.radio(
        "Select your answer:",
        question_data['options'],
        key=f"q_{st.session_state.current_question}"
    )
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_question > 0:
            if st.button("⬅️ Previous", use_container_width=True, key=f"prev_{st.session_state.current_question}"):
                st.session_state.user_answers[st.session_state.current_question] = selected_option
                st.session_state.current_question -= 1
                st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align: center;'>Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
            if st.button("Next ➡️", use_container_width=True, key=f"next_{st.session_state.current_question}"):
                st.session_state.user_answers[st.session_state.current_question] = selected_option
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", use_container_width=True, key="submit_quiz", type="primary"):
                st.session_state.user_answers[st.session_state.current_question] = selected_option
                st.session_state.page = 'results'
                st.rerun()

def show_results_page():
    if not st.session_state.user:
        st.session_state.page = 'login'
        st.rerun()
        return

    # Calculate results
    score = 0
    total_questions = len(st.session_state.quiz_questions)
    
    for i, (question, user_answer) in enumerate(zip(st.session_state.quiz_questions, st.session_state.user_answers)):
        correct_index = question['correct']
        correct_answer = question['options'][correct_index]
        is_correct = (user_answer == correct_answer)
        if is_correct:
            score += 1
        save_quiz_result(
            st.session_state.user['id'],
            st.session_state.session_id,
            question['question'],
            user_answer or "Not answered",
            correct_answer,
            is_correct
        )
    
    percentage = (score / total_questions) * 100
    time_taken = (datetime.now() - st.session_state.quiz_start_time).total_seconds()

    # Update session with final results
    conn = sqlite3.connect('quizzer.db')
    c = conn.cursor()
    c.execute(
        "UPDATE user_sessions SET score = ?, total_questions = ?, time_taken = ? WHERE id = ?",
        (score, total_questions, time_taken, st.session_state.session_id)
    )
    conn.commit()
    conn.close()

    # 🎉 Show confetti if all answers correct
    # Confetti for 100% perfect score
    if score == total_questions:
        st.markdown("""
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <script>
        function launchConfetti() {
            var duration = 5 * 1000;
            var end = Date.now() + duration;
            (function frame() {
                confetti({ particleCount: 7, angle: 60, spread: 70, origin: { x: 0 } });
                confetti({ particleCount: 7, angle: 120, spread: 70, origin: { x: 1 } });
                if (Date.now() < end) requestAnimationFrame(frame);
            }());
        }
        launchConfetti();
        </script>
        """, unsafe_allow_html=True)


    # Performance message
    if percentage >= 80:
        performance_msg = "🎉 Excellent! You're a master!"
        performance_color = "#22c55e"
    elif percentage >= 60:
        performance_msg = "👍 Good job! Keep practicing!"
        performance_color = "#3b82f6"
    elif percentage >= 40:
        performance_msg = "💪 Not bad! Room for improvement."
        performance_color = "#f59e0b"
    else:
        performance_msg = "📚 Keep learning! You'll get better."
        performance_color = "#ef4444"
    
    st.markdown(f"""
    <div style='text-align: center; background: {performance_color}; color: white; padding: 20px; border-radius: 15px; margin: 20px 0;'>
        <h3>{performance_msg}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Review answers
    st.markdown("### 📝 Review Your Answers")
    for i, (question, user_answer) in enumerate(zip(st.session_state.quiz_questions, st.session_state.user_answers)):
        correct_index = question['correct']
        correct_answer = question['options'][correct_index]
        is_correct = (user_answer == correct_answer)
        
        status_icon = "✅" if is_correct else "❌"
        status_color = "#22c55e" if is_correct else "#ef4444"
        
        st.markdown(f"""
        <div class="question-card" style='border-left: 5px solid {status_color};'>
            <h4>Q{i+1}: {question['question']} {status_icon}</h4>
            <p><strong>Your answer:</strong> {user_answer or 'Not answered'}</p>
            <p><strong>Correct answer:</strong> {correct_answer}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Back to Dashboard", use_container_width=True, key="back_to_dashboard"):
            # Reset quiz state
            st.session_state.quiz_started = False
            st.session_state.quiz_questions = []
            st.session_state.current_question = 0
            st.session_state.user_answers = []
            st.session_state.quiz_start_time = None
            st.session_state.session_id = None
            
            st.session_state.page = 'dashboard'
            st.rerun()

if __name__ == "__main__":
    main()