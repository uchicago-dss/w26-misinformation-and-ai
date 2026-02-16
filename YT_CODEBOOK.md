# w26-misinformation-and-ai YouTube Codebook

## Gathering Data

### yt_doordash_girl_video_finalAGGR_clean.csv (24691 rows)

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

### yt_doordash_girl_comments_AGGR_clean.csv (126 rows)

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


### transcript_error_list.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unqiue ID of video that encountered problems when retrieving transcript |


## Vader Sentiment Analysis

Note: Categories are based on compound score and divided according to the Vader GitHub. Positive/Sympathetic means compound score >= 0.05, neutral means 0.05 > compound score > -0.05, negative/inflammatory means compound score <= -0.05.

### yt_transcript_vader.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unique ID YouTube uses to identify video |
| type | type = 'transcript' |
| sentence_index | integer starting from 0, indicates order of sentences |
| text | the actual text being analyzed |
| compound | float, compound score (see Vader) |
| pos | float, positive score (see Vader) |
| neg | float, negative score (see Vader) |
| neu | float, neutral score (see Vader) |

### yt_vader_tscript_analysis.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unique ID YouTube uses to identify video
| type | type = 'comments' |
| hook_stdev | standard deviation of the compound score for the video's hook (sentence index from 0 to 4, inclusive) |
| hook_category | sentiment category the hook falls under based on average compound score |
| overall_stdev | standard deviation of the compound score for the entire video (includes hook) |
| overall_category | sentiment category the overall video falls under based on average compound score (includes hook) |
| pos_count | number of sentences with overall positive sentiment |
| neu_count | number of sentences with overall neutral sentiment |
| neg_count | number of sentences with overall negative sentiment |

### yt_comments_vader.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unique ID YouTube uses to identify video that comment of interest is under
| type | type = 'comments' |
| sentence_index | integer starting from 0, indicates order of sentences |
| text | the actual text being analyzed
| compound | float, compound score (see Vader) |
| pos | float, positive score (see Vader) |
| neg | float, negative score (see Vader) |
| neu | float, neutral score (see Vader) |
| comment_id | unique ID of the comment |
| parent_id | unique ID of the comment's parent comment if it is a reply (value = None otherwise) |

### yt_comments_vader_analysis_byparent.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unique ID YouTube uses to identify video that comment of interest is under
| parent_id | unique ID of parent comment
| parent_avg | average compound score of parent comment |
| parent_category | sentiment category the parent comment falls under |
| replies_avg | average compound score of the max top 5 replies for the comment with parent_id |
| replies_category | sentiment category the max top 5 replies fall under |
| replies_stdev | stadard deviation of the compound scores of the max top 5 replies of the parent comment, value = None if there are less than 2 values |

### yt_comments_vader_analysis_byvideo.csv
| Variable | Description |
| -------- | ----------- |
| video_id | unique ID YouTube uses to identify video that comment of interest is under
| comments_avg | average compound score for all the comments of interest under the video with video_id |
| comments_category | overall sentiment category for the comments, based on comments_avg |
| comments_stdev | stadard deviation of the compound scores of the comments, value = None if there are less than 2 values |
| comments_pos_count | number of comments with overall positive sentiment; if a comment consists of multiple sentences, the sentiment is based on the average of all the compound scores for that particular comment |
| comments_neu_count | number of comments with overall neutral sentiment |
| comments_neg_count | number of comments with overall negative sentiment |