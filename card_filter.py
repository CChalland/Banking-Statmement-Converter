import os
import argparse
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
                trans_type = row[0]
            elif any(x in ["Description", "Total remaining"] for x in row):
                cursorOn = True

            elif cursorOn:
                if 2 < len(row) < 4 and len(row[0]) == 10:
                    if trans_type == "Statement":
                        date, desc, amount = row
                        rows[key] = [string_date(date), desc, amount, "Apple", trans_type]
                    else:
                        date, desc, amount = row
                        rows[key] = [string_date(date), desc, amount, "Apple", trans_type]

                elif 4 < len(row) < 6:
                    if "%" in row[0]:
                        precentage, cash, date, desc, amount = row
                        rows[key] = [string_date(date), desc, amount, "Apple", trans_type]
                    elif len(row[0]) == 10:
                        date, desc, precentage, cash, amount = row
                        rows[key] = [string_date(date), desc, amount, "Apple", trans_type]

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
                    amount = row[0].split(': ')[1]
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
                trans_type = row[0]
                cursorOn = True
            elif cursorOn and 2 < len(row) < 4:
                raw_date, desc, amount = row
                date = raw_date + "/" + year_date
                rows[key] = [string_date(date), desc, amount, "Chase", trans_type]
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


    def data_from_files(self, file_list):
        for file in file_list:
            print("fname: ", file)
            data = [x for x in self._data_praser(file).values()]
            self.results.extend(data)




if __name__ == "__main__":
    input_files = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".", help="The directory to scan pdfs from")
    args = parser.parse_args()

    print("Starting PDFs Uploads:")
    for file in os.listdir(args.dir):
        if file.endswith(".pdf"):
            input_files.append(os.path.join(args.dir, file))

    statements = StatementFilter()
    statements.data_from_files(input_files)

    print("\n\n\n\nALL DATA: ", statements.results)