# w26-misinformation-and-ai YouTube Codebook

## yt_doordash_girl_video_finalAGGR_clean.csv (24691 rows)

| Variable | Description |
| -------- | ----------- |
| video_id | unique ID YouTube uses to identify video |
| url | url for the YouTube video (based on video_id) |
| video_title | video title |
| channel_id | unqiue ID YouTube uses to identify channel |
| channel_title | channel title |
| publish_date | video publication date, in MM-DD-YY format |
| description | video description |
| channel_following | number of subscribers for the posting channel (YouTube rounded to 3 significant figures) |
| duration | length of video, in HH:MM:SS format |
| like_count | number of likes (-1 if unavailable) |
| comment_count | number of comments (-1 if unavailable) |
| view_count | number of views (-1 if unavailable) |
| accessed_at | date and time at which video and channel statistics were retrieved, in YYYY-MM-DD HH:MM:SS.mmmmmm format |
| trascript | english transcript of the video, if available (value = None if not) |

## yt_doordash_girl_comments_AGGR_clean.csv (126 rows)

| Variable | Description |
| -------- | ----------- |
| video_id | ID of the video the comment is under |
| comment_id | unique ID of the comment |
| parent_id | if the comment is a response to another comment, the unique id of the parent comment (value = None if not applicable) |
| author_display_name | commenter's display name, preceeded by an '@" |
| text_display | text content of the comment |
| like_count | comment like count |
| published_at | when the comment was published, in ISO 8601 format |
| updated_at | when the comment was last updated, in ISO 8601 format |
| accessed_at | date and time at which comments were retrieved, in YYYY-MM-DD HH:MM:SS.mmmmmm format |


## transcript_error_list.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unqiue ID of video that encountered problems when retrieving transcript |