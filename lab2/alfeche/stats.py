"""
File: stats.py
Computes mean, median, and mode of a set of numbers.
"""

from collections import Counter

def mean(numbers):
    """Computes the mean of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def median(numbers):
    """Computes the median of a list of numbers."""
    if not numbers:
        return 0
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    midpoint = n // 2
    if n % 2 == 1:
        return sorted_numbers[midpoint]
    else:
        return (sorted_numbers[midpoint] + sorted_numbers[midpoint - 1]) / 2

def mode(numbers):
    """Computes the mode of a list of numbers."""
    if not numbers:
        return 0
    # Use Counter to find the frequency of each number
    counts = Counter(numbers)

    # Find the maximum frequency
    max_frequency = 0
    if counts: # Check if counts is not empty
        max_frequency = max(counts.values())

    # Find the first number with the maximum frequency
    # Note: This implementation returns only one mode if there are multiple.
    for number, frequency in counts.items():
        if frequency == max_frequency:
            return number
    # Should not reach here if numbers is not empty, but added for completeness
    return 0


def main():
    """
    Gets numbers from a file specified by the user or uses a default list,
    then computes and prints the mean, median, and mode.
    """
    numbers = []
    fileName = input("Enter the file name: ") # Prompt user for file name

    try:
        # Attempt to open and read the file like in median.py
        f = open(fileName, 'r') # Use fileName
        print(f"Reading numbers from file: {fileName}") # Use fileName
        for line in f:
            words = line.split() # Split by whitespace
            for word in words:
                try:
                    numbers.append(float(word))
                except ValueError:
                    # Handle non-numeric values found in the file
                    print(f"Skipping non-numeric value in file: {word}")
        f.close() # Close the file

    except FileNotFoundError:
        # Handle case where the file does not exist
        print(f"File '{fileName}' not found.") # Use fileName
    except Exception as e:
        # Handle other potential file reading errors
        print(f"Error reading file '{fileName}': {e}") # Use fileName

    # If numbers list is still empty after attempting to read from file, use default list
    if not numbers:
        print("No valid numbers read from file or file not found. Using default list.")
        numbers = [1, 2, 3, 4, 5, 6, 4, 5, 4, 4, 4, 3, 5, 7] # Default list
    else:
        print("Successfully read numbers from file.")


    print(f"Numbers used: {numbers}")
    print(f"Mean: {mean(numbers)}")
    print(f"Median: {median(numbers)}")
    print(f"Mode: {mode(numbers)}")


if __name__ == "__main__":
    main()