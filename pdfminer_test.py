
import pdfminer
from pdfminer.high_level import extract_text

pdf_file = open('Statements/Chase/Credit/22_09_13.pdf', 'rb')
text = extract_text(pdf_file, password='', page_numbers=None, maxpages=0, caching=True, codec='utf-8', laparams=None)
print(text)



# from io import StringIO

# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# from pdfminer.pdfdocument import PDFDocument
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfpage import PDFPage
# from pdfminer.pdfparser import PDFParser

# output_string = StringIO()
# with open('Chase/Credit/22_09_13.pdf', 'rb') as in_file:
#     parser = PDFParser(in_file)
#     doc = PDFDocument(parser)
#     rsrcmgr = PDFResourceManager()
#     device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#     interpreter = PDFPageInterpreter(rsrcmgr, device)
#     for page in PDFPage.create_pages(doc):
#         interpreter.process_page(page)

# print(output_string.getvalue())