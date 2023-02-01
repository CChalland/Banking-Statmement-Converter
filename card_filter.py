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


    def _clean_data(self, data):
        return data


    def _apple_rows(self, data):
        # csv_rows = []
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
                        rows[key] = [date, desc, amount, trans_type]
                    else:
                        date, desc, amount = row
                        rows[key] = [date, desc, amount, trans_type]
                        # csv_rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))

                elif 4 < len(row) < 6:
                    if "%" in row[0]:
                        precentage, cash, date, desc, amount = row
                        rows[key] = [date, desc, precentage, cash, amount, trans_type]
                        # csv_rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))
                    elif len(row[0]) == 10:
                        date, desc, precentage, cash, amount = row
                        rows[key] = [date, desc, precentage, cash, amount, trans_type]
                        # csv_rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))

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
                    statement[2] = amount

        # return csv_rows
        return rows


    def _chase_rows(self, data):
        # csv_rows = []
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
                date, desc, amount = row
                rows[key] = [date, desc, amount, trans_type]
                # csv_rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))

        # return csv_rows
        return rows


    def data_from_file(self, filename):
        raw_data = {}
        card_provider = list(set(filename.split("/")).intersection(set(gvars.PROVIDERS)))[0]
        
        with open(filename, "rb") as fp:
            rsrcmgr = PDFResourceManager()
            device = LineConverter(rsrcmgr, laparams=LAParams(boxes_flow=-0.5))
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                raw_data.update(device.get_results())

        if card_provider == "Apple":
            self.results.append(self._apple_rows(raw_data))
            return self._apple_rows(raw_data)
        elif card_provider == "Chase":
            self.results.append(self._chase_rows(raw_data))
            return self._chase_rows(raw_data)


    def get_data(self):
        return self.results





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

    for file in input_files:
        print("fname: ", file)
        data = statements.data_from_file(file)
        print(data, "\n\n")

    print("\n\n\n\nALL DATA: ", statements.results)