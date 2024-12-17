import sqlite3
import pandas as pd
import os
from tkinter import Tk, Label, Entry, Button, Listbox, END, Frame, Scrollbar, VERTICAL, RIGHT, LEFT, Y, Menu, filedialog

# Step 1: Import CSV data into SQLite Database (with duplicates check)
def import_csv_to_db(csv_file, db_name):
    # Load CSV into DataFrame
    df = pd.read_csv(csv_file)

    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create companies table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        code TEXT PRIMARY KEY,
        company_name TEXT
    )
    ''')

    # Insert new data from CSV without duplicates
    for _, row in df.iterrows():
        code = row['code']
        company_name = row['company_name']

        # Check if the company already exists in the database
        cursor.execute('SELECT 1 FROM companies WHERE code = ?', (code,))
        if cursor.fetchone() is None:
            # Insert the new company if it does not exist
            cursor.execute('INSERT INTO companies (code, company_name) VALUES (?, ?)', (code, company_name))

    # Commit and close the connection
    conn.commit()
    conn.close()

# Step 2: Check if the database exists and load data if necessary
def check_and_load_data(db_name, csv_file):
    if not os.path.exists(db_name):
        # Database doesn't exist, load from CSV
        import_csv_to_db(csv_file, db_name)

# Step 3: Create the GUI application
def search_companies_by_keyword(keyword, code_listbox, name_listbox, db_name):
    # Clear the Listboxes
    code_listbox.delete(0, END)
    name_listbox.delete(0, END)

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Execute the query
    query = """
    SELECT code, company_name
    FROM companies
    WHERE company_name LIKE ?
    """
    cursor.execute(query, (f"%{keyword}%",))

    # Fetch and display results
    results = cursor.fetchall()
    for ticker, name in results:
        formatted_ticker = f"{ticker}.T"
        code_listbox.insert(END, formatted_ticker)
        name_listbox.insert(END, name)

    conn.close()

def load_csv_from_file(db_name):
    # Open a file dialog to select CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        # Import the selected CSV file into the database
        import_csv_to_db(file_path, db_name)

def create_gui(db_name):
    # Create the main window
    root = Tk()
    root.title("株ヤロウ")
    root.resizable(False, False)  # Disable window resizing

    # Add a menu
    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    # Create File menu
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="read CSV", command=lambda: load_csv_from_file(db_name))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    # Label
    label = Label(root, text="会社名(一部でも可)を入力")
    label.pack(pady=10)

    # Entry
    entry = Entry(root, justify='center')
    entry.pack(pady=5)

    # Button
    button = Button(root, text="Search", command=lambda: search_companies_by_keyword(entry.get(), code_listbox, name_listbox, db_name))
    button.pack(pady=5)

    # Add a frame for headers and results
    frame = Frame(root)
    frame.pack(pady=10)

    # Bind the Return key to trigger the search
    entry.bind("<Return>", lambda event: search_companies_by_keyword(entry.get(), code_listbox, name_listbox, db_name))

    # Headers
    header_code = Label(frame, text="銘柄コード", width=10, anchor='center', bg="lightgrey")
    header_code.grid(row=0, column=0)

    header_name = Label(frame, text="銘柄名", width=28, anchor='center', bg="lightgrey")
    header_name.grid(row=0, column=1)

    # Frame for listboxes and scrollbar
    listbox_frame = Frame(frame)
    listbox_frame.grid(row=1, column=0, columnspan=2)

    # Scrollbar
    scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Listboxes for separate columns
    code_listbox = Listbox(listbox_frame, width=10, height=15, justify='center', yscrollcommand=scrollbar.set)
    code_listbox.pack(side=LEFT, fill=Y)

    name_listbox = Listbox(listbox_frame, width=28, height=15, justify='left', yscrollcommand=scrollbar.set)
    name_listbox.pack(side=LEFT, fill=Y)

    # Link the scrollbar to both listboxes
    scrollbar.config(command=lambda *args: [code_listbox.yview(*args), name_listbox.yview(*args)])

    # Disable mouse wheel scrolling
    def disable_mouse_wheel(event):
        return "break"

    code_listbox.bind("<MouseWheel>", disable_mouse_wheel)
    name_listbox.bind("<MouseWheel>", disable_mouse_wheel)

    # Run the main loop
    root.mainloop()

if __name__ == "__main__":
    # File paths
    csv_file = 'T1_data.csv'  # Path to the uploaded CSV file
    db_name = 'companies.db'

    # Check if the database exists and load data if necessary
    check_and_load_data(db_name, csv_file)

    # Create and launch the GUI
    create_gui(db_name)

