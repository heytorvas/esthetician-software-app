import base64
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class GoogleSheetsDB:
    def __init__(self, base64_creds: str, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self._creds = None
        self._service = None
        self._sheet = None
        if not base64_creds:
            raise ValueError("Google credentials (base64) not provided. Set GCRED_BASE64 env variable.")
        try:
            creds_json = base64.b64decode(base64_creds).decode()
            creds_dict = json.loads(creds_json)
            self._creds = Credentials.from_service_account_info(creds_dict, scopes=[
                'https://www.googleapis.com/auth/spreadsheets'
            ])
        except Exception as e:
            raise ValueError(f"Invalid Google credentials: {e}")

    @property
    def service(self):
        if self._service is None:
            self._service = build('sheets', 'v4', credentials=self._creds)
        return self._service

    @property
    def sheet(self):
        if self._sheet is None:
            self._sheet = self.service.spreadsheets()
        return self._sheet


    def read(self, range_name: str):
        try:
            result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            return result.get('values', [])
        except Exception as e:
            raise RuntimeError(f"Failed to read from Google Sheets: {e}")


    def write(self, range_name: str, values):
        try:
            body = {'values': values}
            result = self.sheet.values().update(spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to write to Google Sheets: {e}")


    def append(self, range_name: str, values):
        try:
            body = {'values': values}
            result = self.sheet.values().append(spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to append to Google Sheets: {e}")


    def delete_row(self, sheet_name: str, row_index: int):
        try:
            requests = [{
                'deleteDimension': {
                    'range': {
                        'sheetId': self._get_sheet_id(sheet_name),
                        'dimension': 'ROWS',
                        'startIndex': row_index,
                        'endIndex': row_index + 1
                    }
                }
            }]
            body = {'requests': requests}
            return self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to delete row in Google Sheets: {e}")

    def _get_sheet_id(self, sheet_name: str):
        try:
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            raise ValueError(f'Sheet {sheet_name} not found')
        except Exception as e:
            raise RuntimeError(f"Failed to get sheet id: {e}")
