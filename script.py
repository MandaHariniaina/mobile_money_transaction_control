import os
import csv
import datetime

def filter_invalid_transactions(input_dir, output_file, output_file_type_03):
    """
    Iterate through all CSV files in the input directory and extract records where TYPE_TRANSACTION is missing.
    Save those records into the output file.
    """
    headers = [
        "REF_TRANSACTION_MVOLA", "TYPE_TRANSACTION", "DATE_TRANSACTION", "NUM_TELEPHONE_PAYEUR", 
        "NOM_PRENOM_PAYEUR", "NUM_IDENTITE_PAYEUR", "NUM_CONTRAT", "DATE_EFFET", 
        "MONTANT_TRANSACTION", "MONTANT_COMMISSION_MVOLA", "MONTANT_NET"
    ]
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as out_csv:
        writer_invalid_transactions = csv.writer(out_csv, delimiter=';')
        writer_invalid_transactions.writerow(headers)  # Write headers to the output file
        
        for file_name in os.listdir(input_dir):
            if file_name.endswith(".csv") and file_name not in [output_file_type_03, output_file]:
                file_path = os.path.join(input_dir, file_name)
                temp_file_path = file_path + ".tmp"
                
                with open(file_path, mode='r+', encoding='utf-8') as in_csv, open(temp_file_path, mode='w', newline='', encoding='utf-8') as out_temp_fiile:
                    reader = csv.reader(in_csv, delimiter=';')
                    writer_cursor_file = csv.writer(out_temp_fiile, delimiter=';')
                    
                    headers_row = next(reader, None)
                    writer_cursor_file.writerow(headers_row)
                    
                    for row in reader:
                        if len(row) >= 2 and not row[1].strip():
                            if len(row) >= 8 and row[7].strip() == "01/01/2000":
                                row[7] = ""
                            writer_invalid_transactions.writerow(row)
                        if len(row) >= 8 and (row[1].strip() == "01" or row[1].strip() == "02" or (row[1].strip() == "03" and row[7].strip() and row[7].strip() != "01/01/2000")):
                            if (row[7].strip() == "01/01/2000"):
                                row[7] = ""
                            writer_cursor_file.writerow(row)
                os.replace(temp_file_path, file_path) 
    
def extract_type_03_missing_date_effet(input_dir, output_file, output_file_invalid):
    """
    Extract all records where TYPE_TRANSACTION is '03' but DATE_EFFET is missing and save them into another file.
    """
    headers = [
        "REF_TRANSACTION_MVOLA", "TYPE_TRANSACTION", "DATE_TRANSACTION", "NUM_TELEPHONE_PAYEUR", 
        "NOM_PRENOM_PAYEUR", "NUM_IDENTITE_PAYEUR", "NUM_CONTRAT", "DATE_EFFET", 
        "MONTANT_TRANSACTION", "MONTANT_COMMISSION_MVOLA", "MONTANT_NET"
    ]
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as out_csv:
        writer = csv.writer(out_csv, delimiter=';')
        writer.writerow(headers)  # Write headers to the output file
        
        for file_name in os.listdir(input_dir):
            if file_name.endswith(".csv") and file_name not in (output_file, output_file_invalid):
                file_path = os.path.join(input_dir, file_name)
                
                with open(file_path, mode='r', encoding='utf-8') as in_csv:
                    reader = csv.reader(in_csv, delimiter=';')
                    next(reader, None)  # Skip header row
                    
                    for row in reader:
                        if len(row) >= 8 and row[1].strip() == "03" and (not row[7].strip() or row[7].strip() == "01/01/2000"):  # TYPE_TRANSACTION = 03 and DATE_EFFET is invalid
                            writer.writerow(row)  # Write to output file

if __name__ == "__main__":
    input_directory = os.getcwd() + "\\to_treat"  # Change this to the current directory
    output_file_invalid = "erreurs_transaction_mvola.csv" # No type transaction specified
    today = datetime.date.today()
    output_file_type_03 = f"{today.strftime('%d-%m-%Y')}_type_03_missing_date_effet.csv" # Type 03 with no date effect
    
    extract_type_03_missing_date_effet(input_directory, output_file_type_03, output_file_invalid)
    filter_invalid_transactions(input_directory, output_file_invalid, output_file_type_03)
    
    print(f"Filtered records saved to {output_file_invalid}")
    print(f"Type 03 transactions with missing DATE_EFFET saved to {output_file_type_03}")
