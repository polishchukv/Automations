import Alteryx
import ctypes
import os
import shutil
import pandas as pd
import openpyxl
import glob
import tempfile
from datetime import datetime, timedelta

# For file locking in Windows
import msvcrt

# Function for locking a file
def lock_file(file_path):
    fd = os.open(file_path, os.O_RDWR)
    msvcrt.locking(fd, msvcrt.LK_LOCK, os.path.getsize(file_path))
    return fd

# Function for unlocking a file
def unlock_file(fd):
    msvcrt.locking(fd, msvcrt.LK_UNLCK, os.path.getsize(fd))
    os.close(fd)

# New base directories (Replaced with placeholders for organizational paths)
root_dir_techeol = os.path.join(os.getenv('USERPROFILE'), "{ORGANIZATION_PATH_1}")
root_dir_streamingeol = os.path.join(os.getenv('USERPROFILE'), "{ORGANIZATION_PATH_2}")

def get_matching_folders(root_dir, match_format):
    matching_folders = []
    for root, dirs, files in os.walk(root_dir):
        for dir in dirs:
            if match_format in dir:
                matching_folders.append(os.path.join(root, dir))
    # Returns a DataFrame
    return pd.DataFrame(matching_folders, columns=['Matching Folder Paths'])

def validate_excel_file(file_path, sheet_name):
    try:
        actual_file_path = ensure_read_access(file_path)
        xls = pd.ExcelFile(actual_file_path, engine='openpyxl')
        
        if sheet_name in xls.sheet_names:
            data = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"Successfully read: {actual_file_path}")
            return data
        else:
            print(f"Sheet {sheet_name} not found in {actual_file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error while processing file: {actual_file_path}") 
        print(f"Error message: {str(e)}")
        return pd.DataFrame()

def unhide_hidden(file_path):
    try:
        actual_file_path = ensure_write_access(file_path)
        
        excelFile = openpyxl.load_workbook(filename=actual_file_path)
        for excelSheet in excelFile:
            for row in excelSheet.row_dimensions:
                excelSheet.row_dimensions[row].hidden = False
            for col in excelSheet.column_dimensions:
                excelSheet.column_dimensions[col].hidden = False
        
        excelFile.save(actual_file_path)
    except Exception as e:
        print(f"Error while un-hiding file: {actual_file_path}") 
        print(f"Error message: {str(e)}")
        pass

def ensure_read_access(file_path):
    if os.access(file_path, os.R_OK):
        return file_path
    else:
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
        shutil.copy2(file_path, temp_file_path)
        return temp_file_path

def ensure_write_access(file_path):
    if os.access(file_path, os.W_OK):
        return file_path
    else:
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
        shutil.copy2(file_path, temp_file_path)
        return temp_file_path

def union_all_excel_files(df):
    all_data = pd.DataFrame()
    target_sheet = "sheet1"
    temp_files = []
    try:
        for path in df['Local Copy Paths']:
            files = glob.glob(path)
            for file in files:
                if file.endswith('.xlsx'):
                    lock_fd = None
                    try:
                        lock_fd = lock_file(file)
                        temp_files.append(file)
                        unhide_hidden(file)
                        data = validate_excel_file(file, target_sheet)
                        if not data.empty:
                            if all_data.empty:
                                all_data = data
                            else:
                                all_data = pd.concat([all_data, data], ignore_index=True, sort=False)
                    except Exception as e:
                        print(f"Error while processing file: {file}") 
                        print(f"Error message: {str(e)}")
                    finally:
                        if lock_fd:
                            unlock_file(lock_fd)
    finally:
        for temp_file in temp_files:
            temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(temp_file))
            if os.path.exists(temp_path):
                os.remove(temp_path)
    return all_data

def copy_files_to_local(df):
    local_paths = []
    local_dir = os.path.join(os.getenv('USERPROFILE'), "{LOCAL_COPY_DIR}")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    for path in df['Matching Folder Paths']:
        files = glob.glob(os.path.join(path, "*.xlsx"))
        for file in files:
            if file.endswith('.xlsx'):
                local_file_path = os.path.join(local_dir, os.path.basename(file))
                shutil.copy2(file, local_file_path)
                local_paths.append(local_file_path)
    
    return pd.DataFrame(local_paths, columns=['Local Copy Paths'])

# Hardcoded date example
# Example match_format for testing: match_format = "2024-07"

try:
    now = datetime.now()
    print(f"Datetime.now function value: {now}.")
    if 1 <= now.day <= 5:
        first_day_of_current_month = now.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        match_format = last_day_of_previous_month.strftime('%Y-%m')
    else:
        match_format = now.strftime('%Y-%m')
except Exception as e:
    match_format = "2024-08"
    print(f"Error occurred: {str(e)}")

print(match_format)

df_techeol = get_matching_folders(root_dir_techeol, match_format)
df_streamingeol = get_matching_folders(root_dir_streamingeol, match_format)

df_techeol_local = copy_files_to_local(df_techeol)
df_streamingeol_local = copy_files_to_local(df_streamingeol)

union_df_techeol_local = union_all_excel_files(df_techeol_local)
union_df_streamingeol_local = union_all_excel_files(df_streamingeol_local)

union_all = pd.concat([union_df_techeol_local, union_df_streamingeol_local], ignore_index=True, sort=False)
print(union_all.columns.tolist())

union_all = union_all.fillna('')
union_all.columns = [str(col) for col in union_all.columns]

Alteryx.write(union_all, 1)
