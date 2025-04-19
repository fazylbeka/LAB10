import csv
import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="postgres", user="postgres", password="Biba2006", host="localhost"
    )

def create_table():
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                phone VARCHAR(20) UNIQUE
            );
        """)
        connection.commit()
        print("Table created successfully.")
    except Exception as error:
        print(f"Error creating table: {error}")
    finally:
        cursor.close()
        connection.close()

def insert_data_from_csv(file_name):
    try:
        connection = connect_db()
        cursor = connection.cursor()
        with open(file_name, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                if len(row) < 3:
                    continue
                first_name, last_name, phone = row
                cursor.execute("SELECT * FROM phonebook WHERE phone = %s", (phone,))
                if cursor.fetchone():
                    print(f"Phone number {phone} already exists!")
                else:
                    cursor.execute("""
                        INSERT INTO phonebook (first_name, last_name, phone)
                        VALUES (%s, %s, %s)
                    """, (first_name, last_name, phone))
        connection.commit()
        print("Data inserted successfully from CSV!")
    except Exception as error:
        print(f"Error inserting data from CSV: {error}")
    finally:
        cursor.close()
        connection.close()

def insert_data_from_console():
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    phone = input("Enter phone number: ").strip()

    if not first_name or not phone:
        print("First name and phone are required!")
        return

    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phonebook WHERE phone = %s", (phone,))
        if cursor.fetchone():
            print(f"Phone number {phone} already exists!")
        else:
            cursor.execute("""
                INSERT INTO phonebook (first_name, last_name, phone)
                VALUES (%s, %s, %s)
            """, (first_name, last_name, phone))
            connection.commit()
            print("Data inserted successfully!")
    except Exception as error:
        print(f"Error inserting data from console: {error}")
    finally:
        cursor.close()
        connection.close()

def update_data(username, new_first_name=None, new_phone=None):
    if not new_first_name and not new_phone:
        print("No new data provided for update.")
        return

    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phonebook WHERE first_name = %s", (username,))
        if not cursor.fetchone():
            print(f"User {username} does not exist.")
            return

        if new_first_name:
            cursor.execute("UPDATE phonebook SET first_name = %s WHERE first_name = %s", (new_first_name, username))
        if new_phone:
            cursor.execute("UPDATE phonebook SET phone = %s WHERE first_name = %s", (new_phone, new_first_name or username))
        connection.commit()
        print(f"Data updated for {username}!")
    except Exception as error:
        print(f"Error updating data: {error}")
    finally:
        cursor.close()
        connection.close()

def query_data(filter_type=None, value=None):
    try:
        connection = connect_db()
        cursor = connection.cursor()
        if filter_type == "name":
            cursor.execute("SELECT * FROM phonebook WHERE first_name = %s", (value,))
        elif filter_type == "phone":
            cursor.execute("SELECT * FROM phonebook WHERE phone = %s", (value,))
        else:
            cursor.execute("SELECT * FROM phonebook")
        rows = cursor.fetchall()
        if not rows:
            print("No data found.")
        for row in rows:
            print(row)
    except Exception as error:
        print(f"Error querying data: {error}")
    finally:
        cursor.close()
        connection.close()

def delete_data(identifier, value):
    try:
        connection = connect_db()
        cursor = connection.cursor()

        if identifier == "username":
            cursor.execute("DELETE FROM phonebook WHERE first_name = %s RETURNING *", (value,))
        elif identifier == "phone":
            cursor.execute("DELETE FROM phonebook WHERE phone = %s RETURNING *", (value,))
        else:
            print("Invalid identifier.")
            return

        deleted = cursor.fetchone()
        if deleted:
            connection.commit()
            print(f"Deleted: {deleted}")
        else:
            print(f"No entry found with {identifier} = {value}")
    except Exception as error:
        print(f"Error deleting data: {error}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    while True:
        print("\nPhoneBook Menu:")
        print("1. Create table")
        print("2. Insert data from CSV")
        print("3. Insert data from console")
        print("4. Update data")
        print("5. Query data")
        print("6. Delete data")
        print("7. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_table()
        elif choice == "2":
            file_name = input("Enter CSV file name: ")
            insert_data_from_csv(file_name)
        elif choice == "3":
            insert_data_from_console()
        elif choice == "4":
            username = input("Enter username to update: ")
            new_first_name = input("Enter new first name (or press Enter to skip): ").strip()
            new_phone = input("Enter new phone number (or press Enter to skip): ").strip()
            update_data(username, new_first_name or None, new_phone or None)
        elif choice == "5":
            filter_type = input("Filter by 'name' or 'phone' (or press Enter for all): ").strip()
            value = input(f"Enter {filter_type}: ").strip() if filter_type in ["name", "phone"] else None
            query_data(filter_type or None, value or None)
        elif choice == "6":
            identifier = input("Delete by 'username' or 'phone': ").strip()
            value = input(f"Enter {identifier}: ").strip()
            delete_data(identifier, value)
        elif choice == "7":
            print("Exiting PhoneBook. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")