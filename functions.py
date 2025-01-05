import unicodedata
import string
import re
def read_txt(input_path):
    """Reads text from a file

    Args:
        input_path (str): Path to the file

    Returns:
        str: Text from the file
    """
    with open(input_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_txt(output_path, text):
    """Writes text to a file

    Args:
        output_path (str): Path to the file
        text (str): Text to write to the file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)

def write_txt_list(output_path, list):
    """Writes a list of strings to a file

    Args:
        output_path (str): Path to the file
        list (list): List of strings to write to the file
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        for list in list:
            file.write(list + '\n')

def remove_diacritics(text):
    """Remove diacritics from text

    Args:
        text (str): Text to remove diacritics from

    Returns:
        str: Text without diacritics
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def remove_punctuation(text):
    """This removes punctuation from text

    Args:
        text (str): Text to remove punctuation from

    Returns:
        text (str): Text without punctuation
    """
    punctuation = string.punctuation + "„“‚‘–…«»" # Punctuation covering czech language
    return text.translate(str.maketrans('', '', punctuation))

def preprocess_txt(input_path, output_path):
    """Preprocesses text by removing diacritics and punctuation

    Args:
        input_path (str): Path to the input file
        output_path (str): Path to the output file

    Returns:
        str: Preprocessed text
    """
    text = read_txt(input_path)
    text = remove_diacritics(text).lower()
    text = remove_punctuation(text)
    text = delete_stop_words(text)
    write_txt(output_path, text)
    return text

def split_questions_answers(text):
    """Split text into questions and answers

    Args:
        text (str): Text to split

    Returns:
        list: List of questions and answers
    """
    return text.strip().split('\n\n')

def generate_word_ngrams(text, n, output_path = None):
    """Generate word n-grams from text

    Args:
        text (str): Text to generate n-grams from
        n (int): Number of words in each n-gram
        output_path (str): Path to the output file

    Returns:
        list: List of n-grams
    """
    words = text.split()
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    if output_path is not None:
        write_txt_list(output_path,ngrams)
    return ngrams

def delete_stop_words(text):
    """Delete stop words from text

    Args:
        text (str): Text to delete stop words from

    Returns:
        str: Text without stop words
    """
    stop_words = read_txt("input/stop_words.txt").split()
    # Pattern to match words
    pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in stop_words) + r')\b', re.IGNORECASE)

    # Function to replace stop words
    def remove_stop_words(match):
        return ''  # Replace with an empty string or any other placeholder

    # Split the text into lines to preserve the structure
    lines = text.split('\n')

    # Process each line individually
    processed_lines = []
    for line in lines:
        # Replace stop words in the line
        processed_line = pattern.sub(remove_stop_words, line)
        # Clean up extra spaces left by removal
        processed_line = re.sub(r'\s{2,}', ' ', processed_line).strip()
        processed_lines.append(processed_line)

    # Join the lines back together, preserving the blank lines
    processed_text = '\n'.join(processed_lines)
    return processed_text

def levenshtein_recursive(str1, str2, m, n):
      # str1 is empty
    if m == 0:
        return n
    # str2 is empty
    if n == 0:
        return m
    if str1[m - 1] == str2[n - 1]:
        return levenshtein_recursive(str1, str2, m - 1, n - 1)
    return 1 + min(
          # Insert     
        levenshtein_recursive(str1, str2, m, n - 1),
        min(
              # Remove
            levenshtein_recursive(str1, str2, m - 1, n),
          # Replace
            levenshtein_recursive(str1, str2, m - 1, n - 1))
    )

def levenstein_distance(str1, str2):
    return levenshtein_recursive(str1, str2, len(str1), len(str2))
