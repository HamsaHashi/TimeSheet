import serial 
from openpyxl import Workbook, load_workbook
from datetime import datetime, timedelta
import os
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

id_to_name = {1: "Rebekka", 2: "Lars", 3: "Bjørnar", 4: "Ole", 5: "Magda", 6: "Hamsa"}

excel_file = 'Trying_out_time_sheet_system.xlsx'

workbook = None

# for tracking the row number in the excel file, do not change
row_tracker = {id: 6 for id in id_to_name.keys()} # default value for the row number


# Setup the excel file: either initialize a new file or load an existing one
def setup_excel_file(file_name):
    if os.path.exists(excel_file):
        workbook = load_workbook(excel_file)

        print(f"File {excel_file} loaded successfully")
    else:
        workbook = Workbook()
        workbook.remove(workbook.active)

        for name in id_to_name.values():
            sheet = workbook.create_sheet(title = name)
            sheet.append(['Date', 'Log in', 'Log out', 'Total session time', 'Work done'])
        workbook.save(excel_file)

        print(f"File {excel_file} created successfully")
    
    return workbook



# Log in or log out data from the arduino 
def log_worker(id, action):
    if id not in id_to_name:
        print(f"ID {id} is not valid.")
        return
    
    page_name = id_to_name[id]
    sheet = workbook[page_name]

    # default values for collumns and rows, do not change 
    date_column         = 3
    log_in_column       = 4
    log_out_column      = 5
    total_time_column   = 6
    

    # getting the row number for the log in, log out, total time and date
    global row_tracker
    current_row_to_use = row_tracker[id]

    # current date and time for log in 
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    # Log in 
    if action == 'Log in':

        sheet.cell(row = current_row_to_use, column = date_column, value = current_date)     # log in date
        sheet.cell(row = current_row_to_use, column = log_in_column, value = current_time)   # log in time

        print(f"{page_name} logged in at {current_time}")

        print(f"Next log in row: {current_row_to_use + 1} and date row: {current_row_to_use + 1}")
    
    elif action == 'Log out':
        log_in_time = sheet.cell(row = current_row_to_use, column = log_in_column).value

        if not log_in_time:
            print(f"{page_name} has not logged out yet or time has not been saved.")
            return
        
        # log_in_time = datetime.strptime(log_in_time, "%H:%M:%S")
        log_out_time = current_time

        # total_time = current_time - log_in_time

        sheet.cell(row = current_row_to_use, column = log_out_column, value = log_out_time)
        # sheet.cell(row = current_row_to_use, column = total_time_column, value = total_time)

        print(f"{page_name} logged out at {log_out_time}")
        # print(f"Total time spent: {total_time}")

        row_tracker[id] += 1

    else:
        print(f"Action {action} is not valid.")
        return
    
    workbook.save(excel_file)

setup_excel_file(excel_file)
workbook = setup_excel_file(excel_file)


log_worker(1, 'Log in')
time.sleep(10)
log_worker(1, 'Log out')
time.sleep(10)


log_worker(2, 'Log in')
time.sleep(10)
log_worker(2, 'Log out')
time.sleep(10)

log_worker(1, 'Log in')
time.sleep(10)
log_worker(1, 'Log out')




