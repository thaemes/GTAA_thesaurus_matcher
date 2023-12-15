
import spacy
import csv
import socket
import json

server_socket = socket.socket()
host = '127.0.0.1'
port = 12223
server_socket.bind((host, port))

similarity_threshold = 0.6 

nlp = spacy.load("nl_core_news_lg")

thesaurus_file = "open_subset_gtaas.csv"
thesaurus = {}

try:
    with open(thesaurus_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            number = (row["Subject"])  # Convert the number to an integer
            word = row["Label"]
            thesaurus[word] = number

    server_socket.listen()
    print("\n### Server Started Listening on Port", port, "\n")

    while True:
        client_socket, address = server_socket.accept()
        print("### Accepted Connection from:", address)

        while True:
            data = client_socket.recv(1024)
            if not data:
                print("### No Data Received. Closing Connection.")
                break

            input_text = data.decode('utf-8')
            print("### Received Data:", input_text)
            response = []

            # Split input text into words/terms
            input_terms = input_text.split()

            # Track terms that have been naively matched
            naively_matched_terms = []

            # Naive matching for the entire input and individual terms
            if input_text in thesaurus:
                response.append({
                    "label": input_text,
                    "gtaa": thesaurus[input_text],
                    "similarity_score": 1
                })
                naively_matched_terms.append(input_text)
            else:
                for term in input_terms:
                    if term in thesaurus:
                        response.append({
                            "label": term,
                            "gtaa": thesaurus[term],
                            "similarity_score": 1
                        })
                        naively_matched_terms.append(term)

            # Spacy matching for terms not naively matched
            for term in input_terms:
                if term not in naively_matched_terms:
                    term_doc = nlp(term)
                    best_match = None
                    best_similarity = 0

                    for word, number in thesaurus.items():
                        word_doc = nlp(word)
                        similarity = term_doc.similarity(word_doc)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = (word, number)

                    if best_similarity >= similarity_threshold:
                        response.append({
                            "label": best_match[0],
                            "gtaa": best_match[1],
                            "similarity_score": best_similarity
                        })

            # Send the response back to the client
            if response:
                client_socket.send( (json.dumps(response)+"\n").encode('utf-8'))
            else:
                client_socket.send('No match found'.encode('utf-8'))

            print("### Response Sent:", json.dumps(response))

finally:
    server_socket.close()
    print("### Server Socket Closed")
