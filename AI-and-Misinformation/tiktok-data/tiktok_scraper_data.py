import asyncio, json
import pandas as pd
from pathlib import Path
from typing import Any
from TikTokApi import TikTokApi
from datetime import datetime, timezone
from tiktok_scraper_tags import load_tags

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "data"
IN_FILE = DATA_FOLDER / "ids.json"
OUT_FILE = DATA_FOLDER / "raw_data.csv"

def load_existing_data(path: Path) -> list[dict[str, Any]]:
    """
    Returns the data saved as a list of dicts
    """
    if not path.exists():
        return []
    try:
        df = pd.read_csv(OUT_FILE)
        return df.to_dict(orient="records")
    except:
        return []
    
# gets the raw data from each video
async def retrieve_video(api: TikTokApi, vid_id: str) -> dict:
        url = f"https://www.tiktok.com/@_/video/{vid_id}"
        try:
            video_info = await api.video(url=url).info()
            return video_info
        except Exception as e:
            print(f"ERROR for {vid_id}: {repr(e)}")
            return None

async def main():
    def tiktok_id_to_datetime(video_id: str) -> datetime:
        # TikTok epoch starts at 2015-01-01
        TIKTOK_EPOCH = 1420070400000
        timestamp_ms = (int(video_id) >> 32) + TIKTOK_EPOCH
        return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

    tags = load_tags(IN_FILE)
    data = load_existing_data(OUT_FILE)

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            headless=True,
            sleep_after=3,
        )

        existing_ids = {row["video_id"] for row in data if "video_id" in row}
        for topic in tags:
            for vid_id in tags[topic]:
                # skip videos that have already been searched
                if vid_id in existing_ids:
                    print(f"{vid_id} in exisiting_ids")
                    continue

                video_info = await retrieve_video(api=api, vid_id=vid_id)
                if video_info is None:
                    print(f"{vid_id} has no info")
                    continue

                author_stats = video_info.get("authorStatsV2", {})

                row = {
                    "source": "TikTok",

                    # ---- Video identifiers ----
                    "video_id": vid_id,
                    "post_date_utc": tiktok_id_to_datetime(vid_id).isoformat(),
                    "description": video_info.get("desc"),
                    "text_language": video_info.get("textLanguage"),
                    "category_type": video_info.get("CategoryType"),

                    # ---- AI / AIGC ----
                    "is_aigc": video_info.get("IsAigc"),
                    "aigc_description": video_info.get("AIGCDescription"),

                    # ---- Moderation / platform signals ----
                    "collected": video_info.get("collected"),
                    "is_reviewing": video_info.get("isReviewing"),

                    # ---- Engagement (may be missing on some videos) ----
                    "likes": video_info.get("stats", {}).get("diggCount"),
                    "comments": video_info.get("stats", {}).get("commentCount"),
                    "shares": video_info.get("stats", {}).get("shareCount"),
                    "views": video_info.get("stats", {}).get("playCount"),

                    # ---- Author stats ----
                    "author_follower_count": int(author_stats.get("followerCount", 0)),
                    "author_following_count": int(author_stats.get("followingCount", 0)),
                    "author_total_likes": int(author_stats.get("heartCount", 0)),
                    "author_video_count": int(author_stats.get("videoCount", 0)),
                }
                existing_ids.add(vid_id)
                data.append(row)
            pd.DataFrame(data).to_csv(OUT_FILE)

    # store in csv
    pd.DataFrame(data).to_csv(OUT_FILE)
        
async def test():
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            headless=False,
            sleep_after=3,
        )
        test_id = "7564422072143826207"
        await retrieve_video(api, test_id)

if __name__ == "__main__":
    # test
    # asyncio.run(test())
    
    asyncio.run(main())