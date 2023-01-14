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