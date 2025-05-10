import asyncio
from playwright.async_api import async_playwright, BrowserContext
from typing import List


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/134.0.4472.124 Safari/537.36"
)

OVERRIDE_SCRIPT = """
Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'});
Object.defineProperty(navigator, 'appVersion', {get: () => '5.0 (Macintosh; Intel Mac OS X 10_15_7)'});
Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
if (navigator.oscpu) {
    Object.defineProperty(navigator, 'oscpu', {get: () => undefined});
}
if (navigator.userAgentData) {
    Object.defineProperty(navigator, 'userAgentData', {
        get: () => ({
            brands: [
                { brand: "Google Chrome", version: "134" },
                { brand: "Chromium", version: "134" }
            ],
            platform: "macOS",
            mobile: false
        })
    });
}
if (window.InstallTrigger !== undefined) {
    Object.defineProperty(window, 'InstallTrigger', {get: () => undefined});
}
"""


async def __fetch_html(url: str, context: BrowserContext) -> str:
    page = await context.new_page()
    html_content = ""
    try:
        await page.goto(url, timeout=10000, wait_until="domcontentloaded")
        html_content = await page.content()
    except Exception:
        pass
    await page.close()
    return html_content


async def __fetch_all_html(urls: List[str]) -> List[str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--use-gl=egl",
            "--disable-features=UserAgentClientHint",
            "--disable-blink-features=AutomationControlled"
        ])
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="en-US",
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "sec-ch-ua-platform": "\"macOS\""
            }
        )
        await context.add_init_script(OVERRIDE_SCRIPT)
        tasks = [__fetch_html(url, context) for url in urls]
        htmls = await asyncio.gather(*tasks)
        await browser.close()
        return htmls


def fetch_urls(urls: List[str]) -> List[str]:
    htmls = asyncio.run(__fetch_all_html(urls))
    return htmls
