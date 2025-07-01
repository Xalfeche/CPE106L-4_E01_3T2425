"""
File: bank.py
This module defines the Bank class.
"""
import pickle

from savingsaccount import SavingsAccount

class Bank:
    """This class represents a bank as a collection of savings accounts.
    An optional file name is also associated
    with the bank, to allow transfer of accounts to and
    from permanent file storage."""

    def __init__(self, fileName = None):
        """Creates a new dictionary to hold the accounts.
        If a file name is provided, loads the accounts from
        a file of pickled accounts."""
        self.accounts = {}
        self.fileName = fileName
        if fileName != None:
            fileObj = open(fileName, 'rb')
            while True:
                try:
                    account = pickle.load(fileObj)
                    self.add(account)
                except Exception:
                    fileObj.close()
                    break

    def __str__(self):
        """Returns the string representation of the bank with accounts sorted by name."""
        # Sort accounts by name using the __lt__ method in SavingsAccount
        sorted_accounts = sorted(self.accounts.values())
        return "\n".join(map(str, sorted_accounts))

    def makeKey(self, name, pin):
        """Returns a key for the account."""
        return name + "/" + pin

    def add(self, account):
        """Adds the account to the bank."""
        key = self.makeKey(account.getName(), account.getPin())
        self.accounts[key] = account

    def remove(self, name, pin):
        """Removes the account from the bank and
        and returns it, or None if the account does
        not exist."""
        key = self.makeKey(name, pin)
        return self.accounts.pop(key, None)

    def get(self, name, pin):
        """Returns the account from the bank,
        or returns None if the account does
        not exist."""
        key = self.makeKey(name, pin)
        return self.accounts.get(key, None)

    def computeInterest(self):
        """Computes and returns the interest on
        all accounts."""
        total = 0
        for account in self.accounts.values():
            total += account.computeInterest()
        return total

    def getKeys(self):
        """Returns a sorted list of keys."""
        return []

    def save(self, fileName = None):
        """Saves pickled accounts to a file.  The parameter
        allows the user to change file names."""
        if fileName != None:
            self.fileName = fileName
        elif self.fileName == None:
            return
        fileObj = open(self.fileName, 'wb')
        for account in self.accounts.values():
            pickle.dump(account, fileObj)
        fileObj.close()


# ===== TEST DEMONSTRATION =====
def test_sorted_accounts():
    """Test function to demonstrate accounts are sorted by name."""
    print("=== Testing Account Sorting by Name ===\n")
    
    # Create a bank
    bank = Bank()
    
    # Add accounts in non-alphabetical order
    bank.add(SavingsAccount("Zoe", "1001", 500.0))
    bank.add(SavingsAccount("Alice", "1002", 750.0))
    bank.add(SavingsAccount("Mark", "1003", 300.0))
    bank.add(SavingsAccount("Bob", "1004", 900.0))
    
    print("\nBank accounts (should be sorted alphabetically by name):")
    print(bank)
    
    print("\n" + "="*50)
if __name__ == "__main__":
    test_sorted_accounts()