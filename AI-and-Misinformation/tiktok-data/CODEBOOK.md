# Codebook: TikTok Video Metadata by Tag

## Dataset Overview

**Dataset name:** TikTok Metadata by Tag  
**Source:** TikTok (collected via TikTokAPI (unofficial) and PlayWright)  
**File format:** CSV  
**One row represents:** One TikTok video  
**Language coverage:** Multiple (e.g., English, Spanish, Unknown)  
**# of rows**: Currently 304, will obtain more

### Data Collection Notes
- Video metadata was collected in [tiktok_scraper_data](tiktok_scraper_data.py) by videos ids collected in [tiktok_scraper_id](tiktok_scraper_id.py).  
- Engagement metrics reflect values at the time of collection and may change over time.
- **[tiktok_scraper_id](tiktok_scraper_id.py) is referenced by https://github.com/Tahvia127/Hashtags-For-Change/tree/main/TikTok_Data**

---

## Variable Definitions

### `source`
- **Type:** string
- **Description:** Platform from which the video was collected
- **Values:** `"TikTok"`
- **Notes:** Included for multi-platform compatibility

---

### `video_id`
- **Type:** string
- **Description:** Unique identifier assigned to the TikTok video
- **Source:** TikTok video ID
- **Notes:** Used to derive approximate post date

---

### `post_date_utc`
- **Type:** datetime (ISO 8601, UTC)
- **Description:** Estimated timestamp when the video was created
- **Derivation:** Extracted from TikTok Snowflake-style video ID
- **Notes:** BROKEN, NEED TO FIX

---

### `description`
- **Type:** string
- **Description:** Video caption text provided by the creator
- **Missing:** Empty if no caption was provided
- **Notes:** May include hashtags, mentions, or sensitive content

---

### `text_language`
- **Type:** string
- **Description:** Language code detected for the video text
- **Examples:**  
  - `en` = English  
  - `es` = Spanish  
  - `un` = Unknown
- **Source:** TikTok language detection

---

### `category_type`
- **Type:** integer
- **Description:** TikTok internal content category identifier
- **Source:** TikTok API
- **Notes:** Numeric codes are platform-defined and not publicly documented

---

### `is_aigc`
- **Type:** boolean
- **Description:** Indicates whether TikTok labels the video as AI-generated
- **Values:**  
  - `true` = Labeled as AI-generated  
  - `false` = Not labeled as AI-generated  
  - `null` = Label not available
- **Source:** TikTok moderation metadata

---

### `aigc_description`
- **Type:** string
- **Description:** Additional description provided when a video is labeled as AI-generated
- **Missing:** Empty if video is not labeled as AI-generated

---

### `collected`
- **Type:** boolean
- **Description:** Indicates whether the video has been collected or favorited by the uploader
- **Source:** TikTok API
- **Notes:** Meaning is platform-defined and may change

---

### `is_reviewing`
- **Type:** boolean
- **Description:** Indicates whether the video is under review by TikTok
- **Source:** TikTok moderation metadata
- **Notes:** Field may be unreliable or transient

---

### `likes`
- **Type:** integer
- **Description:** Number of likes received by the video
- **Source:** `stats.diggCount`
- **Missing:** `null` if unavailable

---

### `comments`
- **Type:** integer
- **Description:** Number of comments on the video
- **Source:** `stats.commentCount`

---

### `shares`
- **Type:** integer
- **Description:** Number of times the video has been shared
- **Source:** `stats.shareCount`

---

### `views`
- **Type:** integer
- **Description:** Number of times the video has been viewed
- **Source:** `stats.playCount`

---

### `author_follower_count`
- **Type:** integer
- **Description:** Number of followers the video creator has
- **Source:** `authorStatsV2.followerCount`

---

### `author_following_count`
- **Type:** integer
- **Description:** Number of accounts the creator follows
- **Source:** `authorStatsV2.followingCount`

---

### `author_total_likes`
- **Type:** integer
- **Description:** Total number of likes received across all creator videos
- **Source:** `authorStatsV2.heartCount`

---

### `author_video_count`
- **Type:** integer
- **Description:** Total number of videos posted by the creator
- **Source:** `authorStatsV2.videoCount`

---

## Known Limitations

- **!!TODO:** I am unsure of the best way to only keep DoorDash Girl content, will update this

