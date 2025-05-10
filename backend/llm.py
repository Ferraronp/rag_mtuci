import asyncio
from typing import List, Dict, Optional, Tuple
from pprint import pprint
import aiohttp
import re


URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer ",
    "Content-Type": "application/json"
}
MAX_CONCURRENT_REQUESTS = 5
MAX_RETRIES = 6
RETRY_TIME_SLEEP = 60


def make_payload(prompt: List[Dict[str, str]], is_small: bool = True) -> Dict:
    return {
        "model": "nvidia/llama-3.3-nemotron-super-49b-v1:free" if is_small else "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        "messages": prompt,
        "temperature": 0.7
    }


async def fetch(session: aiohttp.ClientSession, prompt: List[Dict[str, str]], use_small_model: bool = True) -> Optional[str]:
    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(URL, json=make_payload(prompt, is_small=use_small_model), headers=HEADERS) as response:
                if response.status != 200:
                    time_sleep = RETRY_TIME_SLEEP
                    if response.status == 429:
                        time_sleep = int(response.headers.get('Retry-After'))
                    print(f"[WARNING] Status {response.status} waiting {time_sleep} seconds")
                    await asyncio.sleep(time_sleep)
                    continue
                data = await response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[EXCEPTION] {e}")
            await asyncio.sleep(RETRY_TIME_SLEEP)
    return None


async def run_batch(prompts: List[List[Dict[str, str]]], use_small_model: bool = True) -> List[str]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, prompt, use_small_model) for prompt in prompts]
            return await asyncio.gather(*tasks)


def analyze_and_summarize_texts(texts: List[str], user_request: str) -> List[Tuple[bool, str]]:
    prompts = []
    for x in texts:
        prompt = [
            {
                "role": "user",
                "content": (
                    'На пользовательский запрос: "{}" выполни два действия:\n'.format(user_request) +
                    '1. Ответь, полезен ли текст для генерации ответа. Ответ строго в формате: '
                    '"[Да]" или "[Нет]".\n' +
                    '2. После этого напиши краткую выжимку с основными моментами по запросу пользователя "{}" для ответа.\n'.format(user_request) +
                    'Никаких других пояснений не добавляй.\n'
                    'Текст: ```{}```'.format(x)
                )
            },
            {
                "role": "assistant",
                "content": "["
            }
        ]
        prompts.append(prompt)

    results = asyncio.run(run_batch(prompts))

    parsed = []
    for res in results:
        if not res:
            parsed.append((False, ""))
            continue
        print(res, end="\n" + '=' * 10 + "\n")
        match = re.search(r"(да|нет)\]", res.lower())
        is_useful = match.group(1) == "да" if match else False

        summary = re.sub(r'^.*?\]\s*', '', res, flags=re.DOTALL).strip()

        parsed.append((is_useful, summary))

    return parsed


def get_response_for_user_request_from_large_model(user_request: str, useful_info: Dict[str, List[str]]) -> str:
    text_prompt = ('Основываясь на этих данных: {}\n'.format("\n-----\n".join(list(map(lambda x: "\n".join(x), useful_info.values())))) +
              'Дай ответ на запрос пользователя: ```{}```'.format(user_request))
    print("Final prompt:", text_prompt)
    prompt = [
        {
            "role": "user",
            "content": text_prompt
        }
    ]
    results: List[str] = asyncio.run(run_batch([prompt], use_small_model=False))
    return results[0]
