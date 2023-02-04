import os
import argparse

from card_filter import StatementFilter



if __name__ == "__main__":
    statements = StatementFilter("Statements")
    statements.crawl_directory()
    data = statements.results
    print("\nALL DATA: ", data)
    
    # for file in statements.input_files:
    #     print("file: ", file)
    #     data = statements._data_praser(file)
    #     print("data = ", data, "\n\n")
    