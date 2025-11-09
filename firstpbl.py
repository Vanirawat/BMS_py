import json
import os
from datetime import datetime
from typing import Dict, List, Optional


# Custom Exceptions
class InsufficientBalanceError(Exception):
    """Raised when withdrawal amount exceeds available balance"""
    pass


class InvalidAccountError(Exception):
    """Raised when account number doesn't exist"""
    pass


class InvalidPINError(Exception):
    """Raised when PIN is incorrect"""
    pass


class InvalidAmountError(Exception):
    """Raised when amount is invalid (negative or zero)"""
    pass


# Account Class
class Account:
    """Represents a bank account with all its properties and methods"""

    def __init__(self, account_number: str, name: str, pin: str,
               balance: float = 0.0, account_type: str = "Savings"):
        self.account_number = account_number
        self.name = name
        self.pin = pin
        self.balance = balance
        self.account_type = account_type
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions: List[Dict] = []

    def deposit(self, amount: float) -> None:
        """Deposit money into the account"""
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")

        self.balance += amount
        self._add_transaction("Deposit", amount, self.balance)

    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account"""
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")

        if amount > self.balance:
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: ₹{self.balance:.2f}"
            )

        self.balance -= amount
        self._add_transaction("Withdrawal", amount, self.balance)

    def calculate_interest(self, rate: float = 3.5) -> float:
        """Calculate interest on current balance"""
        interest = (self.balance * rate) / 100
        return interest

    def add_interest(self, rate: float = 3.5) -> None:
        """Add interest to the account"""
        interest = self.calculate_interest(rate)
        self.balance += interest
        self._add_transaction("Interest Credit", interest, self.balance)

    def _add_transaction(self, trans_type: str, amount: float, balance: float) -> None:
        """Add transaction to history"""
        transaction = {
            "type": trans_type,
            "amount": amount,
            "balance": balance,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transactions.append(transaction)

    def get_details(self) -> Dict:
        """Return account details as dictionary"""
        return {
            "account_number": self.account_number,
            "name": self.name,
            "pin": self.pin,
            "balance": self.balance,
            "account_type": self.account_type,
            "creation_date": self.creation_date,
            "transactions": self.transactions
        }

    def verify_pin(self, pin: str) -> bool:
        """Verify if provided PIN matches"""
        return self.pin == pin

    def update_pin(self, new_pin: str) -> None:
        """Update account PIN"""
        self.pin = new_pin

    def __str__(self) -> str:
        return (f"Account: {self.account_number} | Name: {self.name} | "
                f"Type: {self.account_type} | Balance: ₹{self.balance:.2f}")


# Bank Management System Class
class BankManagementSystem:
    """Main class for managing all banking operations"""

    def __init__(self, data_file: str = "bank_data.json"):
        self.data_file = data_file
        self.accounts: Dict[str, Account] = {}
        self.load_data()

    def load_data(self) -> None:
        """Load account data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    for acc_num, acc_data in data.items():
                        account = Account(
                            acc_data['account_number'],
                            acc_data['name'],
                            acc_data['pin'],
                            acc_data['balance'],
                            acc_data['account_type']
                        )
                        account.creation_date = acc_data['creation_date']
                        account.transactions = acc_data['transactions']
                        self.accounts[acc_num] = account
                print(f"✓ Loaded {len(self.accounts)} accounts from database")
            except Exception as e:
                print(f"Error loading data: {e}")
        else:
            print("No existing database found. Starting fresh.")

    def save_data(self) -> None:
        """Save all account data to file"""
        try:
            data = {acc_num: acc.get_details()
                    for acc_num, acc in self.accounts.items()}
            with open(self.data_file, 'w') as file:
                json.dump(data, file, indent=4)
            print("✓ Data saved successfully")
        except Exception as e:
            print(f"Error saving data: {e}")

    def generate_account_number(self) -> str:
        """Generate unique account number"""
        if not self.accounts:
            return "ACC1001"

        last_num = max([int(acc[3:]) for acc in self.accounts.keys()])
        return f"ACC{last_num + 1}"

    def create_account(self, name: str, pin: str,
                       initial_deposit: float = 0.0,
                       account_type: str = "Savings") -> str:
        """Create a new bank account"""
        try:
            if initial_deposit < 0:
                raise InvalidAmountError("Initial deposit cannot be negative")

            account_number = self.generate_account_number()
            account = Account(account_number, name, pin, initial_deposit, account_type)

            if initial_deposit > 0:
                account._add_transaction("Initial Deposit", initial_deposit, initial_deposit)

            self.accounts[account_number] = account
            self.save_data()
            return account_number

        except Exception as e:
            raise Exception(f"Failed to create account: {e}")

    def get_account(self, account_number: str, pin: str) -> Account:
        """Retrieve account after PIN verification"""
        if account_number not in self.accounts:
            raise InvalidAccountError("Account not found")

        account = self.accounts[account_number]
        if not account.verify_pin(pin):
            raise InvalidPINError("Incorrect PIN")

        return account

    def delete_account(self, account_number: str, pin: str) -> None:
        """Delete an account after PIN verification"""
        account = self.get_account(account_number, pin)
        del self.accounts[account_number]
        self.save_data()

    def display_all_accounts(self) -> None:
        """Display summary of all accounts"""
        if not self.accounts:
            print("No accounts found in the system.")
            return

        print("\n" + "=" * 80)
        print(f"{'Account No':<15} {'Name':<25} {'Type':<15} {'Balance':<15}")
        print("=" * 80)
        for account in self.accounts.values():
            print(f"{account.account_number:<15} {account.name:<25} "
                  f"{account.account_type:<15} ₹{account.balance:<14.2f}")
        print("=" * 80)


# UI and Menu System
class BankUI:
    """User Interface for the Bank Management System"""

    def __init__(self):
        self.bank = BankManagementSystem()

    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self, title: str):
        """Display formatted header"""
        print("\n" + "=" * 60)
        print(f"{title:^60}")
        print("=" * 60)

    def main_menu(self):
        """Display main menu"""
        while True:
            self.display_header("BANK MANAGEMENT SYSTEM")
            print("\n1. Create New Account")
            print("2. Login to Account")
            print("3. View All Accounts (Admin)")
            print("4. Exit")

            try:
                choice = input("\nEnter your choice (1-4): ").strip()

                if choice == '1':
                    self.create_account_menu()
                elif choice == '2':
                    self.login_menu()
                elif choice == '3':
                    self.admin_view()
                elif choice == '4':
                    print("\nThank you for using Bank Management System!")
                    break
                else:
                    print("Invalid choice. Please try again.")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                input("\nPress Enter to continue...")

    def create_account_menu(self):
        """Menu for creating new account"""
        self.display_header("CREATE NEW ACCOUNT")

        try:
            name = input("\nEnter account holder name: ").strip()
            if not name:
                raise ValueError("Name cannot be empty")

            pin = input("Set 4-digit PIN: ").strip()
            if len(pin) != 4 or not pin.isdigit():
                raise ValueError("PIN must be 4 digits")

            account_type = input("Account type (Savings/Current) [Savings]: ").strip()
            if not account_type:
                account_type = "Savings"

            initial_deposit = float(input("Initial deposit amount (₹): ") or 0)

            account_number = self.bank.create_account(
                name, pin, initial_deposit, account_type
            )

            print(f"\n✓ Account created successfully!")
            print(f"Account Number: {account_number}")
            print(f"Please remember your account number and PIN.")

        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def login_menu(self):
        """Login to account"""
        self.display_header("ACCOUNT LOGIN")

        try:
            account_number = input("\nEnter Account Number: ").strip()
            pin = input("Enter PIN: ").strip()

            account = self.bank.get_account(account_number, pin)
            print(f"\n✓ Login successful! Welcome, {account.name}")
            self.account_menu(account)

        except (InvalidAccountError, InvalidPINError) as e:
            print(f"Login failed: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def account_menu(self, account: Account):
        """Menu for logged-in account"""
        while True:
            self.display_header(f"ACCOUNT MENU - {account.name}")
            print(f"\nAccount Number: {account.account_number}")
            print(f"Current Balance: ₹{account.balance:.2f}")
            print("\n1. Deposit Money")
            print("2. Withdraw Money")
            print("3. Check Balance")
            print("4. View Account Details")
            print("5. View Transaction History")
            print("6. Calculate Interest")
            print("7. Update PIN")
            print("8. Delete Account")
            print("9. Logout")

            try:
                choice = input("\nEnter your choice (1-9): ").strip()

                if choice == '1':
                    self.deposit_menu(account)
                elif choice == '2':
                    self.withdraw_menu(account)
                elif choice == '3':
                    self.check_balance(account)
                elif choice == '4':
                    self.view_account_details(account)
                elif choice == '5':
                    self.view_transaction_history(account)
                elif choice == '6':
                    self.calculate_interest_menu(account)
                elif choice == '7':
                    self.update_pin_menu(account)
                elif choice == '8':
                    if self.delete_account_menu(account):
                        break
                elif choice == '9':
                    print("Logging out...")
                    break
                else:
                    print("Invalid choice. Please try again.")

                input("\nPress Enter to continue...")

            except Exception as e:
                print(f"Error: {e}")
                input("\nPress Enter to continue...")

    def deposit_menu(self, account: Account):
        """Handle deposit operation"""
        try:
            amount = float(input("\nEnter amount to deposit (₹): "))
            account.deposit(amount)
            self.bank.save_data()
            print(f"✓ ₹{amount:.2f} deposited successfully")
            print(f"New Balance: ₹{account.balance:.2f}")
        except InvalidAmountError as e:
            print(f"Error: {e}")
        except ValueError:
            print("Invalid amount entered")

    def withdraw_menu(self, account: Account):
        """Handle withdrawal operation"""
        try:
            amount = float(input("\nEnter amount to withdraw (₹): "))
            account.withdraw(amount)
            self.bank.save_data()
            print(f"✓ ₹{amount:.2f} withdrawn successfully")
            print(f"New Balance: ₹{account.balance:.2f}")
        except (InvalidAmountError, InsufficientBalanceError) as e:
            print(f"Error: {e}")
        except ValueError:
            print("Invalid amount entered")

    def check_balance(self, account: Account):
        """Display current balance"""
        print(f"\nCurrent Balance: ₹{account.balance:.2f}")

    def view_account_details(self, account: Account):
        """Display detailed account information"""
        print(f"\n{'=' * 60}")
        print(f"Account Number: {account.account_number}")
        print(f"Account Holder: {account.name}")
        print(f"Account Type: {account.account_type}")
        print(f"Current Balance: ₹{account.balance:.2f}")
        print(f"Account Created: {account.creation_date}")
        print(f"Total Transactions: {len(account.transactions)}")
        print(f"{'=' * 60}")

    def view_transaction_history(self, account: Account):
        """Display transaction history"""
        if not account.transactions:
            print("\nNo transactions found.")
            return

        print(f"\n{'=' * 80}")
        print(f"{'Date/Time':<20} {'Type':<20} {'Amount':<15} {'Balance':<15}")
        print(f"{'=' * 80}")

        for trans in account.transactions[-10:]:  # Show last 10 transactions
            print(f"{trans['date']:<20} {trans['type']:<20} "
                  f"₹{trans['amount']:<14.2f} ₹{trans['balance']:<14.2f}")

        print(f"{'=' * 80}")
        print(f"(Showing last {min(10, len(account.transactions))} transactions)")

    def calculate_interest_menu(self, account: Account):
        """Calculate and optionally add interest"""
        try:
            rate = float(input("\nEnter interest rate (%) [3.5]: ") or 3.5)
            interest = account.calculate_interest(rate)

            print(f"\nCalculated Interest: ₹{interest:.2f}")

            add = input("Do you want to add this interest to account? (y/n): ").lower()
            if add == 'y':
                account.add_interest(rate)
                self.bank.save_data()
                print(f"✓ Interest added successfully")
                print(f"New Balance: ₹{account.balance:.2f}")

        except ValueError:
            print("Invalid rate entered")

    def update_pin_menu(self, account: Account):
        """Update account PIN"""
        try:
            old_pin = input("\nEnter current PIN: ").strip()
            if not account.verify_pin(old_pin):
                raise InvalidPINError("Incorrect current PIN")

            new_pin = input("Enter new 4-digit PIN: ").strip()
            if len(new_pin) != 4 or not new_pin.isdigit():
                raise ValueError("PIN must be 4 digits")

            confirm_pin = input("Confirm new PIN: ").strip()
            if new_pin != confirm_pin:
                raise ValueError("PINs don't match")

            account.update_pin(new_pin)
            self.bank.save_data()
            print("✓ PIN updated successfully")

        except (InvalidPINError, ValueError) as e:
            print(f"Error: {e}")

    def delete_account_menu(self, account: Account) -> bool:
        """Delete account after confirmation"""
        try:
            print("\n⚠ WARNING: This action cannot be undone!")
            confirm = input("Type 'DELETE' to confirm account deletion: ").strip()

            if confirm != 'DELETE':
                print("Account deletion cancelled")
                return False

            pin = input("Enter PIN to confirm: ").strip()
            self.bank.delete_account(account.account_number, pin)
            print("✓ Account deleted successfully")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def admin_view(self):
        """Display all accounts (admin function)"""
        self.display_header("ALL ACCOUNTS")
        self.bank.display_all_accounts()


# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("WELCOME TO BANK MANAGEMENT SYSTEM".center(60))
    print("=" * 60)
    print("\nInitializing system...")

    ui = BankUI()
    ui.main_menu()

    print("\nGoodbye!")


