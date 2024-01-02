import spacy
from spacy.matcher import Matcher
import csv
import socket
import json
import string

def initialize_server():
    server_socket = socket.socket()
    host =  '10.150.25.107' #'10.150.24.71' # //'10.150.25.1'
    port = 12224
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

def preprocess_text(input_text, nlp, remove_adjectives):
    doc = nlp(input_text)
    return ' '.join([token.text for token in doc if not token.is_stop and (not remove_adjectives or token.pos_ != 'ADJ')])

def compute_similarities(main_keyword, other_keywords, nlp):
    main_label = main_keyword["label"]  # Extracting the label field
    main_doc = nlp(main_label)  # Use the label for processing
    results = []
    for keyword in other_keywords:
        label, gtaa = keyword["label"], keyword["gtaa"]
        keyword_doc = nlp(label)
        similarity = main_doc.similarity(keyword_doc)
        results.append({
            "label": label,
            "gtaa": gtaa,
            "similarity_score": similarity
        })
    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)
def main():
    nlp = spacy.load("nl_core_news_lg")
    thesaurus_file = "childfriendly_no_dash.csv"
    thesaurus = load_thesaurus(thesaurus_file)

    server_socket = initialize_server()
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"### Accepted Connection from: {address}\n")

            data_buffer = ""
            while True:
                data = client_socket.recv(16384)
                if not data:
                    print("### Null Data Received. Closing Connection.\n")
                    break
                data_buffer += data.decode('utf-8')

                try:
                    # Try to parse the accumulated data
                    parsed_data = json.loads(data_buffer)

                    # If successful, process the request
                    main_keyword = parsed_data["main_keyword"]
                    other_keywords = parsed_data["other_keywords"]
                    response = compute_similarities(main_keyword, other_keywords, nlp)
                    print(response)
                    client_socket.send((json.dumps(response) + "\n").encode('utf-8'))

                    # Clear the buffer for the next message
                    data_buffer = ""
                except json.JSONDecodeError:
                    # If JSON is incomplete, continue accumulating data
                    continue

    finally:
        server_socket.close()
        print("### Server Socket Closed")


if __name__ == "__main__":
    main()