import spacy
import csv
import socket
import json
import string

server_socket = socket.socket()
host = 'localhost' #'10.150.24.129'#'localhost'#'172.20.10.4'
port = 12223
server_socket.bind((host, port))

similarity_threshold = 0.6

nlp = spacy.load("nl_core_news_lg")

thesaurus_file = "open_subset_gtaas_childfriendly.csv"
thesaurus = {}

blocklist_file = "blocklist.txt"
blocklist = set()

# Load the blocklist
try:
    with open(blocklist_file, "r", encoding="utf-8") as blockfile:
        for line in blockfile:
            blocked_word = line.strip()
            blocklist.add(blocked_word)

    with open(thesaurus_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            number = row["Subject"]
            word = row["Label"]
            thesaurus[word] = number

    server_socket.listen()
    print(f"\n### Server Started Listening on Port {port}\n")

    while True:
        client_socket, address = server_socket.accept()
        print(f"### Accepted Connection from: {address}\n")

        while True:
            data = client_socket.recv(1024)
            if not data:
                print("### No Data Received. Closing Connection.\n")
                break

            input_text = data.decode('utf-8')
            input_text = ''.join(char for char in input_text if char not in string.punctuation)
            print(f"### Received Data: {input_text}")
            response = []

            input_terms = input_text.split()
            naively_matched_terms = []

            input_terms = [term for term in input_terms if term not in blocklist]

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

            unmatched_terms = [term for term in input_terms if term not in naively_matched_terms]

            if unmatched_terms:
                # Send a notification to the client before initiating Spacy matching
                client_socket.send("!slow matching\n".encode('utf-8'))

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

            if response:
                client_socket.send((json.dumps(response) + "\n").encode('utf-8'))
            else:
                client_socket.send('!no match found\n'.encode('utf-8'))

            print(f"### Response Sent: {json.dumps(response)}\n")

finally:
    server_socket.close()
    print("### Server Socket Closed")
    
