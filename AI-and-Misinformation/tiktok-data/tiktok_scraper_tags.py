import asyncio, re, json, random
from pathlib import Path
from playwright.async_api import async_playwright, Page

"""
Thank you to the code refereced from the following:
    https://github.com/Tahvia127/Hashtags-For-Change/tree/main/TikTok_Data
"""

# UserAgent
UA: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
# Output Folder
# PROXY = {"server": "http://host:port"}
BASE_DIR = Path(__file__).resolve().parent
TOPICS = BASE_DIR / "topics"
OUT_FOLDER = BASE_DIR / "data"
OUT_FILE = OUT_FOLDER / "ids.json"
STORAGE: Path = BASE_DIR / "./tiktok_storage_state.json"

# video ids per hashtag
TARGET_PER: int = 500

def load_topics(path: Path) -> list[str]:
    """
    Takes a newline spaced file and returns it as a list
    """
    if not path.exists():
        raise NotADirectoryError(str(path) + " || Path does not exist")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f]
    except Exception as e:
        raise ValueError(e)
    
def load_tags(path: Path) -> dict[str, list[str]]:
    """
    Returns the data saved (format of {'hashtag': [list of ids corresponding to hashtag]})
    """
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

async def collect_tags(page: Page, tag: str, target_per = TARGET_PER, time_limit = 1000) -> list[str]:
    url = f"https://www.tiktok.com/tag/{tag}"
    await page.goto(url, wait_until="domcontentloaded")

    try:
        await page.wait_for_selector('a[href*="/video/"]', timeout=60_000)
    except Exception:
        pass
    
    body = page.locator("body")
    link_loc = page.locator('a[href*="/video/"]')
    seen = set()

    def _id_from_url(u: str):
            m = re.search(r"video/(\d+)", u)
            return m.group(1) if m else None

    async def handle_response(response):
        vid = _id_from_url(response.url)
        if vid and len(seen) < target_per:
            seen.add(vid)

    page.on("response", handle_response)
    stall = 0 
    while len(seen) < target_per and stall <= 25:
        if await link_loc.count() > 0:
            try:
                await link_loc.last.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass

        
        await body.evaluate("el => el.scrollBy(0, el.clientHeight * 0.95)")
        await asyncio.sleep(random.uniform(0.5, 1.5))        

        hrefs = await link_loc.evaluate_all("els => els.map(a => a.href).filter(Boolean)")
        for href in hrefs:
            vid = href.split("video/")[-1].split("?")[0].split("/")[0]
            if vid.isdigit() and vid not in seen:
                seen.add(vid)

        verify_count = 0
        while await page.get_by_text("Verify", exact=False).count() and verify_count < 180:
            await asyncio.sleep(1)
            verify_count += 1
        
        # if theres no tags just skip to next
        if len(seen) == 0:
            stall += 1

    print(f"saved {len(seen)} tags to {tag}")
    return list(seen)[:target_per]

async def main():
    topics: list[str] = load_topics(TOPICS)
    data: dict[str, list[str]] = load_tags(OUT_FILE)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = await browser.new_context(
            user_agent=UA,
            locale="en-US",
            timezone_id="America/New_York",
            # proxy=PROXY,
            geolocation={"latitude": 40.7, "longitude": -74.0},
            permissions=["geolocation"],
            storage_state=STORAGE if STORAGE.exists() else None
        )
        page = await context.new_page()

        # loops through each tag
        for tag in topics:
            if tag in data and len(data[tag]) >= TARGET_PER:
                continue
            ids = await collect_tags(page, tag, TARGET_PER)
            # merge lists
            data[tag] = (data.get(tag) or []) + ids
            OUT_FOLDER.mkdir(parents=True, exist_ok=True)

            with OUT_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())