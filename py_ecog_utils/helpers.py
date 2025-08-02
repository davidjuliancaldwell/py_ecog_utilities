import re

def find_first_number_in_list_of_strings(string_list):
    """
    Finds the first number encountered in a list of strings.

    Args:
        string_list: A list of strings.

    Returns:
        The first number found as an int, or None if no number is found.
    """
    for s in string_list:
        match = re.search(r'\d+', s)  # Search for one or more digits
        if match:
            return int(match.group(0))  # Return the matched number
    return None

def numerical_sort_key(filename):
    # Extract numbers from the filename and convert to int for numerical comparison
    parts = [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', filename)]
    return parts