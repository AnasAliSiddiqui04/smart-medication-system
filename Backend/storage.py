# storage.py - ENHANCED STORAGE
from datetime import datetime

patients = [
    {
        "id": 1,
        "name": "John Doe",
        "phone": "+1234567890",
        "gender": "Male",
        "email": "john@example.com",
        "dob": "1980-05-15",
        "emergency_contact": "+1234567891",
        "blood_group": "A+",
        "weight": 75.5,
        "medical_history": "Type 2 Diabetes, Hypertension",
        "allergies": "Penicillin",
        "created_at": "2024-01-15 10:30:00"
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "phone": "+1987654321",
        "gender": "Female",
        "email": "jane@example.com",
        "dob": "1975-08-22",
        "emergency_contact": "+1987654322",
        "blood_group": "O+",
        "weight": 62.0,
        "medical_history": "Asthma, Thyroid",
        "allergies": "None",
        "created_at": "2024-01-16 14:20:00"
    }
]

medications = [
    {
        "id": 1,
        "name": "Metformin",
        "patient": "John Doe",
        "dosage": "500mg",
        "pattern": "ME",
        "frequency": "Twice Daily",
        "instructions": "Take with meals",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "alarm_enabled": True,
        "alarm_time": "08:00",
        "active": True,
        "created_at": "2024-01-15 11:00:00",
        "last_updated": "2024-01-15 11:00:00"
    },
    {
        "id": 2,
        "name": "Lisinopril",
        "patient": "Jane Smith",
        "dosage": "10mg",
        "pattern": "M",
        "frequency": "Once Daily",
        "instructions": "Take in the morning on empty stomach",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "alarm_enabled": True,
        "alarm_time": "08:30",
        "active": True,
        "created_at": "2024-01-16 15:00:00",
        "last_updated": "2024-01-16 15:00:00"
    }
]