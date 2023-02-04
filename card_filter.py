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
    def __init__(self):
        self.results = []


    def _apple_rows(self, data):
        rows = dict()
        statement = []
        stmt_idx = 0
        stop_points = ["Total payments for this period", "Apple Card is issued by Goldman Sachs Bank USA, Salt Lake City Branch.", "Total Daily Cash this month", "Total financed"]
        cursorOn = False
        stmt_state = False
        trans_type = ""

        for key, row in data.items():
            if any(x in stop_points for x in row):
                cursorOn = False
            elif row == ["Payments"] or row == ["Transactions"] or row == ["Statement"]:
                trans_type = row[0] if row == ["Payments"] else "Transactions"
            elif any(x in ["Description", "Total remaining"] for x in row):
                cursorOn = True

            elif cursorOn:
                if 2 < len(row) < 4 and len(row[0]) == 10:
                    if trans_type == "Statement":
                        date_str, desc, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", trans_type, date.strftime("%B"), date.year]
                    else:
                        date_str, desc, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", trans_type, date.strftime("%B"), date.year]

                elif 4 < len(row) < 6:
                    if "%" in row[0]:
                        precentage, cash, date_str, desc, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", trans_type, date.strftime("%B"), date.year]
                    elif len(row[0]) == 10:
                        date_str, desc, precentage, cash, amount_str = row
                        date = dt.strptime(date_str, '%m/%d/%Y').date()
                        amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                        rows[key] = [date, desc, amount, "Apple", trans_type, date.strftime("%B"), date.year]

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
                    if len(row) == 3:
                        statement[2] = amount
                    else:
                        statement[4] = amount
        return rows


    def _chase_rows(self, data, year_date):
        rows = dict()
        trans_type = ""
        cursorOn = False

        for key, row in data.items():
            if row == ["Table Summary"] or row == ["2022 Totals Year-to-Date"]:
                cursorOn = False
            elif row == ["PAYMENTS AND OTHER CREDITS"] or row == ["PURCHASE"]:
                trans_type = "Transactions" if row[0] == ["PAYMENTS AND OTHER CREDITS"] else "Payments"
                cursorOn = True
            elif cursorOn and 2 < len(row) < 4:
                raw_date, desc, amount_str = row
                date_str = raw_date + "/" + year_date
                date = dt.strptime(date_str, '%m/%d/%Y').date()
                amount = Decimal(sub(r'[^\d\-.]', '', amount_str))
                rows[key] = [date, desc, amount, "Chase", trans_type, date.strftime("%B"), date.year]
        return rows


    def _data_praser(self, file):
        raw_data = {}
        card_provider = list(set(file.split("/")).intersection(set(gvars.PROVIDERS)))[0]
        
        with open(file, "rb") as fp:
            rsrcmgr = PDFResourceManager()
            device = LineConverter(rsrcmgr, laparams=LAParams(boxes_flow=-0.5))
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                raw_data.update(device.get_results())

        if card_provider == "Apple":
            return self._apple_rows(raw_data)
        elif card_provider == "Chase":
            filename = file.split("/")[-1].split(".")[0]
            year_date = "20" + filename.split("_")[0]
            return self._chase_rows(raw_data, year_date)


    def _data_from_files(self, file_list):
        for file in file_list:
            print("fname: ", file)
            data = [dict(zip(gvars.CSV_HEADERS, values)) for values in self._data_praser(file).values()]
            self.results.extend(data)
            self.results.sort(key=lambda row: row["Transaction Date"], reverse=True)


    def crawl_directory(self, dir):
        input_files = []
        for root, dir_names, file_names in os.walk(dir):
            for file in file_names:
                if file.endswith(".pdf"):
                    input_files.append(os.path.join(root, file))
        # print("The complete set of files are ", input_files)
        self._data_from_files(input_files)




if __name__ == "__main__":
    statements = StatementFilter()
    statements.crawl_directory("Statements")
    data = statements.results
    
    print("\nALL DATA: ", data)