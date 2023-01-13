import tabula


# Read remote pdf into list of DataFrame
# dfs2 = tabula.read_pdf("https://")
# convert all PDFs in a directory
# tabula.convert_into_by_batch("input_directory", output_format='csv', pages='all')



# Read pdf into list of DataFrame
# dfs = tabula.read_pdf("/Statements/Credit/22_12_13.pdf", pages='all')

# convert PDF into CSV file
tabula.convert_into("Statements/Chase/Credit/22_12_13.pdf", "output.csv", output_format="csv", pages='all')