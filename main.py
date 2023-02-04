import os
import argparse

from card_filter import StatementFilter



if __name__ == "__main__":
    statements = StatementFilter()
    statements.crawl_directory("Statements")
    data = statements.results
    
    print("\nALL DATA: ", data)