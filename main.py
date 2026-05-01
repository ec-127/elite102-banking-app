import mysql.connector
import unittest
import sys

# Connect to MySQL database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # your MySQL username
        password="Ne1015478$",  # the password you set during MySQL install
        database="banking_app"
    )

# Create tables
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            balance DECIMAL(10, 2)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_id INT,
            type ENUM('deposit', 'withdrawl'),
            amount DECIMAL (10,2),
            FOREIGN KEY (account_id) REFERENCES accounts(id)       
        )
    ''')
    # Close when done
    conn.commit()
    cursor.close()
    conn.close()

# Core Functions
def create_acct(name, init_deposit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO accounts (name, balance) VALUES ('{name}', {init_deposit})")
    conn.commit()
    account_id = cursor.lastrowid
    cursor.close()
    conn.close()
    print("Account successfully created!")
    print(f"Your account ID is: {account_id}\n")
    return {"id": account_id, "name": name, "balance": init_deposit}

def deposit(account_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE accounts SET balance = balance + {amount} WHERE id = {account_id}")
    cursor.execute(f"INSERT INTO transactions (account_id, type, amount) VALUES ({account_id}, 'deposit', {amount})")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Deposit of ${amount} successful.\n")

def withdraw(account_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT balance FROM accounts where id = {account_id}")
    row = cursor.fetchone()
    if row and row[0] >= amount:
        cursor.execute(f"UPDATE accounts SET balance = balance - {amount} WHERE id = {account_id}")
        cursor.execute(f"INSERT INTO transactions (account_id, type, amount) VALUES ({account_id}, 'withdrawl', {amount})")
        conn.commit()
        print(f"Withdrawl of ${amount} successful.\n")
    else:
        print("Insufficient funds.\n")
    conn.close()

def check_balance(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT balance FROM accounts WHERE id = {account_id}")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        print(f"Balance: ${row[0]}")
        return float(row[0])
    else:
        print("Account not found.\n")
        return None

def list_accts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, balance FROM accounts")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Balance: ${row[2]}")

# Unit Tests

class TestFunctions(unittest.TestCase):

    def test_create_acct(self):
        acct = create_acct("Bob Smith", 100)
        self.assertEqual(acct["name"], "Bob Smith")
        self.assertEqual(acct["balance"], 100)

    def test_check_balance(self):
        acct = create_acct("Amy Miller", 200)
        self.assertEqual(check_balance(acct["id"]), 200)


# Main Menu
def main_menu():
    print("Welcome to the Banking App! Please select an option below to get started.")
    while True:
        print("-----Banking App-----")
        print("1. Create account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Check balance")
        print("5. List accounts")
        print("6. Exit")

        choice = input("Enter your choice as a number: ")

        if choice == "1":
            name = input("\nEnter full name: ")
            amount = float(input("Initial deposit amount: "))
            create_acct(name, amount)
        elif choice == "2":
            acct_id = int(input("\nAccount ID: "))
            amount = float(input("Deposit amount: "))
            deposit(acct_id, amount)
        elif choice == "3":
            acct_id = int(input("\nAccount ID: "))
            amount = float(input("Withdrawl amount: "))
            withdraw(acct_id, amount)
        elif choice == "4":
            acct_id = int(input("\nAccount ID: "))
            check_balance(acct_id)
        elif choice == "5":
            print()
            list_accts()
            print()
        elif choice == "6":
            print("\nExiting program.")
            break
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    create_tables()
    if "--test" in sys.argv:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestFunctions)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    else:
        main_menu()