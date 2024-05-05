def find_lines_with_words(filename, target_words):
    found_lines = []  # Define the variable "found_lines" as an empty list
    line_counter = 0  # Initialize a line counter variable

    with open(filename, 'r') as file:
        for line in file:
            line_counter += 1  # Increment the line counter
            for word in target_words:
                if word in line:
                    found_lines.append((word, line_counter))  # Append the word, line number, and line itself
    
    return found_lines

def main():
    filename = "C:/Users/tedlj/OneDrive/Desktop/output7.2.0-7.2.3/unpacked_Signal_7.2.3_Apkpure/classes6.c"
    target_words = ['registration']
    
    found_lines = find_lines_with_words(filename, target_words)
    print(found_lines)
    print("\n")

if __name__ == "__main__":
    main()