import tkinter as tk
from tkinter import messagebox, ttk
from firstpbl import BankManagementSystem, Account, InvalidAccountError, InvalidPINError, InvalidAmountError, InsufficientBalanceError


class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("500x500")
        self.bank = BankManagementSystem()
        self.current_account = None

        self.main_menu()

    # Clear all widgets
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ================= MAIN MENU =================
    def main_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="🏦 Bank Management System", font=("Arial", 20, "bold")).pack(pady=30)

        ttk.Button(self.root, text="Create New Account", command=self.create_account_menu, width=30).pack(pady=10)
        ttk.Button(self.root, text="Login to Account", command=self.login_menu, width=30).pack(pady=10)
        ttk.Button(self.root, text="View All Accounts (Admin)", command=self.admin_view, width=30).pack(pady=10)
        ttk.Button(self.root, text="Exit", command=self.root.quit, width=30).pack(pady=10)

    # ================= CREATE ACCOUNT =================
    def create_account_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="🧾 Create New Account", font=("Arial", 16, "bold")).pack(pady=20)

        name_label = tk.Label(self.root, text="Full Name:")
        name_label.pack()
        name_entry = ttk.Entry(self.root, width=40)
        name_entry.pack()

        pin_label = tk.Label(self.root, text="Set 4-digit PIN:")
        pin_label.pack()
        pin_entry = ttk.Entry(self.root, width=40, show="*")
        pin_entry.pack()

        deposit_label = tk.Label(self.root, text="Initial Deposit (₹):")
        deposit_label.pack()
        deposit_entry = ttk.Entry(self.root, width=40)
        deposit_entry.pack()

        def create_account():
            name = name_entry.get().strip()
            pin = pin_entry.get().strip()
            deposit = float(deposit_entry.get() or 0)

            if not name or len(pin) != 4 or not pin.isdigit():
                messagebox.showerror("Error", "Please enter valid name and 4-digit PIN.")
                return

            try:
                acc_num = self.bank.create_account(name, pin, deposit)
                messagebox.showinfo("Success", f"Account created!\nYour Account No: {acc_num}")
                self.main_menu()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.root, text="Create Account", command=create_account).pack(pady=15)
        ttk.Button(self.root, text="Back", command=self.main_menu).pack()

    # ================= LOGIN =================
    def login_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="🔐 Account Login", font=("Arial", 16, "bold")).pack(pady=20)

        acc_label = tk.Label(self.root, text="Account Number:")
        acc_label.pack()
        acc_entry = ttk.Entry(self.root, width=40)
        acc_entry.pack()

        pin_label = tk.Label(self.root, text="PIN:")
        pin_label.pack()
        pin_entry = ttk.Entry(self.root, width=40, show="*")
        pin_entry.pack()

        def login():
            acc_num = acc_entry.get().strip()
            pin = pin_entry.get().strip()
            try:
                account = self.bank.get_account(acc_num, pin)
                self.current_account = account
                messagebox.showinfo("Welcome", f"Login successful!\nWelcome {account.name}")
                self.account_menu()
            except (InvalidAccountError, InvalidPINError) as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.root, text="Login", command=login).pack(pady=15)
        ttk.Button(self.root, text="Back", command=self.main_menu).pack()

    # ================= ACCOUNT MENU =================
    def account_menu(self):
        self.clear_screen()
        acc = self.current_account

        tk.Label(self.root, text=f"💳 Welcome {acc.name}", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text=f"Account No: {acc.account_number}", font=("Arial", 12)).pack()
        tk.Label(self.root, text=f"Balance: ₹{acc.balance:.2f}", font=("Arial", 12)).pack(pady=10)

        ttk.Button(self.root, text="Deposit Money", command=self.deposit_menu, width=30).pack(pady=5)
        ttk.Button(self.root, text="Withdraw Money", command=self.withdraw_menu, width=30).pack(pady=5)
        ttk.Button(self.root, text="View Transactions", command=self.transactions_menu, width=30).pack(pady=5)
        ttk.Button(self.root, text="Check Balance", command=lambda: messagebox.showinfo("Balance", f"Your Balance: ₹{acc.balance:.2f}"), width=30).pack(pady=5)
        ttk.Button(self.root, text="Logout", command=self.main_menu, width=30).pack(pady=20)

    # ================= DEPOSIT =================
    def deposit_menu(self):
        self.clear_screen()
        acc = self.current_account
        tk.Label(self.root, text="💰 Deposit Money", font=("Arial", 16, "bold")).pack(pady=20)

        amt_entry = ttk.Entry(self.root, width=40)
        amt_entry.pack(pady=10)
        amt_entry.insert(0, "Enter amount")

        def deposit():
            try:
                amount = float(amt_entry.get())
                acc.deposit(amount)
                self.bank.save_data()
                messagebox.showinfo("Success", f"Deposited ₹{amount:.2f}\nNew Balance: ₹{acc.balance:.2f}")
                self.account_menu()
            except (InvalidAmountError, ValueError):
                messagebox.showerror("Error", "Invalid amount entered.")

        ttk.Button(self.root, text="Deposit", command=deposit).pack(pady=15)
        ttk.Button(self.root, text="Back", command=self.account_menu).pack()

    # ================= WITHDRAW =================
    def withdraw_menu(self):
        self.clear_screen()
        acc = self.current_account
        tk.Label(self.root, text="🏧 Withdraw Money", font=("Arial", 16, "bold")).pack(pady=20)

        amt_entry = ttk.Entry(self.root, width=40)
        amt_entry.pack(pady=10)
        amt_entry.insert(0, "Enter amount")

        def withdraw():
            try:
                amount = float(amt_entry.get())
                acc.withdraw(amount)
                self.bank.save_data()
                messagebox.showinfo("Success", f"Withdrawn ₹{amount:.2f}\nNew Balance: ₹{acc.balance:.2f}")
                self.account_menu()
            except (InvalidAmountError, InsufficientBalanceError, ValueError) as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(self.root, text="Withdraw", command=withdraw).pack(pady=15)
        ttk.Button(self.root, text="Back", command=self.account_menu).pack()

    # ================= TRANSACTIONS =================
    def transactions_menu(self):
        self.clear_screen()
        acc = self.current_account
        tk.Label(self.root, text="📜 Transaction History", font=("Arial", 16, "bold")).pack(pady=15)

        tree = ttk.Treeview(self.root, columns=("date", "type", "amount", "balance"), show='headings', height=10)
        tree.pack(pady=10, fill="x")
        tree.heading("date", text="Date/Time")
        tree.heading("type", text="Type")
        tree.heading("amount", text="Amount")
        tree.heading("balance", text="Balance")

        for t in acc.transactions[-10:]:
            tree.insert("", tk.END, values=(t["date"], t["type"], f"₹{t['amount']:.2f}", f"₹{t['balance']:.2f}"))

        ttk.Button(self.root, text="Back", command=self.account_menu).pack(pady=10)

    # ================= ADMIN VIEW =================
    def admin_view(self):
        self.clear_screen()
        tk.Label(self.root, text="👑 All Accounts (Admin)", font=("Arial", 16, "bold")).pack(pady=15)

        tree = ttk.Treeview(self.root, columns=("acc", "name", "type", "bal"), show='headings')
        tree.pack(pady=10, fill="x")
        tree.heading("acc", text="Account No")
        tree.heading("name", text="Name")
        tree.heading("type", text="Type")
        tree.heading("bal", text="Balance (₹)")

        for acc in self.bank.accounts.values():
            tree.insert("", tk.END, values=(acc.account_number, acc.name, acc.account_type, f"{acc.balance:.2f}"))

        ttk.Button(self.root, text="Back", command=self.main_menu).pack(pady=15)


# MAIN EXECUTION
if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
