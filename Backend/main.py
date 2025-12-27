# main.py - ENHANCED BACKEND
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time
from models import Patient, Medication
from storage import patients, medications
from automata import validate_pattern, pattern_meaning

app = FastAPI(
    title="Smart Medication System API",
    version="2.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# ROOT ENDPOINT
# =====================
@app.get("/")
def home():
    return {
        "message": "Smart Medication System API",
        "status": "running",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }

# =====================
# DFA PATTERN VALIDATION
# =====================
@app.get("/validate-pattern/{pattern}")
def validate(pattern: str):
    """Enhanced DFA Pattern Validation"""
    if validate_pattern(pattern):
        meaning = pattern_meaning(pattern)
        return {
            "pattern": pattern,
            "valid": True,
            "meaning": meaning,
            "schedule_count": len(meaning),
            "has_skip": "X" in pattern.upper(),
            "message": f"Pattern '{pattern}' is valid"
        }
    return {
        "pattern": pattern,
        "valid": False,
        "message": f"Pattern '{pattern}' is invalid. Use only M (Morning), E (Evening), T (Twice Daily), X (Skip)"
    }

# =====================
# PATIENT MANAGEMENT
# =====================
@app.post("/patients")
def add_patient(patient: Patient):
    patients.append(patient.dict())
    return {
        "status": "success",
        "message": f"Patient '{patient.name}' added",
        "patient_id": patient.id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/patients")
def get_patients():
    return patients

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    for patient in patients:
        if patient["id"] == patient_id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")

# =====================
# MEDICATION MANAGEMENT
# =====================
@app.post("/medications")
def add_medication(med: Medication):
    """Add medication with DFA pattern validation"""
    if not validate_pattern(med.pattern):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid DFA pattern '{med.pattern}'. Only M, E, T, X allowed."
        )
    
    # Add created timestamp
    med_dict = med.dict()
    med_dict["created_at"] = datetime.now().isoformat()
    med_dict["last_updated"] = datetime.now().isoformat()
    
    medications.append(med_dict)
    
    # Generate schedule for the medication
    schedule_items = []
    for char in med.pattern.upper():
        if char == "M":
            schedule_items.append({
                "time": "08:00 AM",
                "type": "Morning",
                "char": "M"
            })
        elif char == "E":
            schedule_items.append({
                "time": "08:00 PM",
                "type": "Evening",
                "char": "E"
            })
        elif char == "T":
            schedule_items.append({
                "time": "08:00 AM & 08:00 PM",
                "type": "Twice Daily",
                "char": "T"
            })
    
    return {
        "status": "success",
        "message": f"Medication '{med.name}' added",
        "medication": med_dict,
        "schedule": schedule_items,
        "pattern_analysis": {
            "length": len(med.pattern),
            "morning_count": med.pattern.upper().count("M"),
            "evening_count": med.pattern.upper().count("E"),
            "twice_count": med.pattern.upper().count("T"),
            "skip_count": med.pattern.upper().count("X")
        }
    }

@app.get("/medications")
def get_medications():
    return medications

@app.get("/medications/active")
def get_active_medications():
    return [m for m in medications if m.get("active", True)]

# =====================
# ENHANCED SCHEDULE GENERATION
# =====================
@app.get("/api/schedule/today")
def get_today_schedule():
    """Generate today's schedule from DFA patterns"""
    schedule = []
    
    for med in medications:
        if not med.get("active", True):
            continue
            
        pattern = med.get("pattern", "M")
        med_name = med.get("name", "Unknown")
        patient = med.get("patient", "Unknown")
        dosage = med.get("dosage", "N/A")
        
        # Generate schedule based on DFA pattern
        for char in pattern.upper():
            if char == "M":
                schedule.append({
                    "time": "08:00 AM",
                    "medication": med_name,
                    "patient": patient,
                    "dosage": dosage,
                    "pattern_char": "M",
                    "pattern_type": "Morning",
                    "medication_id": med.get("id"),
                    "status": "pending",
                    "alarm_time": med.get("alarm_time", "08:00")
                })
            elif char == "E":
                schedule.append({
                    "time": "08:00 PM",
                    "medication": med_name,
                    "patient": patient,
                    "dosage": dosage,
                    "pattern_char": "E",
                    "pattern_type": "Evening",
                    "medication_id": med.get("id"),
                    "status": "pending",
                    "alarm_time": med.get("alarm_time", "20:00")
                })
            elif char == "T":
                # Add both morning and evening for Twice Daily
                schedule.append({
                    "time": "08:00 AM",
                    "medication": med_name,
                    "patient": patient,
                    "dosage": dosage,
                    "pattern_char": "T",
                    "pattern_type": "Twice Daily (AM)",
                    "medication_id": med.get("id"),
                    "status": "pending",
                    "alarm_time": med.get("alarm_time", "08:00")
                })
                schedule.append({
                    "time": "08:00 PM",
                    "medication": med_name,
                    "patient": patient,
                    "dosage": dosage,
                    "pattern_char": "T",
                    "pattern_type": "Twice Daily (PM)",
                    "medication_id": med.get("id"),
                    "status": "pending",
                    "alarm_time": med.get("alarm_time", "20:00")
                })
            # X means skip - no schedule item
    
    # Sort schedule by time
    time_order = {"08:00 AM": 1, "12:00 PM": 2, "02:00 PM": 3, "08:00 PM": 4}
    schedule.sort(key=lambda x: time_order.get(x["time"], 99))
    
    return schedule

# =====================
# NOTIFICATION ENDPOINTS
# =====================
@app.get("/api/notifications/check")
def check_notifications():
    """Check for pending notifications"""
    current_time = datetime.now()
    notifications = []
    
    for med in medications:
        if med.get("alarm_enabled") and med.get("alarm_time"):
            try:
                alarm_time = datetime.strptime(med.get("alarm_time"), "%H:%M").time()
                if (current_time.hour == alarm_time.hour and 
                    current_time.minute == alarm_time.minute):
                    notifications.append({
                        "type": "medication_alarm",
                        "medication": med.get("name"),
                        "patient": med.get("patient"),
                        "dosage": med.get("dosage"),
                        "time": med.get("alarm_time"),
                        "message": f"Time to take {med.get('name')} ({med.get('dosage')})"
                    })
            except:
                pass
    
    return {
        "has_notifications": len(notifications) > 0,
        "notifications": notifications,
        "count": len(notifications),
        "timestamp": current_time.isoformat()
    }

@app.post("/api/medications/{med_id}/mark-taken")
def mark_medication_taken(med_id: int):
    """Mark medication as taken"""
    for med in medications:
        if med["id"] == med_id:
            med["last_taken"] = datetime.now().isoformat()
            med["taken_count"] = med.get("taken_count", 0) + 1
            return {
                "status": "success",
                "message": f"Medication '{med['name']}' marked as taken",
                "last_taken": med["last_taken"]
            }
    raise HTTPException(status_code=404, detail="Medication not found")

# =====================
# SYSTEM STATISTICS
# =====================
@app.get("/api/stats")
def get_system_stats():
    """Get system statistics"""
    total_patients = len(patients)
    total_medications = len(medications)
    active_medications = len([m for m in medications if m.get("active", True)])
    
    # Pattern statistics
    pattern_stats = {}
    for med in medications:
        pattern = med.get("pattern", "")
        for char in pattern.upper():
            if char in pattern_stats:
                pattern_stats[char] += 1
            else:
                pattern_stats[char] = 1
    
    return {
        "total_patients": total_patients,
        "total_medications": total_medications,
        "active_medications": active_medications,
        "pattern_statistics": pattern_stats,
        "system_uptime": datetime.now().isoformat()
    }