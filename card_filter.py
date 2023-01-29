import os
import argparse
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from pdf_parser import LineConverter

CSV_DATE_FORMAT = "%m/%d/%Y"
CSV_HEADERS = ["Type", "Transaction Date", "Description", "Amount"]



def chase_filter_rows(data):
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


def apple_filter_rows(data):
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


def pdf_to_data(file_name):
    data = {}
    card_provider = file_name.split("/")[1]
    
    with open(file_name, "rb") as fp:
        rsrcmgr = PDFResourceManager()
        device = LineConverter(rsrcmgr, laparams=LAParams(boxes_flow=-0.5))
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            data.update(device.get_results())

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
        data = pdf_to_data(file)
        # print("Parsed {} rows from file: {}".format(len(data), file))
        print(data, "\n\n")
        all_pdf_data.extend(data)

    # print("\n\n\n\nALL DATA: ", all_pdf_data)