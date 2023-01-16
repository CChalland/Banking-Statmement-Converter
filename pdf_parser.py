import os
import argparse
import re
from datetime import datetime as dt

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage

CSV_DATE_FORMAT = '%m/%d/%Y'
CSV_HEADERS = ['Type', 'Trans Date', 'Description', 'Amount']


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
                child_str = ''
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    lines.setdefault((self.pageno, item.bbox[1]), []).append(child_str) # page number, bbox y1
                for child in item:
                    render(child)
            return

        render(ltpage)
        self.result = lines

    def get_result(self):
        return list(self.result.values())


class Parser:
    def __init__(self):
        self.data = []
        self.csv = []
    
    def pdf_lines(self, file_name):
        with open(file_name, 'rb') as fp:
            resourceManager = PDFResourceManager()
            device = LineConverter(resourceManager, laparams=LAParams())
            interpreter = PDFPageInterpreter(resourceManager, device)
            
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                self.data.extend(device.get_results())
    
    def _translate_to_csv(self):
        for row in self.data:
            print(row)



def pdf_to_lines(file_name):
    data = []

    with open(file_name, 'rb') as fp:
        rsrcmgr = PDFResourceManager()
        device = LineConverter(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            data.extend(device.get_result())

    # print(data)
    return data

def lines_rows(lines):
    data = []
    row_type = ''
    cursorOn = False
    
    for row in lines:
        if row == ['Table Summary'] or row == ['2022 Totals Year-to-Date']:
            cursorOn = False
        elif row == ['PAYMENTS AND OTHER CREDITS'] or row == ['PURCHASE']:
            row_type = row[0]
            cursorOn = True
        elif cursorOn and 2 < len(row) < 4:
            print("row type: ", row_type)
            print(row, "\n")
            
            data.extend(row)
    
    return data



if __name__ == '__main__':
    path = 'Statements/Chase/Credit'
    input_files = []

    for file in os.listdir(path):
        if file.endswith(".pdf"):
            input_files.append(os.path.join(path, file))
    
    print("file names: ", input_files)
    
    all_pdf_data = []
    for file in input_files:
        print("fname: ", file)
        data = lines_rows(pdf_to_lines(file))
        # print("\n\nrow data: ", data)
