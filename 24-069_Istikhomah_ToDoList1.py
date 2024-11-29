# Membuat aplikasi Todo List secara realtime

# IMPORT PACKAGE ------------------------------------------------------------------
import os
from datetime import datetime
import json
import re

# SETUP ----------------------------------------------------------------------------
# CONSTANT
DATA_PATH = "data.json"

STATUS = {
    0: 'Belum Selesai',
    1: 'Selesai',
    2: 'Terlambat'
}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DATE_FORMAT_PATTREN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

# ERROR HANDLING
error = {
    "show" : False,
    "message" : ""
}

# DATA
todos = []

# UTILS / HELPERS -------------------------------------------------------

def load_data():
    try:
        with open(DATA_PATH, 'r') as file:
            content = file.read().strip()
            if not content:  # Jika file kosong
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save2json():
    with open(DATA_PATH, 'w') as file:
        json.dump(todos, file, indent=2)

def update_error(message="", show=True):
    error['message'] = "~ ⚠ " + message
    error['show'] = show

def is_valid_date(date) -> bool:
    return re.match(DATE_FORMAT_PATTREN, date)

def date2str(date: datetime) -> str:
    return date.strftime(DATE_FORMAT)

def str2date(date:str) -> datetime:
    return datetime.strptime(date, DATE_FORMAT)

def is_overdue(todo):
    today = datetime.now()
    if todo['status'] != 1 and today > str2date(todo['due_date']):
        return True
    return False

def mark_all_overdue_todos():
    for todo in todos:
        if is_overdue(todo):
            todo['status'] = 2

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def cari_tugas():
    priority = int(input("Cari tugas prioritas (1-5): "))
    
    hasil = [tugas for tugas in todos if tugas['priority'] == priority]
    
    if hasil:
        print(f"\nTugas Prioritas {priority}:")
        for tugas in hasil:
            print(f"ID: {tugas['id']} - {tugas['task']}")
        print(f"Total: {len(hasil)} tugas")
    else:
        print("Tidak ada tugas ditemukan.")
    
    input("Tekan Enter untuk melanjutkan...")

# CRUD -------------------------------------------------------------
def add_task(task="", due_date="", description="",category="", priority=0):
    if not is_valid_date(due_date):
        update_error("Format tanggal tidak valid. Harap masukkan tanggal dalam format 'YYYY-MM-DD HH:MM:SS'.")
        return

    if type(priority) is not int:
        update_error("Prioritas harus angka!!")
        return

    today = datetime.now()

    if today >= str2date(due_date):
        update_error("Tenggat waktu harus lebih besar atau sama dengan tanggal sekarang")
        return

    new_id = 0 if not todos else max(todos, key=lambda todo: todo['id'])['id'] + 1
    todos.append({
        'id' : new_id,
        'task': task,
        'category' : category,
        'priority' : priority,
        'status': 0,
        'description' : description,
        'created_at': date2str(today),
        'due_date' : due_date,
        })

    save2json()

def create_line_separator(*column_widths):
    """Create a line separator for a table."""
    separator = ""
    for width in column_widths:
        separator += "+" + "-" * width
    separator += "+"
    print(separator)

def create_row(widths, values):
    """Create a row for a table."""
    row = ""
    for width, value in zip(widths, values):
        value = str(value)
        if len(value) > width:
            value = value[:width - 3] + "..."
        row += "| " + value.ljust(width) + " "
    row += "|"
    print(row)

def show_tasks():

    todos.sort(key=lambda x: x['priority'])

    header = ["ID", "Tugas", "Deskripsi", "Kategori", "Prioritas", "Status", "Tenggat Waktu", "created_at"]
    column_widths = [3, 20, 50, 10, 9, 14, 20, 20]

    sperator_widths = [width + 2 for width in column_widths]

    print("Daftar Tugas:")
    create_line_separator(*sperator_widths)
    create_row(column_widths, header)
    create_line_separator(*sperator_widths)
    for todo in todos:
        id, task, category, priority, status, description, created_at, due_date = todo.values()
        create_row(
            column_widths,
            [id, task, description, category, priority, STATUS[status], due_date, created_at]
        )
    create_line_separator(*sperator_widths)

def delete_task(task_id):
    global todos
    for i, todo in enumerate(todos):
        if todo['id'] == task_id:
            del todos[i]
            save2json()
            return
    update_error("Tugas tidak ditemukan")

def update_status_to_done(task_id):
    found = False
    for todo in todos:
        if todo['id'] == task_id:
            if todo['status'] == 1:
                update_error("Tugas sudah selesai")
                return

            if todo['status'] == 2:
                update_error("Tugas sudah terlambat")
                return

            todo['status'] = 1
            save2json()
            found =True
            break

    if not found:
        update_error("Tugas tidak ditemukan")

def summary():
    total = len(todos)
    done = len(list(filter(lambda todo: todo['status'] == 1, todos)))

    print(f"Total tugas: {total} \t|\t Selesai: {done} \t|\t Belum Selesai: {total - done}")


# MAIN ------------------------------------------------------------------------------------------------

def onInit():
    clear_screen()
    mark_all_overdue_todos()
    print(" Aplikasi Todo List ".center(100, "="))
    summary()
    show_tasks()
    print()


def menu():
    global todos
    todos = load_data()

    while True:
        onInit()
        print(" Menu ".center(30, "="))
        print("\t1. Tambah Tugas")
        print("\t2. Hapus Tugas")
        print("\t3. Selesaikan Tugas")
        print("\t4. Cari Tugas")
        print("\t5. Refresh")
        print("\t6. Keluar")
        print("="*30)

        if error['show']:
            print(f"Error: {error['message']}")
            update_error("", False)

        choice = input("Pilih menu (1/2/3/4/5/6): ")

        if choice == '1':
            task = input("Masukkan tugas baru: ")
            due_date = input("Masukkan tenggat waktu (YYYY-MM-DD HH:MM:SS): ")
            description = input("Masukkan deskripsi tugas: ")
            category = input("Masukkan kategori tugas: ")
            priority = int(input("Masukkan prioritas tugas (1-5): "))
            add_task(task, due_date, description, category, priority)
        elif choice == '2':
            task_id = int(input("Masukkan ID tugas yang akan dihapus: "))
            delete_task(task_id)
        elif choice == '3':
            task_id = int(input("Masukkan ID tugas yang terselesaikan: "))
            update_status_to_done(task_id)
        elif choice == '4':
            cari_tugas()
        elif choice == '5':
            continue
        elif choice == '6':
            print("Terima kasih telah menggunakan aplikasi Todo List. Sampai jumpa!")
            break
        else:
            update_error("Pilihan tidak valid. Silakan pilih menu yang tersedia.")

if __name__ == "__main__":
    menu() 
