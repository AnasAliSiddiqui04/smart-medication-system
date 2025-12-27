# models.py - ENHANCED MODELS
from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class Patient(BaseModel):
    id: int
    name: str
    phone: str
    gender: str
    email: Optional[str] = None
    dob: Optional[date] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    weight: Optional[float] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    created_at: Optional[str] = None

class Medication(BaseModel):
    id: int
    name: str
    patient: str
    dosage: str
    pattern: str
    frequency: Optional[str] = "Once Daily"
    instructions: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    alarm_enabled: Optional[bool] = False
    alarm_time: Optional[str] = None
    active: bool = True
    created_at: Optional[str] = None
    last_updated: Optional[str] = None