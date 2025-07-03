'''
Alfeche, paul Janric E.
03-07-2025
'''


import sqlite3

def list_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def print_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    col_names = [description[0] for description in cursor.description]
    print(f"\nTable: {table_name}")
    print(" | ".join(col_names))
    print("-" * 40)
    for row in rows:
        print(" | ".join(str(item) for item in row))

def main():
    db_path = "ColonialAdventuresTours.db"  # <-- corrected filename
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = list_tables(cursor)
    if not tables:
        print("No tables found in the database.")
        return

    print("Available tables:")
    for idx, table in enumerate(tables, 1):
        print(f"{idx}. {table}")

    choice = input("Enter the number of the table to display: ")
    try:
        table_idx = int(choice) - 1
        if 0 <= table_idx < len(tables):
            print_table(cursor, tables[table_idx])
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")

    conn.close()

if __name__ == "__main__":
    main()