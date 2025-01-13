import pymysql
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os

# Definer filnavnet til Excel-filen
file_name = "Excel_attendance_log.xlsx"

# Forhånds valgte farger for hver student basert på studentnummert vårt
student_colors = {
    "222333": "FFCCCB",  # Lys rød for student nummer 222333 Lars
    "238218": "CCFFCC",  # Lys grønn for student nummer 238218 Hamsa
    "238225": "1E90FF",  # Lys grønn for student nummer 238218 Magda
    "238218": "CCFFCC",  # Lys grønn for student nummer 238218 
    "238218": "CCFFCC",  # Lys grønn for student nummer 238218
    "238218": "CCFFCC",  # Lys grønn for student nummer 238218
    # Legg til flere farger for de andre studentnummerne her !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
}

# Koble til MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='attendance_bachelor_data'
)

# SQL-spørring for å hente nye data for dagen fra databasen (attendance_bachelor_data)
query = """
SELECT attendance_log.ID, members.student_number, members.name, attendance_log.check_in, attendance_log.check_out, attendance_log.duration
FROM attendance_log
JOIN members ON attendance_log.student_number = members.student_number
WHERE DATE(attendance_log.check_in) = CURDATE()
"""

# Hent dagens data og lagre i en pandas DataFrame
df = pd.read_sql(query, connection)

# Sjekk om det allerede finnes en Excel-fil for å unngå at flere excel-filer blir opprettet hver gang skriptet kjører
if os.path.exists(file_name):
    # Dersom det finnes, last inn eksisterende Excel-fil
    workbook = load_workbook(file_name)
    sheet = workbook.active

    # Finner neste ledige rad i Excel-arket
    next_row = sheet.max_row + 1

    # Legg til data i Excel-arket fra DataFrame
    for row in df.itertuples(index=False):
        sheet.append(row)

        # Få studentnummeret fra raden
        student_number = str(row[1])  # student_number er på kolonne 2
        fill_color = student_colors.get(student_number, "FFFFFF")  # Hvit som standard

        # Sett bakgrunnsfarge på raden
        for cell in sheet[next_row]:
            cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

        next_row += 1

    # Lagre endringer i Excel-filen
    workbook.save(file_name)
    print(f"Data for {pd.Timestamp.now().strftime('%Y-%m-%d')} er lagt til i {file_name}")
else:
    # Hvis Excel-filen ikke finnes, opprett ny fil eller hvis vi bruker en annen filtype, kan vi bruke to_excel-metoden
    df.to_excel(file_name, index=False)
    # Last inn Excel-filen for å legge til farger
    workbook = load_workbook(file_name)
    sheet = workbook.active

    # Sett bakgrunnsfarge for hver rad
    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, max_row=sheet.max_row), start=2):
        student_number = str(sheet.cell(row=row_idx, column=2).value)
        fill_color = student_colors.get(student_number, "FFFFFF")

        for cell in row:
            cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

    # Lagre endringer
    workbook.save(file_name)
    print(f"Ny Excel-fil opprettet med farger: {file_name}")

# tilslutt avlsutte databasetilkoblingen
connection.close()
