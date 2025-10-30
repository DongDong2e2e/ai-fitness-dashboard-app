import gspread
from google.oauth2.service_account import Credentials
import os
import re
from datetime import datetime
from backend.app.config import Config

class GoogleSheetsService:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.credentials = self._get_credentials()
        self.client = gspread.authorize(self.credentials)

    def _get_credentials(self):
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            return Credentials.from_service_account_file(credentials_path, scopes=self.scope)
        else:
            service_account_info = {
                "type": Config.GCP_TYPE,
                "project_id": Config.GCP_PROJECT_ID,
                "private_key_id": Config.GCP_PRIVATE_KEY_ID,
                "private_key": Config.GCP_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": Config.GCP_CLIENT_EMAIL,
                "client_id": Config.GCP_CLIENT_ID,
                "auth_uri": Config.GCP_AUTH_URI,
                "token_uri": Config.GCP_TOKEN_URI,
                "auth_provider_x509_cert_url": Config.GCP_AUTH_PROVIDER_X509_CERT_URL,
                "client_x509_cert_url": Config.GCP_CLIENT_X509_CERT_URL,
                "universe_domain": Config.GCP_UNIVERSE_DOMAIN
            }
            return Credentials.from_service_account_info(service_account_info, scopes=self.scope)

    def open_spreadsheet(self, spreadsheet_name: str):
        return self.client.open(spreadsheet_name)

    def get_sheet_by_name(self, spreadsheet_name: str, sheet_name: str):
        spreadsheet = self.open_spreadsheet(spreadsheet_name)
        return spreadsheet.worksheet(sheet_name)

    def get_all_records(self, spreadsheet_name: str, sheet_name: str):
        sheet = self.get_sheet_by_name(spreadsheet_name, sheet_name)
        return sheet.get_all_records()

    def append_row(self, spreadsheet_name: str, sheet_name: str, row_data: list):
        sheet = self.get_sheet_by_name(spreadsheet_name, sheet_name)
        sheet.append_row(row_data)

    def update_cells(self, spreadsheet_name: str, sheet_name: str, start_row: int, start_col: int, values: list):
        sheet = self.get_sheet_by_name(spreadsheet_name, sheet_name)
        sheet.update(f'R{start_row}C{start_col}', values)

    def clear_range(self, spreadsheet_name: str, sheet_name: str, start_row: int, end_row: int, num_cols: int):
        sheet = self.get_sheet_by_name(spreadsheet_name, sheet_name)
        range_to_clear = sheet.range(start_row, 1, end_row, num_cols)
        for cell in range_to_clear:
            cell.value = ''
        sheet.update_cells(range_to_clear)

    def get_exercise_info_map(self, spreadsheet_name: str):
        mapping_sheet_name = Config.MAPPING_SHEET
        mapping_sheet = self.get_sheet_by_name(spreadsheet_name, mapping_sheet_name)
        data = mapping_sheet.get_all_values()

        if not data: # Handle empty sheet
            return {}

        info_map = {}
        # Assuming the first row is header, start from the second row
        for row in data[1:]:
            if not row or not row[0]: # Skip empty rows or rows with no exercise name
                continue
            name = row[0].strip()
            if name.startswith('**'): # Skip commented out exercises
                continue

            info_map[name] = {
                'category': row[1].strip() if len(row) > 1 and row[1] else '미분류',
                'calcMultiplier': int(row[2]) if len(row) > 2 and row[2] and row[2].isdigit() else 1,
                'tool': row[3].strip() if len(row) > 3 and row[3] else '',
                'movement': row[4].strip() if len(row) > 4 and row[4] else '',
                'target': row[5].strip() if len(row) > 5 and row[5] else ''
            }
        return info_map

    def parse_sheet_data(self, sheet, info_map, all_parsed_data):
        data = sheet.get_all_values()
        date_pattern = re.compile(r'(\d{4})[-.\s]*(\d{1,2})[-.\s]*(\d{1,2}).*')
        set_pattern = re.compile(r'^(?:(\d+)\s*세트|Warm-up)\s*(?:\((F|D)\))?:\s*([\d.]+)\s*(kg|lbs)\s*([\d.]+)\s*(?:회|reps)', re.IGNORECASE)
        set_pattern_reps_only = re.compile(r'^(?:(\d+)\s*세트|Warm-up)\s*(?:\((F|D)\))?:\s*([\d.]+)\s*(?:회|reps)', re.IGNORECASE)
        set_pattern_time = re.compile(r'^(?:(\d+)\s*세트|Warm-up)\s*(?:\((F|D)\))?:\s*([\d.]+)\s*(초|분|시간|min|sec|s)', re.IGNORECASE)
        LBS_TO_KG = 0.453592

        current_date = None
        current_exercise = None

        for row in data:
            if not row or not row[0]:
                continue
            line = str(row[0]).strip()

            if not line or "기록이 몸을 만든다" in line:
                continue

            date_match = date_pattern.match(line)
            if date_match:
                current_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                current_exercise = None
                continue

            if ':' not in line and not line[0].isdigit() and not line[0].isalpha(): # Simplified check for exercise name
                current_exercise = line.strip()
                continue

            if current_date and current_exercise:
                set_type = '본세트'
                if '(F)' in line: set_type = '실패세트'
                elif '(D)' in line: set_type = '드롭세트'
                elif 'warm-up' in line.lower(): set_type = '웜업'

                weight = 0.0
                reps_or_time = 0.0
                unit = ''
                set_num_str = '1'

                match = set_pattern.match(line)
                if match:
                    set_num_str = match.group(1) if match.group(1) else set_num_str
                    raw_weight = float(match.group(3))
                    weight_unit = match.group(4).lower()
                    weight = raw_weight * LBS_TO_KG if weight_unit == 'lbs' else raw_weight
                    reps_or_time = float(match.group(5))
                    unit = '회'
                else:
                    match = set_pattern_reps_only.match(line)
                    if match:
                        set_num_str = match.group(1) if match.group(1) else set_num_str
                        reps_or_time = float(match.group(3))
                        unit = '회'
                    else:
                        match = set_pattern_time.match(line)
                        if match:
                            set_num_str = match.group(1) if match.group(1) else set_num_str
                            reps_or_time = float(match.group(3))
                            time_unit = match.group(4).lower()
                            unit = '분' if time_unit in ['분', 'min'] else '초'
                        else:
                            continue

                set_num = 'Warm-up' if set_type == '웜업' else (set_num_str or '1')
                info = info_map.get(current_exercise, {'category': '미분류', 'calcMultiplier': 1, 'tool': '', 'movement': '', 'target': ''})

                volume = 0.0
                if unit == '회':
                    volume = weight * reps_or_time * info['calcMultiplier']

                all_parsed_data.append([current_date, current_exercise, set_type, set_num, weight, reps_or_time, unit, volume, info['category'], info['tool'], info['movement'], info['target']])

    def sync_data_to_sheet(self, spreadsheet_name: str, all_data: list):
        log_sheet_name = Config.STRUCTURED_LOG_SHEET
        log_sheet = self.get_sheet_by_name(spreadsheet_name, log_sheet_name)

        # Sort data
        all_data.sort(key=lambda x: (x[0], x[1], int(x[3]) if str(x[3]).isdigit() else 0))

        new_data_row_count = len(all_data)
        # get_all_values() includes header, so subtract 1 for actual data rows
        old_data_row_count = len(log_sheet.get_all_values()) - 1

        if new_data_row_count > 0:
            # Update from row 2 (after header)
            log_sheet.update(f'A2', all_data)

        if old_data_row_count > new_data_row_count:
            # Clear extra rows if new data is smaller
            start_row_to_clear = new_data_row_count + 2  # +1 for 1-based index, +1 for header
            num_rows_to_clear = old_data_row_count - new_data_row_count
            # Assuming max columns is 12 based on the header in Code.gs
            self.clear_range(spreadsheet_name, log_sheet_name, start_row_to_clear, start_row_to_clear + num_rows_to_clear - 1, 12)

    def update_structured_log_sheet(self, spreadsheet_name: str):
        try:
            info_map = self.get_exercise_info_map(spreadsheet_name)
            spreadsheet = self.open_spreadsheet(spreadsheet_name)
            
            target_sheets = [s for s in spreadsheet.worksheets() if s.title.startswith(Config.RAW_DATA_SHEET_PREFIX)]

            if not target_sheets:
                print("No raw data sheets found.")
                return

            all_parsed_data = []
            for sheet in target_sheets:
                self.parse_sheet_data(sheet, info_map, all_parsed_data)
            
            self.sync_data_to_sheet(spreadsheet_name, all_parsed_data)
            print("데이터 변환 및 동기화 완료.")
        except Exception as e:
            print(f"파싱/동기화 오류: {e}")
