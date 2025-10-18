import os
from google_sheets import GoogleSheetsDB
from dotenv import load_dotenv

load_dotenv()

gcreds_base64 = os.getenv("GCRED_BASE64", "")
spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
db = GoogleSheetsDB(gcreds_base64, spreadsheet_id)

PATIENTS_SHEET = "Patients"
APPOINTMENTS_SHEET = "Appointments"
