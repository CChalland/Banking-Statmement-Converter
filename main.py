import os
import argparse

from card_filter import StatementFilter



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
        
    print("\n\n\n\nALL DATA: ", statements.results)

