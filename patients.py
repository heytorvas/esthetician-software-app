from fastapi import APIRouter, HTTPException, Query
from uuid import UUID, uuid4
from typing import List
from datetime import datetime
from schemas import PatientSchema, PatientUpdateSchema, PatientOutSchema, AppointmentSchema, AppointmentOutSchema, ProceduresEnum, BodyFormSchema, FacialFormSchema
from constants import db, PATIENTS_SHEET, APPOINTMENTS_SHEET, RECORDS_SHEET
from commons import paginate
import json

def get_patient_by_id(patient_id: UUID):
    rows = db.read(f"{PATIENTS_SHEET}!A:B")
    for idx, row in enumerate(rows[1:], start=1):
        if UUID(row[0]) == patient_id:
            data = json.loads(row[1])
            data["id"] = UUID(row[0])
            return data, idx
    return None, None

def get_record_by_patient_id(patient_id: UUID):
    rows = db.read(f"{RECORDS_SHEET}!A:C")
    for idx, row in enumerate(rows[1:], start=1):
        if row[1] == str(patient_id):
            data = json.loads(row[2])
            return row[0], data, idx
    return None, None, None

router = APIRouter()

@router.post("/patients", response_model=PatientOutSchema)
def create_patient(payload: PatientSchema) -> PatientOutSchema:
    dt = datetime.now().isoformat()
    patient_id = uuid4()
    data = payload.model_dump()
    # Convert date fields to isoformat for JSON serialization
    if isinstance(data.get("birth_date"), datetime):
        data["birth_date"] = data["birth_date"].date().isoformat()
    elif hasattr(data.get("birth_date"), "isoformat"):
        data["birth_date"] = data["birth_date"].isoformat()
    data["created_at"] = dt
    data["updated_at"] = dt
    db.append(f"{PATIENTS_SHEET}!A:B", [[str(patient_id), json.dumps(data)]])
    return PatientOutSchema(id=patient_id, **data)

@router.get("/patients", response_model=List[PatientOutSchema])
def get_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    name: str = Query(None)
) -> List[PatientOutSchema]:
    rows = db.read(f"{PATIENTS_SHEET}!A:B")
    patients = []
    for row in rows[1:]:
        data = json.loads(row[1])
        data["id"] = UUID(row[0])
        patients.append(PatientOutSchema(**data))
    if name:
        name_lower = name.lower()
        patients = [p for p in patients if name_lower in p.name.lower()]
    patients.sort(key=lambda p: p.name)
    return paginate(patients, page, limit)

@router.get("/patients/{patient_id}", response_model=PatientOutSchema)
def get_patient(patient_id: UUID) -> PatientOutSchema:
    patient, _ = get_patient_by_id(patient_id)
    if patient:
        return PatientOutSchema(**patient)
    raise HTTPException(status_code=404, detail="Patient not found")

@router.patch("/patients/{patient_id}", response_model=PatientOutSchema)
def update_patient(patient_id: UUID, payload: PatientUpdateSchema) -> PatientOutSchema:
    patient, idx = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    data = patient.copy()
    update = payload.model_dump(exclude_unset=True)
    # Convert date fields to isoformat for JSON serialization
    if "birth_date" in update and hasattr(update["birth_date"], "isoformat"):
        update["birth_date"] = update["birth_date"].isoformat()
    data.update(update)
    if isinstance(data.get("updated_at"), datetime):
        data["updated_at"] = data["updated_at"].date().isoformat()
    elif hasattr(data.get("updated_at"), "isoformat"):
        data["updated_at"] = data["updated_at"].isoformat()
    del data["id"]
    db.write(f"{PATIENTS_SHEET}!A{idx+1}:B{idx+1}", [[str(patient_id), json.dumps(data)]])
    return PatientOutSchema(id=patient_id, **data)

@router.delete("/patients/{patient_id}")
def delete_patient(patient_id: UUID) -> dict:
    _, idx = get_patient_by_id(patient_id)
    if idx is not None:
        db.delete_row(PATIENTS_SHEET, idx)
        return {"detail": "Patient deleted"}
    raise HTTPException(status_code=404, detail="Patient not found")

@router.get("/patients/{patient_id}/appointments", response_model=list[AppointmentOutSchema])
def get_patient_appointments(patient_id: str, page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    rows = db.read(f"{APPOINTMENTS_SHEET}!A:C")
    appointments = []
    for row in rows[1:]:
        if row[1] == patient_id:
            data = json.loads(row[2])
            data["id"] = row[0]
            data["patient_id"] = row[1]
            appointments.append(AppointmentOutSchema(**data))
    appointments.sort(key=lambda a: a.created_at)
    return paginate(appointments, page, limit)

@router.post("/patients/{patient_id}/records/body")
def save_body_record(patient_id: UUID, payload: BodyFormSchema):
    rec_id, record, idx = get_record_by_patient_id(patient_id)
    if not record:
        record = {"body": None, "facial": None}
    record["body"] = payload.model_dump()
    if idx is not None:
        db.write(f"{RECORDS_SHEET}!A{idx+1}:C{idx+1}", [[rec_id, str(patient_id), json.dumps(record, ensure_ascii=False)]])
    else:
        from uuid import uuid4
        rec_id = str(uuid4())
        db.append(f"{RECORDS_SHEET}!A:C", [[rec_id, str(patient_id), json.dumps(record, ensure_ascii=False)]])
    return {"detail": "Body record saved"}

@router.post("/patients/{patient_id}/records/facial")
def save_facial_record(patient_id: UUID, payload: FacialFormSchema):
    rec_id, record, idx = get_record_by_patient_id(patient_id)
    if not record:
        record = {"body": None, "facial": None}
    record["facial"] = payload.model_dump()
    if idx is not None:
        db.write(f"{RECORDS_SHEET}!A{idx+1}:C{idx+1}", [[rec_id, str(patient_id), json.dumps(record, ensure_ascii=False)]])
    else:
        from uuid import uuid4
        rec_id = str(uuid4())
        db.append(f"{RECORDS_SHEET}!A:C", [[rec_id, str(patient_id), json.dumps(record, ensure_ascii=False)]])
    return {"detail": "Facial record saved"}

@router.get("/options/patients")
def get_patient_options():
    rows = db.read(f"{PATIENTS_SHEET}!A:B")
    options = []
    for row in rows[1:]:
        data = json.loads(row[1])
        options.append({"id": row[0], "name": data["name"]})
    return options

@router.get("/patients/{patient_id}/records")
def get_patient_records(patient_id: UUID):
    rec_id, record, idx = get_record_by_patient_id(patient_id)
    body = record.get("body") if record else None
    facial = record.get("facial") if record else None
    return {"body": body, "facial": facial}