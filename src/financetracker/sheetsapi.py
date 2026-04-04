import os,json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SPREADSHEET_ID = "1rSx6kLYIh-_Y8iDSpAZntyBPZxtYS_r7922F47TTb5o"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/spreadsheets.readonly"]





# TODO: make this into a class so it's easier to retrieve attributes of the sheet without having to send request
class FinanceSheet:
    def __init__(self, name):
        self.name = name
        self.client = self.new_client()
        self.sheet_rows = self.get_sheet(self.client, self.name)
        self.sheet_cols = self.sheet_rows[0]
        self.sheet_data_rows = self.sheet_rows[1:]
        self.sheet_json = {}
        self.categories = set()
        self._refresh_sheet()

    def new_client(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
            try:
                client = build("sheets", "v4", credentials=creds)
                return client
            except HttpError as err:
                print(err)
        return client

    def get_data(self):
        sheet_path = f'sheets/{self.name}.json'
        if os.path.exists(sheet_path):
            with open(sheet_path, 'r') as f:
                contents = f.read()
            return json.loads(contents)
        self._refresh_sheet()
        self.get_data()
            

    def get_sheet(self, client, sheet_name):
        try:
            sheet = client.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!A:D")
                .execute()
            )
            values = result.get("values", [])
            if not values:
                print("No data found.")
                return
            return values

        except HttpError as err:
            print(err)

    def sheet_to_obj(self):
        objs = []
        for row in self.sheet_data_rows:
            obj = {
                self.sheet_cols[0]: str(row[0]),
                self.sheet_cols[1]: float(row[1]),
                self.sheet_cols[2]: str(row[2]),
                self.sheet_cols[3]: str(row[3]),
            }
            objs.append(obj)
        return objs
        
    def add_row(self, data):
        body = {
            'values': [data]
        }
        target_row = len(self.sheet_rows)
        target_range = f"{self.name}!A{target_row+1}:D{target_row+1}"
        sheet = self.client.spreadsheets()
        try:
            result = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=target_range,
                valueInputOption='USER_ENTERED', # Renders values as if they were entered by a user
                body=body
            ).execute()

            assert result['updates']['updatedRange'] == target_range, 'warning: unexpected update range in response'
            self._refresh_sheet()
            return 1
        except HttpError as err:
            print(err)
            return 0
    
    def write_sheet_to_file(self, sheet_data, sheet_name):
        sheet_path = f'sheets/{sheet_name}.json'
        if os.path.exists(sheet_path):
            os.remove(sheet_path)
        with open(sheet_path, 'w') as f:
            json.dump(sheet_data, f, indent=4)
    
    def validate_data(self, cols, rows):
        validated_data = []
        for i in range(len(rows)):
            if len(rows[i]) != len(cols):
                print(f"row {i+2} is missing data - please review")
                continue
            cleaned = []
            data_row = rows[i]
            for k in range(len(data_row)):
                if k == 0:
                    cleaned.append(str(data_row[0]))
                elif k == 1:
                    cleaned.append(float(data_row[1]))
                elif k == 2:
                    cleaned.append(str(data_row[2]))
                elif k == 3:
                    cleaned.append(str(data_row[3]))
            validated_data.append(cleaned)
    
        return validated_data

    def _refresh_sheet(self):
        try:
            
            self.sheet_rows = self.get_sheet(self.client, self.name)
            self.sheet_data_rows = self.validate_data(self.sheet_cols, self.sheet_rows[1:])
            self.sheet_json = self.sheet_to_obj()
            self.write_sheet_to_file(self.sheet_json, self.name)
            for row in self.sheet_data_rows:
                self.categories.add(row[2])
            return 1
        except Exception as e:
            print(f"error during sheet refresh: {e}")
            return 0
        