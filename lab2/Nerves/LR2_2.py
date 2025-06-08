def main():
    filename = input("Enter the filename: ")

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            if not lines:
                print("The file is empty.")
                return
    except FileNotFoundError:
        print("File not found.")
        return

    print(f"\nThe file has {len(lines)} lines.")
    
    while True:
        try:
            line_number = int(input("Enter a line number (0 to quit): "))
            if line_number == 0:
                print("Exiting program.")
                break
            elif 1 <= line_number <= len(lines):
                print(f"Line {line_number}: {lines[line_number - 1]}")
            else:
                print("Line number out of range.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
