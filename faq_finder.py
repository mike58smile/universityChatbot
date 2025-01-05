import typing
from statistics import mean
import evaluate
from sentence_transformers import SentenceTransformer, util
import pickle
from functions import preprocess_txt, generate_word_ngrams
input_faq = "input/faq.txt"


def create_list_of_faq(file = input_faq):
    with open(file, mode="r", encoding='utf-8') as f:
        content = f.read()
        faq_list = content.split("\n\n")
    return faq_list

def calc_embeddings(list_sentences: list[str], model: SentenceTransformer = None):
    """Load references from a file and compute their embeddings.
    Embeddings are vectors which will be used to compute semantic similarity between the prompt and the reference.

    Args:
        file (str): File with faqs.
        model (SentenceTransformer): Model for extracting embeddings.
    
    Returns: list[tuple[str, typing.Any]]: List of tuples with the reference and its embedding.
    """
    references = list_sentences
    reference_embeddings = model.encode(references, batch_size=32, convert_to_tensor=True)
    return list(zip(references, reference_embeddings))


def compare_semantic(prompt: str, references: list[tuple[str, typing.Any]], model: SentenceTransformer):
    """Compare the prompt with the references using semantic similarity.

    Args:
        prompt (str): Prompt to compare with the references
        references (list[tuple[str, typing.Any]]): List of tuples with the reference and its embedding
        model (SentenceTransformer): Model for extracting embeddings

    Returns:
        scores(list): List of scores for each reference
    """
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    scores = []
    for ref, ref_embed in references:
        semantic_similarity = util.cos_sim(prompt_embedding, ref_embed).item()  # Convert tensor to a numerical value
        scores.append(semantic_similarity)
    return scores

def calculate_n_gram_old(prompt: str, list_sentences: list[str]):
    evaluator = evaluate.load("sacrebleu")
    scores = []
    for ref in list_sentences:
        n_gram_similarity = evaluator.compute(predictions=[prompt], references=[[ref]])["score"]
        print(n_gram_similarity)
        scores.append(n_gram_similarity)
    return scores


def calculate_n_gram(prompt: str, list_sentences: list[str]):
    """Calculate n-gram similarity between the prompt and the preprocessed list of sentences 

    Args:
        prompt (str): prompt from the user
        list_sentences (list[str]): preprocessed list of sentences
    """
    prompt_ngrams = generate_word_ngrams(prompt, 1, "processed/prompt_ngrams.txt")
    list_ngrams = []
    for sentence in list_sentences:
        sentence_ngrams = generate_word_ngrams(sentence, 1)
        list_ngrams.append(sentence_ngrams)

    scores = [0] * len(list_ngrams)
    for i, sentence_ngrams in enumerate(list_ngrams):
        for prompt_ngram in prompt_ngrams:
            for sentence_ngram in sentence_ngrams:
                if prompt_ngram[:3] == sentence_ngram[:3]:
                    scores[i] += 1
    return prompt_ngrams, list_ngrams, scores

def compare_prompt(prompt: str, references: list[tuple[str, typing.Any]], model: SentenceTransformer):
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    evaluator = evaluate.load("sacrebleu")

    scores = []
    for ref, ref_embed in references:
        semantic_similarity = util.cos_sim(prompt_embedding, ref_embed).item()  # Convert tensor to a numerical value
        n_gram_similarity = evaluator.compute(predictions=[prompt], references=[[ref]])["score"]
        scores.append(mean([semantic_similarity, n_gram_similarity]))
    return scores

def read_input_from_console() -> str:
    """Read input from the console and return it as a string."""
    return input("Please enter your prompt: ")

def calculate_semantic(prompt: str, list_sentences: list[str], model: SentenceTransformer):
    cache_file = "cached_references.pkl" # Check if cached embeddings exist
    try:
        with open(cache_file, "rb") as f:
            references = pickle.load(f)
    except FileNotFoundError:
        references = calc_embeddings(list_sentences, model)
        with open(cache_file, "wb") as f:
            pickle.dump(references, f)
    return compare_semantic(prompt, references, model)

def get_best_match(list_sentences: list[str], probability: list, i: int = 3) -> list:
    """Get the best answer from a list of faq, with answer on the last line - the items in the format: question(NL)question(NL)...answer

    Args:
        list_sentences (list[str]): List of sentences to choose from.
        probability (list): List of probabilities for each sentence.

    Returns:
        str: The best match.
    """
    top_indices = sorted(range(len(probability)), key=lambda i: probability[i], reverse=True)[:i]
    top_probabilities = [round(probability[i], 3) for i in top_indices]
    print(f"Top indices: {top_indices}")
    top_answers = ["\n".join(list_sentences[i].split("\n")[1:]) for i in top_indices] #top_answers = [list_sentences[i].split("\n")[-1] for i in top_indices]
    return [top_probabilities, top_answers]
    #index = list_sentences.index(max(list_sentences))
    #return list_sentences[index].split("\n")[-1]

def main():
    list_of_faq = create_list_of_faq("input/faq.txt")
    list_of_faq_processed = create_list_of_faq("processed/faq_processed.txt")
    #read_input_from_console()
    semantic_probability = calculate_semantic("tištěnou verzi", list_of_faq, SentenceTransformer("paraphrase-multilingual-mpnet-base-v2", device="cpu"))

    #best_match_index = semantic_probability.index(max(semantic_probability))
    #best_match_faq = list_of_faq[best_match_index].split("\n")[-1]
    
    #print(f"Size of list_of_faq_processed: {len(list_of_faq_processed)}")
    #print("List of FAQs:")
    #print(list_of_faq)
    # for faq in list_of_faq:
    #     print(faq)
    # print("\nAnswer Probabilities:")
    # for probability in semantic_probability:
    #     print(probability)
    #print(best_match_faq)
    #print(semantic_probability)
    #print(get_best_match(list_of_faq, semantic_probability))
    top_probabilities, top_answers = get_best_match(list_of_faq, semantic_probability)
    for prob, ans in zip(top_probabilities, top_answers):
        print(f"[{prob}] {ans}")

if __name__ == "__main__":
    main()
