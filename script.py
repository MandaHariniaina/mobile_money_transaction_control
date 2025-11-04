import os
import csv
import datetime
import pandas as pd

def filter_invalid_transactions(input_dir, output_file):
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
            if file_name.endswith(".csv"):
                file_path = os.path.join(input_dir, file_name)
                temp_file_path = file_path + ".tmp"
                
                with open(file_path, mode='r+', encoding='utf-8') as in_csv, open(temp_file_path, mode='w', newline='', encoding='utf-8') as out_temp_file:
                    reader = csv.reader(in_csv, delimiter=';')
                    writer_cursor_file = csv.writer(out_temp_file, delimiter=';')
                    
                    headers_row = next(reader, None)
                    writer_cursor_file.writerow(headers_row)
                    
                    for row in reader:
                        if not row[1].strip():  # Check if TYPE_TRANSACTION is missing
                            writer_invalid_transactions.writerow(row)
                        else:
                            if row[1].strip() in ["01", "03"]:
                                row[7] = row[2]
                            elif row[1].strip() == "02":
                                row[7] = ""
                            writer_cursor_file.writerow(row)
                os.replace(temp_file_path, file_path)
                
def transform_excel_into_csv(input_dir):
    """ Transform all excel files in the input directory into CSV files with ; separator """
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            excel_file_path = os.path.join(input_dir, file_name)
            base_name = os.path.splitext(file_name)[0]
            
            xls = pd.ExcelFile(excel_file_path)
            for i, sheet_name in enumerate(xls.sheet_names, start=1):
                df = xls.parse(sheet_name)
                csv_file_name = f"{base_name}.csv"
                csv_file_path = os.path.join(input_dir, csv_file_name)
                
                df.to_csv(csv_file_path, sep=';', index=False, encoding='utf-8')
                print(f"Saved: {csv_file_path}")
            
            # Delete the Excel file after transformation
            os.remove(excel_file_path)
            print(f"Deleted: {excel_file_path}")

if __name__ == "__main__":
    input_directory = os.getcwd() + "\\mvola\\to_treat"
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    output_file_invalid = f"mvola\\to_send_to_bo\\{yesterday.strftime('%Y-%m-%d')}_Transaction_Report_ARO_MVola_erreur.csv" # No type transaction specified
    output_file_type_03 = f"mvola\\missing_date_effet\\{yesterday.strftime('%d-%m-%Y')}_type_03_missing_date_effet.csv" # Type 03 with no date effect
    
    filter_invalid_transactions(input_directory, output_file_invalid)
    transform_excel_into_csv(input_directory)
