import os
import argparse
from re import sub
from decimal import Decimal
from datetime import datetime as dt
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from pdf_parser import LineConverter
from utils import *
import gvars


class StatementFilter:
    def __init__(self, dir):
        self.dir = dir
        self.input_files = []
        self.results = []


    def _apple_credit(self, data, account_type, file_date):
        rows = dict()
        statement = []
        stmt_idx = 0
        stop_points = ["Total payments for this period", "Apple Card is issued by Goldman Sachs Bank USA, Salt Lake City Branch.", "Total Daily Cash this month", "Total financed"]
        cursorOn = False
        stmt_state = False
        trans_type = ""
        bill_date = dt.strptime(file_date, '%y_%m_%d').date()

        for key, row in data.items():
            if any(x in stop_points for x in row):
                cursorOn = False
            elif row == ["Payments"] or row == ["Transactions"] or row == ["Statement"]:
                trans_type = row[0]
            elif any(x in ["Description", "Total remaining"] for x in row):
                cursorOn = True

            elif cursorOn:
                if 2 < len(row) < 4 and len(row[0]) == 10:
                    if trans_type == "Statement":
                        date_str, desc, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", account_type, trans_type, bill_date]
                    else:
                        date_str, desc, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", account_type, trans_type, bill_date]

                elif 4 < len(row) < 6:
                    if "%" in row[0]:
                        precentage, cash, date_str, desc, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", account_type, trans_type, bill_date]
                    elif len(row[0]) == 10:
                        date_str, desc, precentage, cash, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", account_type, trans_type, bill_date]

                elif "TRANSACTION #" in row[0]:
                    stmt_state = True
                    stmt_idx = (key[0], key[1] + 10)
                    statement = rows[stmt_idx]
                    statement[1] = row[0]

                elif "Final installment" in row[0]:
                    stmt_state = False
                    statement[1] += ", " + row[0]
                    rows[stmt_idx] = statement
                
                elif stmt_state:
                    amount_str = row[0].split(': ')[1]
                    amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                    statement[2] = amount
        return rows


    def _chase_credit(self, data, account_type, file_date):
        rows = dict()
        trans_type = ""
        cursorOn = False
        bill_date = dt.strptime(file_date, '%y_%m_%d').date()

        for key, row in data.items():
            if row == ["Table Summary"] or row == ["2022 Totals Year-to-Date"]:
                cursorOn = False
            elif row == ["PAYMENTS AND OTHER CREDITS"] or row == ["PURCHASE"]:
                trans_type = "Transactions" if row == ["PURCHASE"] else "Payments"
                cursorOn = True
            elif cursorOn and 2 < len(row) < 4:
                raw_date, desc, amount_str = row
                raw_date_arr = raw_date.split('/')
                
                if raw_date_arr[0] == '12' and bill_date.month == 1:
                    date_str = raw_date + "/" + str(bill_date.year - 1)
                else:
                    date_str = raw_date + "/" + str(bill_date.year)
                
                date = dt.strptime(date_str, '%m/%d/%Y').date()
                amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                rows[key] = [date, desc, amount, "Chase", account_type, trans_type, bill_date]
        return rows


    def _chase_checkings_savings(self, data, account_type, file_date):
        rows = dict()
        trans_type = ""
        cursorOn = False
        bill_date = dt.strptime(file_date, '%y_%m_%d').date()
        
        for key, row in data.items():
            if row == ["*end*transaction detail"]:
                cursorOn = False
            elif row == ["Chase Savings"] or row == ["Chase Total Checking"]:
                trans_type = "Savings" if row == ["Chase Savings"] else "Checking"
            elif row == ["DATE", "DESCRIPTION", "AMOUNT", "BALANCE"]:
                cursorOn = True
            elif cursorOn and 3 < len(row) < 5:
                raw_date, desc, amount_str, total_str = row
                raw_date_arr = raw_date.split('/')
                
                if raw_date_arr[0] == '12' and bill_date.month == 1:
                    date_str = raw_date + "/" + str(bill_date.year - 1)
                else:
                    date_str = raw_date + "/" + str(bill_date.year)
                
                date = dt.strptime(date_str, '%m/%d/%Y').date()
                amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                total = Decimal(sub(r'[^\d\-.]', '', total_str))
                rows[key] = [date, desc, amount, "Chase", account_type, trans_type, bill_date]
        return rows


    def _data_praser(self, file):
        raw_data = {}
        account_type = file.split("/")[-2]
        file_date = file.split("/")[-1].split(".")[0]
        card_provider = list(set(file.split("/")).intersection(set(gvars.PROVIDERS)))[0]
        
        with open(file, "rb") as fp:
            rsrcmgr = PDFResourceManager()
            device = LineConverter(rsrcmgr, laparams=LAParams(boxes_flow=-0.5))
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                raw_data.update(device.get_results())

        if card_provider == "Apple":
            return self._apple_credit(raw_data, account_type, file_date)
        elif card_provider == "Chase":
            if account_type == "Credit":
                return self._chase_credit(raw_data, account_type, file_date)
            elif account_type == "Checkings" or account_type == "Savings":
                return self._chase_checkings_savings(raw_data, account_type, file_date)


    def _data_from_files(self, file_list):
        for file in file_list:
            print("fname: ", file)
            data = [dict(zip(gvars.CSV_HEADERS, values)) for values in self._data_praser(file).values()]
            self.results.extend(data)
            self.results.sort(key=lambda row: row["Transaction Date"], reverse=True)


    def crawl_directory(self):
        for root, dir_names, file_names in os.walk(self.dir):
            for file in file_names:
                if file.endswith(".pdf"):
                    self.input_files.append(os.path.join(root, file))
        # print("The complete set of files are ", self.input_files)
        self._data_from_files(self.input_files)




if __name__ == "__main__":
    statements = StatementFilter("Statements")
    statements.crawl_directory()
    data = statements.results
    print("\nALL DATA: ", data)
    
    # for file in statements.input_files:
    #     print("file: ", file)
    #     data = statements._data_praser(file)
    #     print("data = ", data, "\n\n")
    