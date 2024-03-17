# Alamin Masharqa           ID:207358326
def validate_positive_input(prompt, max_attempts=5, timeout=60):
    attempts = 0
    while attempts < max_attempts:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        attempts += 1
    print(f"Too many invalid attempts. Waiting for {timeout} seconds.")
    # Implement waiting mechanism
