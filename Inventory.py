import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3

def create_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            quantity INTEGER,
            barcode TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS serial_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            serial_number TEXT,
            note TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    conn.commit()
    conn.close()

def update_inventory_view(inventory_list, filter_text=''):
    inventory_list.delete(*inventory_list.get_children())
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    query = 'SELECT id, name, type, quantity, barcode FROM products WHERE name LIKE ? OR type LIKE ? OR barcode LIKE ?'
    for row in c.execute(query, ('%' + filter_text + '%', '%' + filter_text + '%', '%' + filter_text + '%')):
        inventory_list.insert('', 'end', values=row)
    conn.close()

def add_product(name, type, quantity, barcode, inventory_list):
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute('INSERT INTO products (name, type, quantity, barcode) VALUES (?, ?, ?, ?)',
                  (name, type, quantity, barcode))
        conn.commit()
        conn.close()
        update_inventory_view(inventory_list)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_product_details(product_id):
    detail_window = tk.Toplevel()
    detail_window.title("Product Details")

    ttk.Label(detail_window, text="Serial Numbers:").grid(row=0, column=0, padx=10, pady=5)
    serial_frame = ttk.Frame(detail_window)
    serial_frame.grid(row=1, column=0, padx=10, pady=5)
    serial_list = ttk.Treeview(serial_frame, columns=("Serial Number", "Note"), show="headings")
    serial_list.grid(row=0, column=0, sticky="nsew")
    serial_list.heading("Serial Number", text="Serial Number")
    serial_list.heading("Note", text="Note")

    def add_serial():
        serial = simpledialog.askstring("Serial Number", "Enter Serial Number:")
        note = simpledialog.askstring("Note", "Enter Note:")
        if serial:
            conn = sqlite3.connect('inventory.db')
            c = conn.cursor()
            c.execute('INSERT INTO serial_numbers (product_id, serial_number, note) VALUES (?, ?, ?)',
                      (product_id, serial, note))
            conn.commit()
            conn.close()
            update_serial_list()

    ttk.Button(detail_window, text="Add Serial Number", command=add_serial).grid(row=2, column=0, padx=10, pady=5)

    def update_serial_list():
        serial_list.delete(*serial_list.get_children())
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        query = 'SELECT id, serial_number, note FROM serial_numbers WHERE product_id = ?'
        for row in c.execute(query, (product_id,)):
            serial_list.insert('', 'end', values=(row[1], row[2]), iid=row[0])  # Correctly use database ID as iid
        conn.close()

    def on_double_click(event):
        item_id = serial_list.identify_row(event.y)
        column = serial_list.identify_column(event.x)
        if item_id and column == "#2":  # Note column
            current_value = serial_list.item(item_id, 'values')[1]
            new_value = simpledialog.askstring("Edit Note", "Enter new note:", initialvalue=current_value)
            if new_value is not None:
                conn = sqlite3.connect('inventory.db')
                c = conn.cursor()
                c.execute('UPDATE serial_numbers SET note = ? WHERE id = ?', (new_value, item_id))
                conn.commit()
                conn.close()
                update_serial_list()

    serial_list.bind("<Double-1>", on_double_click)
    
    update_serial_list()

def setup_gui():
    root = tk.Tk()
    root.title("Inventory Management System")

    # Add Product Section
    product_frame = ttk.LabelFrame(root, text="Add Product")
    product_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    ttk.Label(product_frame, text="Product Name:").grid(row=0, column=0, sticky="e")
    ttk.Label(product_frame, text="Type:").grid(row=1, column=0, sticky="e")
    ttk.Label(product_frame, text="Quantity:").grid(row=2, column=0, sticky="e")
    ttk.Label(product_frame, text="Barcode:").grid(row=3, column=0, sticky="e")
    product_name = ttk.Entry(product_frame)
    product_type = ttk.Entry(product_frame)
    product_quantity = ttk.Entry(product_frame)
    product_barcode = ttk.Entry(product_frame)
    product_name.grid(row=0, column=1)
    product_type.grid(row=1, column=1)
    product_quantity.grid(row=2, column=1)
    product_barcode.grid(row=3, column=1)
    ttk.Button(product_frame, text="Add Product", command=lambda: add_product(
        product_name.get(),
        product_type.get(),
        int(product_quantity.get()),
        product_barcode.get(),
        inventory_list
    )).grid(row=4, column=0, columnspan=2)

    # Inventory View
    inventory_frame = ttk.LabelFrame(root, text="Inventory View")
    inventory_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    inventory_list = ttk.Treeview(inventory_frame, columns=("ID", "Name", "Type", "Quantity", "Barcode"), show="headings")
    inventory_list.grid(row=0, column=0, sticky="nsew")
    inventory_list.heading("ID", text="ID")
    inventory_list.heading("Name", text="Name")
    inventory_list.heading("Type", text="Type")
    inventory_list.heading("Quantity", text="Quantity")
    inventory_list.heading("Barcode", text="Barcode")

    # Search Bar
    search_frame = ttk.LabelFrame(root, text="Search Products")
    search_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    search_entry = ttk.Entry(search_frame)
    search_entry.grid(row=0, column=0, sticky="ew")
    ttk.Button(search_frame, text="Search", command=lambda: update_inventory_view(inventory_list, search_entry.get())).grid(row=0, column=1)

    update_inventory_view(inventory_list)  # Initial update of the inventory view

    # Open details on double click in the inventory list
    inventory_list.bind("<Double-1>", lambda event: open_product_details(inventory_list.set(inventory_list.selection()[0], '#1')))

    root.mainloop()

create_db()  # Ensure database is created
setup_gui()