import re
import argparse
import os
import subprocess
import csv

# function to extract text from pdf
def extract_text_from_pdf(pdf_path):
    # create a temporary text file
    temp_txt = "temp.txt"
    
    # call pdftotext to extract text
    subprocess.run(["pdftotext", "-layout", pdf_path, temp_txt])
    
    # read the extracted text
    with open(temp_txt, 'r') as f:
        text = f.read()
    
    # delete the temporary text file
    os.remove(temp_txt)
    
    return text

def convert_to_number(s):
    # Remove thousands separator and replace decimal comma with a period
    s = s.replace('.', '').replace(',', '.')
    # Convert to float
    try:
        return "{:.2f}".format(float(s)).replace(".", ",")
    except ValueError:
        return None


# function to parse text and return list of lines (each line is a list of columns)
def parse_text(text):
    lines = text.split("\n")
    parsed_lines = []
    debit_pos = 150
    credit_pos = 200

    for line in lines:
        # check and match the headers if present
        matchheaders = re.match(r'\s*(Date)\s*(Date valeur)\s*(Opération)\s*(Débit euros)\s*(Crédit euros)', line)
        if matchheaders:
            print(matchheaders.groupdict)
            # get the start position of debit and crédit Opération does not work
            debit_pos = matchheaders.start(4)
            credit_pos = matchheaders.start(5)
        # find occurrences of two dates separated by exactly one space
        match = re.search(r'(\d{2}/\d{2}/\d{4}) (\d{2}/\d{2}/\d{4})', line)
        if match:
            date, datevaleur = match.groups()
            pos_end_value = match.end()
            parsed_line = [date, datevaleur, line[pos_end_value:debit_pos], convert_to_number( line[debit_pos:credit_pos+1]), convert_to_number(line[credit_pos+2:len(line)])]
            # Print if no amount has been catched
            if parsed_line[3] == "" and parsed_line[4] == "":
                print(line)
                print(len(line),"/",len(line))
                print(parsed_line)

            parsed_lines.append(parsed_line)
    return parsed_lines

# function to write lines to CSV
def write_to_csv(lines, output_path):
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Date de valeur', 'Operation', 'Debit Euros', 'Credit Euros'])
        writer.writerows(lines)

# main function to read PDFs, extract and parse text, and write to CSV
def process_bank_statements(input_dir, output_path):
    all_lines = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(filename)
            text = extract_text_from_pdf(pdf_path)
            lines = parse_text(text)
            all_lines.extend(lines)
    write_to_csv(all_lines, output_path)

# Argument parser
parser = argparse.ArgumentParser(description='Process bank statement PDFs.')
parser.add_argument('-i', '--input', type=str, required=True, help='Path to the directory containing the input PDFs.')
parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output CSV file.')
args = parser.parse_args()

# example usage
process_bank_statements(args.input, args.output)
