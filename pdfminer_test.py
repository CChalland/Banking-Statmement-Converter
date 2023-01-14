
# from pdfminer.high_level import extract_text

# pdf_file = open('Statements/Chase/Credit/22_09_13.pdf', 'rb')
# text = extract_text(pdf_file, password='', page_numbers=None, maxpages=0, caching=True, codec='utf-8', laparams=None)
# print(text)


from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

# Open a PDF document.
fp = open('Statements/Apple/Credit/22_07_31.pdf', 'rb')
parser = PDFParser(fp)
document = PDFDocument(parser)

# Get the outlines of the document.
outlines = document.get_outlines()
for (level,title,dest,a,se) in outlines:
    print (level, title)


# from io import StringIO

# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# from pdfminer.pdfdocument import PDFDocument
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdfparser import PDFParser

# output_string = StringIO()
# with open('Statements/Apple/Credit/22_07_31.pdf', 'rb') as in_file:
#     parser = PDFParser(in_file)
#     doc = PDFDocument(parser)
#     rsrcmgr = PDFResourceManager()
#     device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#     interpreter = PDFPageInterpreter(rsrcmgr, device)
#     for page in PDFPage.create_pages(doc):
#         interpreter.process_page(page)

# print(output_string.getvalue())




"""
import os
import argparse
import re
import csv
from datetime import datetime as dt

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage

CSV_DATE_FORMAT = '%m/%d/%Y'
CSV_HEADERS = ['Type', 'Trans Date', 'Post Date', 'Description', 'Amount']
START_DATE = None
END_DATE = None


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


def pdf_to_lines(file_name):
    data = []

    with open(file_name, 'rb') as fp:
        rsrcmgr = PDFResourceManager()
        device = LineConverter(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            data.extend(device.get_result())
    
    return data

# def translate_to_csv(lines):
#     # Regex pattern for matching month/day format of each line
#     date_pattern = r'\d\d\/\d\d'
#     csv_data = []

#     rownum = -1
#     for row in lines:
#         rownum += 1

#         if not 2 <= len(row) <= 4:
#             continue

#         if (len(row) == 2):
#             if not re.match(date_pattern + '$', row[0][:5]):
#                 continue
#             date = row[0][:5]
#             desc = row[0][6:]
#             amount = row[1]
#         elif (len(row) == 4):
#             if not re.match(date_pattern + '$', row[1]):
#                 continue
#             date = row[1]
#             desc = row[0] + ' ' + row[2]
#             amount = row[3]
#         elif re.match(date_pattern + '$', row[1]):
#             desc, date, amount = row
#         else:
#             date, desc, amount = row


#             csv_data.append(dict(zip(CSV_HEADERS, [trans_type, date, '', desc, amount])))

#     return csv_data



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start",
        default=None,
        help="The Start Date to filter items (inclusive), uses the date-format"
    )
    parser.add_argument(
        "--end",
        default=None,
        help="The End Date to filter items (exclusive), uses the date-format"
    )
    parser.add_argument(
        "--date-format",
        default=CSV_DATE_FORMAT,
        help="The output date format, default: '%(default)s'"
    )
    parser.add_argument(
        "--output",
        default='Extracted_Chase_Activity_Stmt_{}.csv'.format(dt.today().strftime('%Y%m%d')),
        help="The output filename"
    )
    parser.add_argument(
        "--dir",
        default='.',
        help="The directory to scan pdfs from"
    )

    args = parser.parse_args()

    CSV_DATE_FORMAT = args.date_format
    output_file = args.output

    print('Started chase-ing PDFs:')
    input_files = []

    for file in os.listdir(args.dir):
        if file.endswith(".pdf"):
            input_files.append(os.path.join(args.dir, file))

    all_pdf_data = []
    num_rows = 0
    for file in input_files:
        data = pdf_to_lines(file)
        print(file, ' \n', data)
        # all_pdf_data.extend(data)
        print('Parsed {} rows from file: {}'.format(len(data), file))
"""