import time
from typing import List, Dict
import re

import tiktoken

from test import get_texts_and_urls_from_google_search
from llm import (analyze_and_summarize_texts,
                 get_response_for_user_request_from_large_model)

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_text(text: str) -> List[str]:
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)

    return sentences


def split_text_into_chunks(text: str, chunk_limit: int = 4000) -> List[str]:
    tokenizer = tiktoken.encoding_for_model("gpt-4")

    sentences = normalize_text(text)

    chunks = []
    current_chunk = ''
    current_tokens = 0

    for sentence in sentences:
        token_count = len(tokenizer.encode(sentence))

        if current_tokens + token_count > chunk_limit:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ' '
            current_tokens = token_count
        else:
            current_chunk += sentence + ' '
            current_tokens += token_count

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


class SearchRequest(BaseModel):
    query: str


@app.post("/search")
def search(request: SearchRequest):
    google_start = time.time()
    user_request = request.query.strip()
    texts, urls = get_texts_and_urls_from_google_search(user_request)
    print(f"[INFO] Parsing {time.time() - google_start}")
    llm_start = time.time()
    useful_info: Dict[str, List[str]] = dict()
    for text, url in zip(texts, urls):
        if not text:
            continue
        chunks_of_text = split_text_into_chunks(text)
        print("Count chunks:", len(chunks_of_text))
        information = analyze_and_summarize_texts(chunks_of_text, user_request)
        summary_of_texts = list()
        for is_useful_text, summary_text in information:
            if is_useful_text:
                summary_of_texts.append(summary_text)
        if not summary_of_texts:
            continue
        useful_info[url] = summary_of_texts
    answer = get_response_for_user_request_from_large_model(user_request, useful_info)

    sources = list(useful_info.keys())
    print(f"[INFO] LLM {time.time() - llm_start}")
    return {
        "answer": answer,
        "sources": sources
    }
