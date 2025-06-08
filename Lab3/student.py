"""
File: student.py
Resources to manage a student's name and test scores.
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


def main():
    """A simple test."""
    student1 = Student("Ken", 5)
    student2 = Student("Ken", 5)
    student3 = Student("Alice", 4)
    student4 = Student("Bob", 3)

    print("Testing initial students:")
    print(student1)
    print(student3)

    print("\nTesting comparison operators:")
    print(f"'{student1.getName()}' == '{student2.getName()}': {student1 == student2}") # Test equality
    print(f"'{student1.getName()}' == '{student3.getName()}': {student1 == student3}") # Test equality
    print(f"'{student3.getName()}' < '{student1.getName()}': {student3 < student1}")   # Test less than
    print(f"'{student1.getName()}' < '{student3.getName()}': {student1 < student3}")   # Test less than
    print(f"'{student1.getName()}' >= '{student2.getName()}': {student1 >= student2}") # Test greater than or equal to
    print(f"'{student1.getName()}' >= '{student4.getName()}': {student1 >= student4}") # Test greater than or equal to
    print(f"'{student3.getName()}' >= '{student1.getName()}': {student3 >= student1}") # Test greater than or equal to


if __name__ == "__main__":
    main()


