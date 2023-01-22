import os
import argparse
import math
import re
from datetime import datetime as dt

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage

CSV_DATE_FORMAT = "%m/%d/%Y"
CSV_HEADERS = ["Type", "Transaction Date", "Description", "Amount"]


class LineConverter(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.result = {}

    def receive_layout(self, ltpage):
        lines = {}
        def render(item):
            if isinstance(item, (LTPage, LTTextBox)):
                for child in item:
                    render(child)
            elif isinstance(item, LTTextLine):
                child_str = ""
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = " ".join(child_str.split()).strip()
                if child_str:
                    lines.setdefault((self.pageno, math.floor(item.bbox[1])), []).append(child_str)  # page number, bbox y1
                for child in item:
                    render(child)
            return
        render(ltpage)
        self.result = lines

    def get_lines(self):
        return list(self.result.values())

    def get_results(self):
        return self.result



def pdf_to_data(file_name):
    data = {}
    with open(file_name, "rb") as fp:
        rsrcmgr = PDFResourceManager()
        device = LineConverter(rsrcmgr, laparams=LAParams(boxes_flow=-0.5))
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            data.update(device.get_results())
    # print("data = ", data)

    return data


def chase_filter_rows(data):
    rows = []
    trans_type = ""
    cursorOn = False

    for key, row in data.items():
        if row == ["Table Summary"] or row == ["2022 Totals Year-to-Date"]:
            cursorOn = False
        elif row == ["PAYMENTS AND OTHER CREDITS"] or row == ["PURCHASE"]:
            trans_type = row[0]
            cursorOn = True
        elif cursorOn and 2 < len(row) < 4:
            # print("row type: ", trans_type)
            # print(row, "\n")
            date, desc, amount = row
            rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))

    return rows


def apple_filter_rows(data):
    rows = []
    trans_type = ""
    cursorOn = False
    stop_points = ["Total payments for this period", "Apple Card is issued by Goldman Sachs Bank USA, Salt Lake City Branch.", "Total Daily Cash this month", "Total financed"]

    for key, row in data.items():
        if any(x in stop_points for x in row):
            cursorOn = False
        
        elif row == ["Payments"] or row == ["Transactions"] or row == ["Statement"]:
            trans_type = row[0]
            
        elif row == ["Date", "Description", "Amount"] or row == ["Date", "Description", "Daily Cash", "Amount"] or row == ["Dates", "Description", "Daily Cash", "Amounts"]:
            cursorOn = True
            
        elif cursorOn and 2 < len(row) < 4:
            date, desc, amount = row
            rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))
            
        elif cursorOn and 4 < len(row) < 6:
            date, desc, precentage, cash, amount = row
            rows.append(dict(zip(CSV_HEADERS, [trans_type, date, desc, amount])))
    
    return rows


def convert_pdf(file_name):
    card_provider = file_name.split("/")[1]
    data = pdf_to_data(file_name)

    if card_provider == "Apple":
        return apple_filter_rows(data)
    elif card_provider == "Chase":
        return chase_filter_rows(data)


if __name__ == "__main__":
    # path = 'Statements/Chase/Credit'
    # input_files = []

    # for file in os.listdir(path):
    #     if file.endswith(".pdf"):
    #         input_files.append(os.path.join(path, file))

    # print("file names: ", input_files)

    # all_pdf_data = []
    # for file in input_files:
    #     print("fname: ", file)
    #     data = lines_rows(pdf_to_lines(file))
    #     print("\n\nrow data: ", data)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".", help="The directory to scan pdfs from")

    args = parser.parse_args()

    print("Started chase-ing PDFs:")
    input_files = []

    for file in os.listdir(args.dir):
        if file.endswith(".pdf"):
            input_files.append(os.path.join(args.dir, file))

    all_pdf_data = []
    num_rows = 0
    for file in input_files:
        print("fname: ", file)
        data = convert_pdf(file)
        print("Parsed {} rows from file: {}".format(len(data), file))
        print("\n\nrow data: ", data)
        all_pdf_data.extend(data)

    # print("\n\n\n\nALL DATA: ", all_pdf_data)
