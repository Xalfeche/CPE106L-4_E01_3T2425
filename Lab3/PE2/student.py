"""
Alfeche, Paul Janric E.
07-01-2025
"""

class Student(object):
    """Represents a student."""

    def __init__(self, name, number):
        """All scores are initially 0."""
        self.name = name
        self.scores = []
        for count in range(number):
            self.scores.append(0)

    def getName(self):
        """Returns the student's name."""
        return self.name

    def setScore(self, i, score):
        """Resets the ith score, counting from 1."""
        self.scores[i - 1] = score

    def getScore(self, i):
        """Returns the ith score, counting from 1."""
        return self.scores[i - 1]

    def getAverage(self):
        """Returns the average score."""
        # Corrected attribute name from _scores to scores
        if not self.scores:
            return 0
        return sum(self.scores) / len(self.scores)

    def getHighScore(self):
        """Returns the highest score."""
        if not self.scores:
            return 0 # Or handle as appropriate for an empty list
        return max(self.scores)

    def __str__(self):
        """Returns the string representation of the student."""
        return "Name: " + self.name  + "\nScores: " + \
               " ".join(map(str, self.scores))

    # Added comparison methods
    def __eq__(self, other):
        """Tests for equality based on name."""
        if self is other:
            return True
        if type(self) != type(other):
            return False
        return self.name == other.name

    def __lt__(self, other):
        """Tests for less than based on name."""
        if type(self) != type(other):
            return False # Cannot compare different types
        return self.name < other.name

    def __ge__(self, other):
        """Tests for greater than or equal to based on name."""
        if type(self) != type(other):
            return False # Cannot compare different types
        return self.name >= other.name


import random
import string

def random_name(length=5):
    """Generate a random name with the given length."""
    return ''.join(random.choices(string.ascii_uppercase, k=1) + 
                   random.choices(string.ascii_lowercase, k=length-1))

def main():
    # Create a list of students with fixed names and random scores
    names = ["Ken", "Alice", "Bob", "Zara", "Mike"]
    students = []
    for name in names:
        num_scores = random.randint(2, 6)
        student = Student(name, num_scores)
        # Assign random score
        for i in range(1, num_scores + 1):
            student.setScore(i, random.randint(50, 100))
        students.append(student)

    print("\nOriginal list of students:")
    for s in students:
        print(s)
        print("-" * 20)

    # Shuffle the list
    random.shuffle(students)
    print("\nShuffled list of students:")
    for s in students:
        print(s)
        print("-" * 20)

    # Sort the list
    students.sort()
    print("\nSorted list of students:")
    for s in students:
        print(s)
        print("-" * 20)

if __name__ == "__main__":
    main()


