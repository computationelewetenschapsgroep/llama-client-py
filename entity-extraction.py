## implementation of https://github.com/ggerganov/llama.cpp/blob/master/examples/server/chat.sh in python

import requests
import re
import json
import sys 

from concurrent.futures import ThreadPoolExecutor, as_completed
import time


urls = [
    "http://127.0.0.1:8001/",
    "http://127.0.0.1:8002/",
    "http://127.0.0.1:8003/",
    "http://127.0.0.1:8004/"
]

chat_template_library = [
    ("sports_category_extraction",[
    "I want to participate in boston marathon.",
	"Marathon"
]),
 ("location_extraction",[
    "I want to participate in boston marathon.",
	"Boston"
]),
("product_extraction",[
    "I want shoes to participate in boston marathon.",
	"Shoes"
]),
("season_extraction",[
    "I want to participate in boston marathon.",
	"Spring"
])
]

instruction_library =[
    ("sports_category_extraction","You are a world class entity extractor. For a given user query, extract the sports category from it. No preamble."),
    ("location_extraction","You are a world class geocoder. For a given user query, extract the location from it. No preamble."),
    ("product_extraction","You are a world class entity extractor. For a given user query, extract the product category from it. No preamble."),
    ("season_extraction", "You are a world class season extractor. For a given user query, extract the season from it. No preamble.")
]



def get_num_tokens(query,url)->int:
    response = requests.post(url+"tokenize",json={"content":query})

    tokens = response.json()
    num_tokens = len(tokens["tokens"])
    return num_tokens

def run_concurrent_queries(queries, max_workers=12):
    """
    Run the extraction in parallel using multiple threads.
    """
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_num_tokens, query, urls[idx]) for idx, query in enumerate(queries)]

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    return results

token_count_per_instruction = run_concurrent_queries(map(lambda pair: pair[1],instruction_library))

def get_entities(query, url, key, chat, instruction, num_tokens):
    prompt = str()
    prompt += instruction
    prompt += " "
    for item in zip(["\n### Human:","\n### Assistant:"],chat):
        prompt+=" ".join(item)
    q = [
        query,
        ""
    ]
    for item in zip(["\n### Human:","\n### Assistant:"],q):
         prompt+=" ".join(item)


    payload = {"prompt": prompt,
            "temperature": 0.01,
            "top_k": 2,
            "top_p": 0.9,
            "n_keep": num_tokens,
            "n_predict": 2,
            "cache_prompt": False,
            "stop": ["\n### Human:"],
            "stream": True}

    response = requests.post(url+"completion",json=payload)

    results = [json.loads(item[5:].strip()) for item in response.text.split("\n") if item and re.match("data:", item)]

    output = ""
    for item in results:
        output += item["content"].strip() 

    return (key,output)

def extract_entities_concurrently(query, urls, chats, instructions, token_counts_per_instruction, max_workers=12):
    keys = []
    chat_instruction_pair = []
    for chat, instruction in zip(chats, instructions):
        k, c = chat
        k, i = instruction
        keys.append(k)
        chat_instruction_pair.append((c,i))

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_entities, query, urls[idx], keys[idx], 
                                   chat , instruction, 
                                   token_counts_per_instruction[idx]) for idx,(chat , instruction) in enumerate(chat_instruction_pair)]

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
        
    return results

if __name__ == "__main__":
    for line in sys.stdin:
        q = line.strip()
        start = time.time()
        entities = extract_entities_concurrently(q,urls, chat_template_library, 
                                                 instruction_library, token_count_per_instruction)
        end = time.time()
        print(entities)
        print(f"elapsed time: {end-start}")
