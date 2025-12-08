import os
import csv
import datetime
import pymssql
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def filter_transactions(input_dir, output_file):
    """
    Iterate through all CSV files in the input directory and:
    - Remove if transaction reference is already present in the transaction table
    - Fill missing policy number from the table containing bo transactions
    - Extract those who have no policy number and are missing from the bo's records.
    Save those records into the output file.
    """
    headers = [
        "REF_TRANSACTION_MVOLA", "TYPE_TRANSACTION", "DATE_TRANSACTION", "NUM_TELEPHONE_PAYEUR", 
        "NOM_PRENOM_PAYEUR", "NUM_IDENTITE_PAYEUR", "NUM_CONTRAT", "DATE_EFFET", 
        "MONTANT_TRANSACTION", "MONTANT_COMMISSION_MVOLA", "MONTANT_NET"
    ]
    
    # Open connection
    mobile_money_db_config = {
        "database": os.getenv("MOBILE_MONEY_DATABASE"),
        "user": os.getenv("MOBILE_MONEY_USER"),
        "password": os.getenv("MOBILE_MONEY_PASSWORD"),
        "host": os.getenv("MOBILE_MONEY_HOST"),
        "port": str(os.getenv("MOBILE_MONEY_PORT")),
        "tds_version": "7.0",
    }
    conn = pymssql.connect(**mobile_money_db_config)
    
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
                        # Check if transaction reference already exists
                        with conn.cursor() as cursor:
                            query = "SELECT 1 FROM [Transactions] WHERE [Reference_Trans] = %s"
                            cursor.execute(query, (row[0].strip(),))
                            if cursor.fetchone():
                                # Transaction reference exists, skip this row
                                continue
                        if not row[1].strip():  # Check if TYPE_TRANSACTION is missing
                            # Try to find it in the database
                            with conn.cursor() as cursor:
                                query = """
                                    SELECT numeroPolice
                                    FROM [paiement_bo] 
                                    WHERE Reference = %s AND Statut = 'Succès' and Montant = %s and modePaiement = 'mvola'
                                """
                                cursor.execute(query, (row[0].strip(), float(row[8].strip())))
                                result = cursor.fetchone()
                                
                                if result:
                                    row[6] = result[0]  # Fill NUM_CONTRAT
                                    writer_cursor_file.writerow(row)
                                else:
                                    writer_invalid_transactions.writerow(row)
                        else:
                            if row[1].strip() in ["01", "03"]:
                                row[7] = row[2]
                            elif row[1].strip() == "02":
                                row[7] = ""
                            writer_cursor_file.writerow(row)
                os.replace(temp_file_path, file_path)
        
    # Close connection
    conn.close()
    
    
# TODO Test
def transform_excel_into_csv(input_dir):
    """ Transform all excel files in the input directory into CSV files with ; separator """
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            excel_file_path = os.path.join(input_dir, file_name)
            base_name = os.path.splitext(file_name)[0]
            
            # Use context manager to ensure proper resource cleanup
            with pd.ExcelFile(excel_file_path) as xls:
                for i, sheet_name in enumerate(xls.sheet_names, start=1):
                    df = xls.parse(sheet_name)
                    
                    # Convert date columns from yyyy-mm-dd to dd/mm/yyyy format
                    for col in df.columns:
                        if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d/%m/%Y')
                    
                    csv_file_name = f"{base_name}.csv"
                    csv_file_path = os.path.join(input_dir, csv_file_name)
                    
                    df.to_csv(csv_file_path, sep=';', index=False, encoding='utf-8')
                    print(f"Saved: {csv_file_path}")
            
            # Delete the Excel file after transformation (file handle is now properly closed)
            try:
                os.remove(excel_file_path)
                print(f"Deleted: {excel_file_path}")
            except PermissionError as e:
                print(f"Warning: Could not delete {excel_file_path} - {e}")
            except Exception as e:
                print(f"Error deleting {excel_file_path}: {e}")

if __name__ == "__main__":
    input_directory = os.getcwd() + "\\mvola\\to_treat"
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    output_file_invalid = f"mvola\\to_send_to_bo\\{yesterday.strftime('%Y-%m-%d')}_Transaction_Report_ARO_MVola_erreur.csv" # No type transaction specified
    output_file_type_03 = f"mvola\\missing_date_effet\\{yesterday.strftime('%d-%m-%Y')}_type_03_missing_date_effet.csv" # Type 03 with no date effect
    
    filter_transactions(input_directory, output_file_invalid)
    transform_excel_into_csv(input_directory)
