# streamlit_app.py - ENHANCED VERSION
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
import time as tm
from streamlit_autorefresh import st_autorefresh

# ======================
# PAGE CONFIGURATION
# ======================
st.set_page_config(
    page_title="Smart Medication System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 30 seconds for notifications
st_autorefresh(interval=30000, key="notification_refresh")

# ======================
# CUSTOM CSS (Enhanced)
# ======================
st.markdown("""
<style>
    /* Main containers */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 5px solid #667eea;
    }
    
    .notification-card {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
    }
    
    /* Patient form styling */
    .patient-form {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #4a6491 100%);
    }
    
    /* Pattern validation */
    .pattern-valid { 
        color: #28a745; 
        font-weight: bold;
        background: #d4edda;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .pattern-invalid { 
        color: #dc3545; 
        font-weight: bold;
        background: #f8d7da;
        padding: 0.5rem;
        border-radius: 5px;
    }
    
    /* Alarm styling */
    .alarm-active {
        color: #dc3545;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE INITIALIZATION
# ======================
if 'patients' not in st.session_state:
    st.session_state.patients = []
if 'medications' not in st.session_state:
    st.session_state.medications = []
if 'show_patient_form' not in st.session_state:
    st.session_state.show_patient_form = False
if 'show_med_form' not in st.session_state:
    st.session_state.show_med_form = False
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'alarm_time' not in st.session_state:
    st.session_state.alarm_time = None

# ======================
# NOTIFICATION SYSTEM
# ======================
def check_medication_time():
    """Check current time against medication schedule"""
    current_time = datetime.now().strftime("%H:%M")
    notifications = []
    
    # Common medication times
    medication_times = {
        "08:00": "🌅 Morning Medication Time (8:00 AM)",
        "12:00": "☀️ Noon Medication Time (12:00 PM)",
        "20:00": "🌇 Evening Medication Time (8:00 PM)",
    }
    
    # Check if current time matches any medication time
    for med_time, message in medication_times.items():
        if current_time == med_time:
            notifications.append({
                "type": "warning",
                "message": f"⏰ {message} - Please take your medications!",
                "time": current_time
            })
    
    return notifications

def ring_alarm():
    """Simulate alarm ringing"""
    alarm_html = """
    <div class="card notification-card">
        <h3 style='color: #dc3545;'>🔔 MEDICATION ALARM!</h3>
        <p>It's time to take your medication!</p>
        <audio controls autoplay>
            <source src="https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3" type="audio/mpeg">
        </audio>
        <button onclick="document.querySelector('audio').pause();" 
                style="background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 5px; margin-top: 10px;">
            ⏰ Snooze for 10 minutes
        </button>
    </div>
    """
    return alarm_html

# ======================
# SIDEBAR NAVIGATION
# ======================
with st.sidebar:
    st.markdown("<h1 style='color: white;'>🏥 MedCare</h1>", unsafe_allow_html=True)
    
    # Backend connection status
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    st.markdown("---")
    
    # Navigation
    menu = st.radio(
        "📱 Navigation",
        ["🏠 Dashboard", "👤 Add Patient", "💊 Add Medication", "📅 View Schedule", 
         "🔔 Notifications", "⚙️ Settings", "🧠 DFA Pattern Tester"],
        key="main_menu"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Patients", len(st.session_state.patients))
    with col2:
        st.metric("Meds", len(st.session_state.medications))
    
    st.markdown("---")
    
    # Quick Actions
    if st.button("🆕 Add New Patient", use_container_width=True):
        st.session_state.show_patient_form = True
        menu = "👤 Add Patient"
        st.rerun()
    
    if st.button("➕ Add Medication", use_container_width=True):
        st.session_state.show_med_form = True
        menu = "💊 Add Medication"
        st.rerun()
    
    if st.button("🔔 Test Alarm", use_container_width=True):
        st.session_state.alarm_time = datetime.now()
        st.rerun()

# ======================
# MAIN HEADER
# ======================
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
col_title1, col_title2 = st.columns([3, 1])
with col_title1:
    st.markdown("<h1 style='margin: 0; color: white;'>💊 Smart Medication System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(255,255,255,0.8);'>Automata-Powered Medication Management with Notifications</p>", unsafe_allow_html=True)
with col_title2:
    current_time = datetime.now().strftime("%I:%M %p")
    st.markdown(f"<div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 10px; text-align: center;'>"
                f"<h3 style='margin: 0; color: white;'>🕒 {current_time}</h3></div>", 
                unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ======================
# NOTIFICATION DISPLAY AREA
# ======================
notifications = check_medication_time()
if notifications or st.session_state.alarm_time:
    with st.container():
        st.markdown("### 🔔 Active Notifications")
        
        # Show medication time notifications
        for notif in notifications:
            st.warning(notif["message"])
        
        # Show alarm if triggered
        if st.session_state.alarm_time:
            st.markdown(ring_alarm(), unsafe_allow_html=True)
            if st.button("✅ Dismiss Alarm", key="dismiss_alarm"):
                st.session_state.alarm_time = None
                st.rerun()

# ======================
# DASHBOARD PAGE
# ======================
if menu == "🏠 Dashboard":
    st.markdown("<h2>📊 Dashboard Overview</h2>", unsafe_allow_html=True)
    
    # Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 👥 Total Patients")
        st.markdown(f"<h1 style='text-align: center; color: #667eea;'>{len(st.session_state.patients)}</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 💊 Active Medications")
        active_meds = len([m for m in st.session_state.medications if m.get('active', True)])
        st.markdown(f"<h1 style='text-align: center; color: #28a745;'>{active_meds}</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ⏰ Next Medication")
        try:
            schedule = requests.get("http://localhost:8000/api/schedule/today", timeout=3).json()
            if schedule:
                next_med = schedule[0]
                st.markdown(f"<h3 style='color: #dc3545;'>{next_med.get('medication', 'None')}</h3>", unsafe_allow_html=True)
                st.markdown(f"**Time:** {next_med.get('time', 'N/A')}")
            else:
                st.info("No medications scheduled")
        except:
            st.info("Schedule not available")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Actions Row
    st.markdown("### ⚡ Quick Actions")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    
    with qcol1:
        if st.button("👤 Add Patient", use_container_width=True, key="dash_add_patient"):
            st.session_state.show_patient_form = True
            menu = "👤 Add Patient"
            st.rerun()
    
    with qcol2:
        if st.button("💊 Add Medication", use_container_width=True, key="dash_add_med"):
            st.session_state.show_med_form = True
            menu = "💊 Add Medication"
            st.rerun()
    
    with qcol3:
        if st.button("📅 View Schedule", use_container_width=True, key="dash_view_sched"):
            menu = "📅 View Schedule"
            st.rerun()
    
    with qcol4:
        if st.button("🔔 Test Alarm", use_container_width=True, key="dash_test_alarm"):
            st.session_state.alarm_time = datetime.now()
            st.rerun()
    
    # Recent Medications
    st.markdown("### 📋 Recent Medications")
    if st.session_state.medications:
        meds_df = pd.DataFrame(st.session_state.medications)
        st.dataframe(meds_df[['name', 'patient', 'dosage', 'pattern']], 
                    use_container_width=True, hide_index=True)
    else:
        st.info("No medications added yet")

# ======================
# ADD PATIENT PAGE (Interactive Form)
# ======================
elif menu == "👤 Add Patient":
    st.markdown("<h2>👤 Add New Patient</h2>", unsafe_allow_html=True)
    
    # Interactive form in tabs
    tab1, tab2 = st.tabs(["📝 Patient Form", "👁️ Preview"])
    
    with tab1:
        st.markdown("<div class='patient-form'>", unsafe_allow_html=True)
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="John Doe", help="Enter patient's full name")
                gender = st.selectbox("Gender *", ["Select", "Male", "Female", "Other"])
                phone = st.text_input("Phone Number *", placeholder="+1234567890")
                dob = st.date_input("Date of Birth", datetime.now())
            
            with col2:
                email = st.text_input("Email", placeholder="john@example.com")
                emergency_contact = st.text_input("Emergency Contact", placeholder="+1234567890")
                blood_group = st.selectbox("Blood Group", ["Select", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
            
            # Medical Information
            st.markdown("### 🏥 Medical Information")
            medical_history = st.text_area("Medical History", 
                                          placeholder="e.g., Diabetes Type 2, Hypertension...",
                                          height=100)
            
            allergies = st.text_input("Allergies", placeholder="e.g., Penicillin, Nuts...")
            
            # Form submission
            submitted = st.form_submit_button("💾 Save Patient", type="primary", use_container_width=True)
            
            if submitted:
                if not name or gender == "Select" or not phone:
                    st.error("Please fill in all required fields (*)")
                else:
                    new_patient = {
                        "id": len(st.session_state.patients) + 1,
                        "name": name,
                        "gender": gender,
                        "phone": phone,
                        "email": email,
                        "dob": dob.strftime("%Y-%m-%d"),
                        "emergency_contact": emergency_contact,
                        "blood_group": blood_group,
                        "weight": weight,
                        "medical_history": medical_history,
                        "allergies": allergies,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    try:
                        response = requests.post(
                            "http://localhost:8000/patients",
                            json=new_patient,
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.session_state.patients.append(new_patient)
                            st.success(f"✅ Patient '{name}' added successfully!")
                            st.balloons()
                            
                            # Show notification
                            st.session_state.notifications.append({
                                "type": "success",
                                "message": f"New patient '{name}' added to system",
                                "time": datetime.now().strftime("%H:%M")
                            })
                            
                            # Reset form
                            st.rerun()
                    except:
                        # Save locally
                        st.session_state.patients.append(new_patient)
                        st.success(f"✅ Patient '{name}' saved locally!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 👁️ Patient Preview")
        if 'name' in locals() and name:
            st.info(f"**Name:** {name}")
            st.info(f"**Gender:** {gender}")
            st.info(f"**Phone:** {phone}")
            if email:
                st.info(f"**Email:** {email}")
        else:
            st.info("Fill the form to see preview")

# ======================
# ADD MEDICATION PAGE
# ======================
elif menu == "💊 Add Medication":
    st.markdown("<h2>💊 Add Medication with DFA Pattern</h2>", unsafe_allow_html=True)
    
    with st.form("medication_form"):
        # Form in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Medication Details")
            med_name = st.text_input("Medication Name *", placeholder="Metformin")
            patient = st.selectbox("Select Patient *", 
                                 ["Select"] + [p.get('name', '') for p in st.session_state.patients])
            dosage = st.text_input("Dosage *", placeholder="500mg")
            frequency = st.selectbox("Frequency", ["Once Daily", "Twice Daily", "Thrice Daily", "As Needed"])
            start_date = st.date_input("Start Date", datetime.now())
            end_date = st.date_input("End Date", datetime.now())
            
            # Alarm settings
            st.markdown("### 🔔 Alarm Settings")
            enable_alarm = st.checkbox("Enable Medication Alarm", value=True)
            if enable_alarm:
                alarm_time = st.time_input("Alarm Time", time(8, 0))
        
        with col2:
            st.markdown("### 🧠 DFA Pattern Input")
            pattern = st.text_input(
                "Enter Pattern Sequence *",
                placeholder="e.g., ME (Morning+Evening), T (Twice Daily), MXE (Morning+Skip+Evening)",
                help="M=Morning (8 AM), E=Evening (8 PM), T=Twice Daily (8 AM & 8 PM), X=Skip"
            )
            
            # Real-time pattern validation
            if pattern:
                pattern_upper = pattern.upper()
                if all(c in "METX" for c in pattern_upper) and len(pattern_upper) > 0:
                    st.markdown(f"<div class='pattern-valid'>✅ VALID PATTERN: '{pattern}'</div>", unsafe_allow_html=True)
                    
                    # Show schedule visualization
                    st.markdown("#### 📅 Schedule Preview:")
                    schedule_map = {"M": "🌅 8:00 AM - Morning", "E": "🌇 8:00 PM - Evening", 
                                  "T": "🔄 8:00 AM & 8:00 PM - Twice Daily", "X": "⏭️ Skip"}
                    
                    for i, char in enumerate(pattern_upper):
                        if char in schedule_map:
                            st.write(f"{i+1}. {schedule_map[char]}")
                else:
                    invalid_chars = [c for c in pattern_upper if c not in "METX"]
                    if invalid_chars:
                        st.markdown(f"<div class='pattern-invalid'>❌ INVALID: Characters {', '.join(invalid_chars)} not allowed</div>", 
                                  unsafe_allow_html=True)
                    else:
                        st.warning("Pattern cannot be empty")
            
            # Special Instructions
            st.markdown("### 📝 Special Instructions")
            instructions = st.text_area(
                "Instructions",
                placeholder="Take with food. Avoid alcohol. Store at room temperature...",
                height=100
            )
        
        # Form submission
        submitted = st.form_submit_button("💾 Save Medication", type="primary", use_container_width=True)
        
        if submitted:
            if not med_name or patient == "Select" or not dosage or not pattern:
                st.error("Please fill all required fields (*)")
            elif not all(c in "METX" for c in pattern.upper()):
                st.error("Invalid pattern! Use only M, E, T, X")
            else:
                new_med = {
                    "id": len(st.session_state.medications) + 1,
                    "name": med_name,
                    "patient": patient,
                    "dosage": dosage,
                    "frequency": frequency,
                    "pattern": pattern.upper(),
                    "instructions": instructions,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "alarm_enabled": enable_alarm,
                    "alarm_time": alarm_time.strftime("%H:%M") if enable_alarm else None,
                    "active": True
                }
                
                try:
                    response = requests.post(
                        "http://localhost:8000/medications",
                        json=new_med,
                        timeout=5
                    )
                    if response.status_code == 200:
                        st.session_state.medications.append(new_med)
                        st.success(f"✅ Medication '{med_name}' added for {patient}!")
                        st.balloons()
                        
                        # Show alarm notification
                        if enable_alarm:
                            st.info(f"🔔 Alarm set for {alarm_time.strftime('%I:%M %p')}")
                except:
                    st.session_state.medications.append(new_med)
                    st.success(f"✅ Medication '{med_name}' saved locally!")

# ======================
# VIEW SCHEDULE PAGE
# ======================
elif menu == "📅 View Schedule":
    st.markdown("<h2>📅 Medication Schedule</h2>", unsafe_allow_html=True)
    
    # Date selector
    col_date1, col_date2 = st.columns([3, 1])
    with col_date1:
        selected_date = st.date_input("Select Date", datetime.now())
    with col_date2:
        if st.button("🔄 Refresh Schedule", use_container_width=True):
            st.rerun()
    
    # Fetch schedule
    try:
        schedule_response = requests.get("http://localhost:8000/api/schedule/today", timeout=5)
        if schedule_response.status_code == 200:
            schedule_data = schedule_response.json()
        else:
            schedule_data = []
    except:
        schedule_data = []
    
    # Display in time slots
    col1, col2, col3 = st.columns(3)
    
    time_slots = {
        "Morning (6 AM - 12 PM)": ["08:00 AM"],
        "Afternoon (12 PM - 5 PM)": ["12:00 PM", "02:00 PM"],
        "Evening (5 PM - 10 PM)": ["08:00 PM"]
    }
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 🌅 Morning Medications")
        morning_meds = [m for m in schedule_data if any(time in str(m.get("time", "")) for time in time_slots["Morning (6 AM - 12 PM)"])]
        if morning_meds:
            for med in morning_meds:
                with st.expander(f"💊 {med.get('medication', 'Unknown')}"):
                    st.markdown(f"**Patient:** {med.get('patient', 'Unknown')}")
                    st.markdown(f"**Dosage:** {med.get('dosage', 'N/A')}")
                    st.markdown(f"**Time:** {med.get('time', 'N/A')}")
                    if st.button("✅ Mark as Taken", key=f"morning_{med.get('medication')}"):
                        st.success(f"Marked {med.get('medication')} as taken!")
        else:
            st.info("No morning medications")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### ☀️ Afternoon Medications")
        afternoon_meds = [m for m in schedule_data if any(time in str(m.get("time", "")) for time in time_slots["Afternoon (12 PM - 5 PM)"])]
        if afternoon_meds:
            for med in afternoon_meds:
                with st.expander(f"💊 {med.get('medication', 'Unknown')}"):
                    st.markdown(f"**Patient:** {med.get('patient', 'Unknown')}")
                    st.markdown(f"**Dosage:** {med.get('dosage', 'N/A')}")
                    st.markdown(f"**Time:** {med.get('time', 'N/A')}")
                    if st.button("✅ Mark as Taken", key=f"afternoon_{med.get('medication')}"):
                        st.success(f"Marked {med.get('medication')} as taken!")
        else:
            st.info("No afternoon medications")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 🌇 Evening Medications")
        evening_meds = [m for m in schedule_data if any(time in str(m.get("time", "")) for time in time_slots["Evening (5 PM - 10 PM)"])]
        if evening_meds:
            for med in evening_meds:
                with st.expander(f"💊 {med.get('medication', 'Unknown')}"):
                    st.markdown(f"**Patient:** {med.get('patient', 'Unknown')}")
                    st.markdown(f"**Dosage:** {med.get('dosage', 'N/A')}")
                    st.markdown(f"**Time:** {med.get('time', 'N/A')}")
                    if st.button("✅ Mark as Taken", key=f"evening_{med.get('medication')}"):
                        st.success(f"Marked {med.get('medication')} as taken!")
        else:
            st.info("No evening medications")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Detailed schedule table
    if schedule_data:
        st.markdown("### 📋 Detailed Schedule Table")
        df = pd.DataFrame(schedule_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ======================
# NOTIFICATIONS PAGE
# ======================
elif menu == "🔔 Notifications":
    st.markdown("<h2>🔔 Medication Notifications & Alarms</h2>", unsafe_allow_html=True)
    
    # Notification Settings
    with st.expander("⚙️ Notification Settings", expanded=True):
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            enable_notifications = st.checkbox("Enable Notifications", value=True)
            enable_sound = st.checkbox("Enable Sound Alarms", value=True)
            notification_time = st.number_input("Notification Minutes Before", 
                                              min_value=0, max_value=60, value=5)
        with col_set2:
            repeat_alarm = st.checkbox("Repeat Alarm if Missed", value=True)
            snooze_duration = st.selectbox("Snooze Duration", 
                                         ["5 minutes", "10 minutes", "15 minutes", "30 minutes"])
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("Notification settings saved!")
    
    # Active Alarms
    st.markdown("### ⏰ Active Medication Alarms")
    
    # Simulated alarms based on medications
    if st.session_state.medications:
        for med in st.session_state.medications:
            if med.get('alarm_enabled'):
                col_alarm1, col_alarm2, col_alarm3 = st.columns([2, 1, 1])
                with col_alarm1:
                    st.markdown(f"**{med.get('name')}** for {med.get('patient')}")
                    st.markdown(f"⏰ Alarm: {med.get('alarm_time', 'Not set')}")
                with col_alarm2:
                    if st.button("🔕 Snooze", key=f"snooze_{med.get('id')}"):
                        st.info(f"Snoozed {med.get('name')} for {snooze_duration}")
                with col_alarm3:
                    if st.button("✅ Taken", key=f"taken_{med.get('id')}"):
                        st.success(f"Marked {med.get('name')} as taken!")
    
    # Test Alarm Section
    st.markdown("### 🔧 Test Alarm System")
    test_time = st.time_input("Set Test Alarm Time", datetime.now().time())
    if st.button("🔔 Test Alarm Now", use_container_width=True):
        st.session_state.alarm_time = datetime.now()
        st.rerun()

# ======================
# SETTINGS PAGE
# ======================
elif menu == "⚙️ Settings":
    st.markdown("<h2>⚙️ System Settings</h2>", unsafe_allow_html=True)
    
    tabs = st.tabs(["General", "DFA Settings", "Backup", "About"])
    
    with tabs[0]:
        st.markdown("### General Settings")
        system_name = st.text_input("System Name", "Smart Medication System")
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "IST", "CET"])
        language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
        
        if st.button("Save General Settings", use_container_width=True):
            st.success("General settings saved!")
    
    with tabs[1]:
        st.markdown("### 🧠 DFA Pattern Settings")
        st.markdown("""
        **Current DFA Alphabet:** M, E, T, X
        
        **Meanings:**
        - **M** = Morning (Default: 8:00 AM)
        - **E** = Evening (Default: 8:00 PM)
        - **T** = Twice Daily (Default: 8:00 AM & 8:00 PM)
        - **X** = Skip/No Medication
        
        **Validation Rules:**
        1. Only characters M, E, T, X are allowed
        2. Empty patterns are invalid
        3. Case insensitive (M = m, E = e, etc.)
        """)
        
        # Custom time settings
        morning_time = st.time_input("Morning Time", time(8, 0))
        evening_time = st.time_input("Evening Time", time(20, 0))
        
        if st.button("Update DFA Times", use_container_width=True):
            st.success("DFA time settings updated!")
    
    with tabs[2]:
        st.markdown("### 💾 Backup & Restore")
        if st.button("📥 Backup Data", use_container_width=True):
            st.success("Data backup created!")
        
        uploaded_file = st.file_uploader("Restore from backup", type=['json'])
        if uploaded_file:
            st.success("Backup file loaded!")
    
    with tabs[3]:
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Smart Medication System v2.0**
        
        **Features:**
        - 🧠 DFA Pattern Validation (M, E, T, X)
        - ⏰ Smart Medication Scheduling
        - 🔔 Notification & Alarm System
        - 📱 Interactive Patient Management
        - 📊 Real-time Dashboard
        
        **Technology Stack:**
        - Backend: FastAPI + Python
        - Frontend: Streamlit
        - DFA Engine: Custom Automata Logic
        
        **Developed for:** Automata Theory Project
        """)

# ======================
# DFA PATTERN TESTER
# ======================
elif menu == "🧠 DFA Pattern Tester":
    st.markdown("<h2>🧠 DFA Pattern Tester & Validator</h2>", unsafe_allow_html=True)
    
    col_test1, col_test2 = st.columns([2, 1])
    
    with col_test1:
        pattern_input = st.text_area(
            "Enter Pattern(s) to Validate",
            placeholder="Enter one pattern per line\nExample:\nME\nMET\nMXE\nT\nA  # Invalid\nME1  # Invalid",
            height=200
        )
        
        if st.button("🔍 Validate Patterns", use_container_width=True):
            if pattern_input:
                patterns = [p.strip() for p in pattern_input.split('\n') if p.strip()]
                results = []
                
                for pattern in patterns:
                    try:
                        response = requests.get(f"http://localhost:8000/validate-pattern/{pattern}", timeout=3)
                        if response.status_code == 200:
                            result = response.json()
                            results.append({
                                "Pattern": pattern,
                                "Status": "✅ Valid" if result.get("valid") else "❌ Invalid",
                                "Meaning": ", ".join(result.get("meaning", [])) if result.get("valid") else result.get("message", "Error")
                            })
                    except:
                        # Local validation
                        pattern_upper = pattern.upper()
                        if all(c in "METX" for c in pattern_upper) and len(pattern_upper) > 0:
                            meaning_map = {"M": "Morning", "E": "Evening", "T": "Twice Daily", "X": "Skip"}
                            meaning = [meaning_map.get(c, "Unknown") for c in pattern_upper]
                            results.append({
                                "Pattern": pattern,
                                "Status": "✅ Valid",
                                "Meaning": " → ".join(meaning)
                            })
                        else:
                            results.append({
                                "Pattern": pattern,
                                "Status": "❌ Invalid",
                                "Meaning": "Invalid characters or empty pattern"
                            })
                
                if results:
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    with col_test2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🧪 Quick Tests")
        
        test_cases = [
            ("M", "Morning only"),
            ("ME", "Morning + Evening"),
            ("MET", "Morning + Evening + Twice"),
            ("MXE", "Morning + Skip + Evening"),
            ("T", "Twice Daily only"),
            ("MMEE", "Multiple Mornings & Evenings"),
            ("A", "❌ Invalid (A)"),
            ("ME1", "❌ Invalid (1)"),
            ("", "❌ Empty")
        ]
        
        for pattern, desc in test_cases:
            if st.button(f"Test: '{pattern}'", key=f"quick_{pattern}", use_container_width=True):
                st.session_state.test_pattern = pattern
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # DFA State Diagram
        st.markdown("### 🔄 DFA State Diagram")
        st.markdown("""
        ```
        Start → [Read Character]
                ↓
        [Check if char in {M,E,T,X}]
                ↓
        [Valid] → [Accept] → [Next Character]
                ↓
        [Invalid] → [Reject]
        ```
        """)

# ======================
# FOOTER
# ======================
st.markdown("---")
col_foot1, col_foot2 = st.columns([2, 1])
with col_foot1:
    st.markdown("<small>💊 Smart Medication System | 🧠 DFA Automata Project | ⏰ v2.0</small>", unsafe_allow_html=True)
with col_foot2:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"<small align='right'>Last updated: {current_time}</small>", unsafe_allow_html=True)