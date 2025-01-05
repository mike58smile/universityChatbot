from functions import preprocess_txt, delete_stop_words, generate_word_ngrams
from faq_finder import create_list_of_faq, calculate_semantic, get_best_match, read_input_from_console, calculate_n_gram
from sentence_transformers import SentenceTransformer


def print_most_probable_answers(list_of_faq, probability, i=3):
    #Get the i best matches
    top_probabilities, top_answers = get_best_match(list_of_faq, probability, i)
    # Print the resulting most probable answers
    for prob, ans in zip(top_probabilities, top_answers):
        print(f"[{prob}] {ans}")
    return top_answers

def get_most_probable_answers(list_of_faq, probability, i=3):
    #Get the i best matches
    top_probabilities, top_answers = get_best_match(list_of_faq, probability, i)
    output = ""
    for prob, ans in zip(top_probabilities, top_answers):
        output += f"{ans} [{prob}]\n\n"  # Add a newline for better formatting
    return output

def main():
    raw_path = "input/faq.txt" # toto menim
    processed_path = "processed/faq_processed2.txt" # toto menim
    
    # Save preprocessed text to a file
    preprocess_txt(raw_path, processed_path)

    # Create list of faq - without \n
    list_of_faq = create_list_of_faq(raw_path) # jedno z tychto vkladam do calculate_semantic funkcie
    list_of_faq_processed = create_list_of_faq(processed_path) # jedno z tychto vkladam do calculate_semantic funkcie

    # Read from console
    prompt = read_input_from_console()
    #Calculate semantic probability
    semantic_probability = calculate_semantic(prompt, list_of_faq, SentenceTransformer("paraphrase-multilingual-mpnet-base-v2", device="cpu"))
    print(calculate_n_gram(prompt, list_of_faq_processed))

    print("Semantic probability:")
    print_most_probable_answers(list_of_faq, semantic_probability,3)
    #print("\n\n\nN-gram probability:")
    #print_most_probable_answers(list_of_faq, ngram_probability,3)

if __name__ == "__main__":
    main()

