from src.financetracker.sheetsapi import FinanceSheet

class TestFinanceSheet:

    def test_sheet_data_loaded(self):
        sheet_object = FinanceSheet('test')
        assert len(sheet_object.sheet_rows) > 1

    def test_sheet_columns_identified(self):
        sheet_object = FinanceSheet('test')
        assert len(sheet_object.sheet_cols) == 4
    
    def test_sheet_add_row(self):
        sheet_object = FinanceSheet('test')
        assert sheet_object.add_row(['test', 1.25, 'testing category', '2026-04-01']) == 1

    def test_sheet_refresh(self):
        sheet_object = FinanceSheet('test')
        assert sheet_object._refresh_sheet() == 1