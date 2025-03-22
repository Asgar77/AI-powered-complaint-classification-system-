import streamlit as st
import sqlite3
import pandas as pd
import re
from groq import Groq
import os
from streamlit_option_menu import option_menu
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
import base64

# Page config
st.set_page_config(page_title="TechZone Complaint System", layout="wide", initial_sidebar_state="expanded")

# Departments
DEPARTMENTS = ["Technical Support", "Billing", "Customer Service", "Shipping", "General Queries"]

# Initialize Groq client
client = Groq(api_key="your_groq_api_key")

# Classification function using Groq
def classify_complaint_llm(complaint: str) -> (str, float):
    try:
        prompt = f"""
        Classify the following customer complaint into exactly one of these departments: {', '.join(DEPARTMENTS)}.
        Provide a confidence score between 0 and 1.
        
        Respond in the format:
        Department: <Department Name>
        Confidence: <Confidence Score>

        Complaint: {complaint}
        """
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=200
        )
        response = chat_completion.choices[0].message.content.strip()
        
        department, confidence = "", 0.0
        for line in response.split("\n"):
            if line.startswith("Department:"):
                department = line.split(":", 1)[1].strip()
            elif line.startswith("Confidence:"):
                confidence = float(line.split(":", 1)[1].strip())
        
        if department not in DEPARTMENTS:
            department = "General Queries"
        return department, confidence
    except Exception as e:
        st.error(f"Classification failed: {e}")
        return "General Queries", 0.0

# Email sending function (Adapted from School Fee Management System)
def send_email(recipient_email, subject, message):
    try:
        # Email credentials from secrets (update your secrets.toml accordingly)
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
        
        # Create MIME message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))  # Use HTML formatting
        
        # Connect to SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Updated email function for admin notification
def send_email_to_admin(complaint_data, confidence_score):
    subject = "Low Confidence Complaint Alert"
    message = f"""
    <html>
        <body style='font-family: Arial, sans-serif;'>
            <h2 style='color: #1e40af;'>Low Confidence Complaint Alert</h2>
            <p>Dear Administrator,</p>
            <p>A complaint has been classified with a confidence score of <strong>{confidence_score:.2%}</strong> (below 70% threshold). Please review the details below:</p>
            <table style='border-collapse: collapse; width: 100%;'>
                <tr>
                    <th style='border: 1px solid #ddd; padding: 8px; background-color: #f1f5f9;'>Field</th>
                    <th style='border: 1px solid #ddd; padding: 8px; background-color: #f1f5f9;'>Details</th>
                </tr>
                <tr>
                    <td style='border: 1px solid #ddd; padding: 8px;'>Name</td>
                    <td style='border: 1px solid #ddd; padding: 8px;'>{complaint_data['name']}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid #ddd; padding: 8px;'>Age</td>
                    <td style='border: 1px solid #ddd; padding: 8px;'>{complaint_data['age']}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid #ddd; padding: 8px;'>Mobile</td>
                    <td style='border: 1px solid #ddd; padding: 8px;'>{complaint_data['mobile_number']}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid #ddd; padding: 8px;'>Email</td>
                    <td style='border: 1px solid #ddd; padding: 8px;'>{complaint_data['email_id']}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid #ddd; padding: 8px;'>Complaint</td>
                    <td style='border: 1px solid #ddd; padding: 8px;'>{complaint_data['complaint']}</td>
                </tr>
                <tr>
                    <td style='border: 1px solid #ddd; padding: 8px;'>Department</td>
                    <td style='border: 1px solid #ddd; padding: 8px;'>{complaint_data['department']}</td>
                </tr>
            </table>
            <p>Please review this complaint manually to ensure proper handling.</p>
            <p style='color: #64748b;'>Thank you for your attention.</p>
        </body>
    </html>
    """
    admin_email = st.secrets["email"]["admin_email"]
    return send_email(admin_email, subject, message)

# Database with migration
@st.cache_resource
def init_db():
    conn = sqlite3.connect('complaints.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints
                 (name TEXT, age INTEGER, mobile_number TEXT, email_id TEXT, complaint TEXT, department TEXT)''')
    c.execute("PRAGMA table_info(complaints)")
    columns = [col[1] for col in c.fetchall()]
    if 'id' not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN id INTEGER")
    if 'timestamp' not in columns:
        c.execute("ALTER TABLE complaints ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
    conn.commit()
    return conn

conn = init_db()

def store_complaint(data):
    try:
        with conn:
            conn.execute("INSERT INTO complaints (name, age, mobile_number, email_id, complaint, department) VALUES (?, ?, ?, ?, ?, ?)",
                         (data["name"], data["age"], data["mobile_number"], data["email_id"], data["complaint"], data["department"]))
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def fetch_complaints():
    c = conn.cursor()
    c.execute("SELECT COALESCE(id, rowid) AS id, name, age, mobile_number, email_id, complaint, department, COALESCE(timestamp, 'N/A') AS timestamp FROM complaints")
    return c.fetchall()

# Validation
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def is_valid_mobile(mobile):
    return re.match(r'^\d{10}$', mobile) is not None

# Enhanced styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%);
        color: #e0e0e0;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput > label, .stNumberInput > label, .stTextArea > label {
        font-weight: bold;
        color: #f39c12;
        margin-bottom: 5px;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #2c2c2c;
        color: #e0e0e0;
        border: 1px solid #f39c12;
        border-radius: 10px;
        padding: 8px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    }
    .stButton > button {
        background: linear-gradient(90deg, #f39c12, #e67e22);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        padding: 12px 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #e67e22, #d35400);
        box-shadow: 0 6px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .stMarkdown h1, .stMarkdown h2 {
        color: #f39c12;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .card {
        background-color: #2c2c2c;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    selected = option_menu("Main Menu", ["Submit Complaint", "View Complaints"],
                           icons=['pencil-fill', 'card-list'],
                           menu_icon="cast", default_index=0,
                           styles={
                               "container": {"padding": "10px", "background": "linear-gradient(135deg, #1e1e1e, #2c2c2c)"},
                               "icon": {"color": "#f39c12", "font-size": "24px"},
                               "nav-link": {"font-size": "16px", "color": "#e0e0e0", "margin": "5px 0", "--hover-color": "#f39c12"},
                               "nav-link-selected": {"background": "linear-gradient(90deg, #f39c12, #e67e22)"},
                           })

# Pages
if selected == "Submit Complaint":
    st.title("📝 Register a New Complaint")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    with st.form(key="complaint_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            name = st.text_input("Name", help="Enter your full name")
            age = st.number_input("Age", min_value=1, max_value=150, help="Enter your age")
        with col2:
            mobile_number = st.text_input("Mobile Number", help="Enter a 10-digit mobile number")
            email_id = st.text_input("Email ID", help="Enter a valid email address")
        complaint = st.text_area("Complaint Details", height=200, help="Describe your issue in detail")
        
        submit_button = st.form_submit_button(label="Submit Complaint")

    if submit_button:
        if not all([name, mobile_number, email_id, complaint]):
            st.error("Please fill all fields.")
        elif not is_valid_email(email_id):
            st.error("Invalid email address.")
        elif not is_valid_mobile(mobile_number):
            st.error("Invalid mobile number (10 digits required).")
        else:
            complaint_data = {"name": name, "age": age, "mobile_number": mobile_number, "email_id": email_id, "complaint": complaint}
            with st.spinner("Processing..."):
                progress_bar = st.progress(0)
                progress_bar.progress(25)
                department, confidence = classify_complaint_llm(complaint)
                progress_bar.progress(75)
                complaint_data["department"] = department
                
                override = st.selectbox("Override Department (optional)", [""] + DEPARTMENTS, index=DEPARTMENTS.index(department) + 1 if department in DEPARTMENTS else 0)
                if override:
                    complaint_data["department"] = override
                
                if confidence < 0.70:
                    if send_email_to_admin(complaint_data, confidence):
                        st.warning(f"Low confidence ({confidence:.2%}). Email sent for manual review.")
                    else:
                        st.warning(f"Low confidence ({confidence:.2%}). Email failed to send.")
                progress_bar.progress(100)
                
                if store_complaint(complaint_data):
                    st.success("🎉 Complaint submitted successfully!")
                    st.write(f"Department: **{complaint_data['department']}**")
                    st.write(f"Confidence: **{confidence:.2%}**")
                progress_bar.empty()
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "View Complaints":
    st.title("🔍 View Complaints")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    search_term = st.text_input("Search complaints", help="Search by name or complaint content")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Search"):
            with st.spinner("Searching..."):
                c = conn.cursor()
                c.execute("SELECT COALESCE(id, rowid) AS id, name, age, mobile_number, email_id, complaint, department, COALESCE(timestamp, 'N/A') AS timestamp FROM complaints WHERE name LIKE ? OR complaint LIKE ?", (f'%{search_term}%', f'%{search_term}%'))
                data = c.fetchall()
                if data:
                    df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Mobile", "Email", "Complaint", "Department", "Timestamp"])
                    for i, row in df.iterrows():
                        with st.expander(f"Complaint #{row['ID']} - {row['Name']}"):
                            st.write(f"**Age**: {row['Age']}")
                            st.write(f"**Mobile**: {row['Mobile']}")
                            st.write(f"**Email**: {row['Email']}")
                            st.write(f"**Complaint**: {row['Complaint']}")
                            st.write(f"**Department**: {row['Department']}")
                            st.write(f"**Timestamp**: {row['Timestamp']}")
                else:
                    st.info("No matching complaints found.")
    with col2:
        if st.button("Load All Complaints"):
            with st.spinner("Loading..."):
                data = fetch_complaints()
                if data:
                    df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Mobile", "Email", "Complaint", "Department", "Timestamp"])
                    for i, row in df.iterrows():
                        with st.expander(f"Complaint #{row['ID']} - {row['Name']}"):
                            st.write(f"**Age**: {row['Age']}")
                            st.write(f"**Mobile**: {row['Mobile']}")
                            st.write(f"**Email**: {row['Email']}")
                            st.write(f"**Complaint**: {row['Complaint']}")
                            st.write(f"**Department**: {row['Department']}")
                            st.write(f"**Timestamp**: {row['Timestamp']}")
                    csv = df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="complaints.csv">Download CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.info("No complaints found.")
    st.markdown('</div>', unsafe_allow_html=True)
