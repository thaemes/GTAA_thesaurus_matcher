import spacy
from spacy.matcher import Matcher
import csv
import socket
import json
import string

def initialize_server():
    server_socket = socket.socket()
    host = 'localhost'
    port = 12223
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"\n### Server Started Listening on Port {port}\n")
    return server_socket

def load_thesaurus(thesaurus_file):
    thesaurus = {}
    with open(thesaurus_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            number = row["Subject"]
            word = row["Label"]
            thesaurus[word] = number
    return thesaurus

# def preprocess_text(input_text, nlp):
#     doc = nlp(input_text)
#     return ' '.join([token.text for token in doc if not token.is_stop and not token.is_punct])

def preprocess_text(input_text, nlp, remove_adjectives):
    doc = nlp(input_text)
    return ' '.join([token.text for token in doc if not token.is_stop and (not remove_adjectives or token.pos_ != 'ADJ')])


def naive_matching(input_text, thesaurus, matcher, nlp):
    doc = nlp(input_text)
    matches = matcher(doc)
    results = []
    for match_id, start, end in matches:
        span = doc[start:end]
        word = span.text
        if word in thesaurus:
            results.append({
                "label": word,
                "gtaa": thesaurus[word],
                "similarity_score": 1
            })
    return results

def semantic_similarity_matching(input_text, thesaurus, nlp, similarity_threshold):
    input_doc = nlp(input_text)
    best_match = None
    best_similarity = 0
    for word, number in thesaurus.items():
        word_doc = nlp(word)
        similarity = input_doc.similarity(word_doc)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = (word, number)
    if best_similarity >= similarity_threshold:
        return [{
            "label": best_match[0],
            "gtaa": best_match[1],
            "similarity_score": best_similarity
        }]
    return []

def main():
    similarity_threshold = 0.6
    nlp = spacy.load("nl_core_news_lg")
    thesaurus_file = "open_subset_gtaas_childfriendly.csv"
    thesaurus = load_thesaurus(thesaurus_file)

    # Create patterns for Matcher
    matcher = Matcher(nlp.vocab)
    for word in thesaurus.keys():
        pattern = [{"LOWER": word.lower()} for word in word.split()]
        matcher.add(word, [pattern])

    server_socket = initialize_server()
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"### Accepted Connection from: {address}\n")

            while True:
                data = client_socket.recv(1024)
                if not data:
                    print("### Null Data Received. Closing Connection.\n")
                    break

                input_text = data.decode('utf-8')
                preprocessed_text = preprocess_text(input_text, nlp, False)

                response = naive_matching(preprocessed_text, thesaurus, matcher, nlp)
                if not response:
                    preprocessed_text = preprocess_text(input_text, nlp, True)
                    client_socket.send("!slow matching\n".encode('utf-8'))
                    response = semantic_similarity_matching(preprocessed_text, thesaurus, nlp, similarity_threshold)

                if response:
                    client_socket.send((json.dumps(response) + "\n").encode('utf-8'))
                else:
                    client_socket.send('!no match found\n'.encode('utf-8'))

                print(f"### Response Sent: {json.dumps(response)}\n")
    finally:
        server_socket.close()
        print("### Server Socket Closed")

if __name__ == "__main__":
    main()
