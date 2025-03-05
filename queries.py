## ======= AUTHORS ======= ##

authors_to_drop_query = """
SELECT 
    AUTHORID
FROM MART_AUTHORS
GROUP BY 1
HAVING COUNT(*) > 1
"""

authors_authors_segments_joined_query = f"""
SELECT 
    MART_AUTHORS.AUTHORID
    , MART_AUTHORS.NB_FOLLOWS AS NB_FOLLOWS
    , COALESCE(MART_AUTHORS.NB_FOLLOWERS, CAST(MART_AUTHORS_SEGMENTATIONS.NB_FOLLOWERS AS INT)) AS NB_FOLLOWERS
    , MART_AUTHORS_SEGMENTATIONS.FASHION_INTEREST_SEGMENT
FROM MART_AUTHORS 
LEFT JOIN ({authors_to_drop_query}) authors_to_drop
USING(AUTHORID)
LEFT JOIN MART_AUTHORS_SEGMENTATIONS
USING(AUTHORID) 
WHERE authors_to_drop.AUTHORID IS NULL
AND NOT (
    MART_AUTHORS.NB_FOLLOWERS IS NULL 
    AND MART_AUTHORS_SEGMENTATIONS.NB_FOLLOWERS IS NULL
)
"""

nb_follows_median_query = f"""
SELECT
    CAST(median(NB_FOLLOWS) AS INT) as NB_FOLLOWS_MEDIAN
FROM ({authors_authors_segments_joined_query}) authors
"""

clean_authors_query = f"""
SELECT
    authors.AUTHORID
    , COALESCE(authors.NB_FOLLOWS, med.NB_FOLLOWS_MEDIAN) AS NB_FOLLOWS
    , authors.NB_FOLLOWERS
    , LN(1 + authors.NB_FOLLOWERS) AS NB_FOLLOWERS_LN1P
    , authors.FASHION_INTEREST_SEGMENT
FROM ({authors_authors_segments_joined_query}) authors
CROSS JOIN ({nb_follows_median_query}) med 
"""

## ===== IMAGES OF POSTS ===== ##
authors_posts_summary_query = """
SELECT
    AUTHORID
    , CAST(AVG(NB_LIKES) AS FLOAT) AS AVG_LIKES
    , CAST(VARIANCE(NB_LIKES) AS FLOAT) AS VAR_LIKES
    , CAST(AVG(COMMENT_COUNT) AS FLOAT) AS AVG_COMMENTS
    , CAST(VARIANCE(COMMENT_COUNT) AS FLOAT) AS VAR_COMMENTS
    , COUNT(DISTINCT POST_ID) AS NB_POSTS 
    , COUNT(IMAGE_ID) AS NB_IMAGES
    , DATEDIFF(day, MIN(POST_PUBLICATION_DATE), ANY_VALUE(MAX_DATE_IN_POST_DATASET) ) AS NB_DAYS_SINCE_FIRST_POST
FROM MART_IMAGES_OF_POSTS 
CROSS JOIN (
    SELECT 
        MAX(POST_PUBLICATION_DATE) AS MAX_DATE_IN_POST_DATASET 
    FROM MART_IMAGES_OF_POSTS
) last_date
GROUP BY AUTHORID
"""

authors_posts_summary_logged_query = f"""
SELECT
    AUTHORID
    , AVG_LIKES
    , LN(1 + AVG_LIKES) AS AVG_LIKES_LN1P
    , VAR_LIKES
    , AVG_COMMENTS
    , LN(1 + AVG_COMMENTS) AS AVG_COMMENTS_LN1P
    , VAR_COMMENTS
    , NB_POSTS
    , LN(1 + NB_POSTS) AS NB_POSTS_LN1P
    , NB_IMAGES
    , LN(1 + NB_IMAGES) AS NB_IMAGES_LN1P
    , NB_DAYS_SINCE_FIRST_POST
FROM ({authors_posts_summary_query}) t
"""

## ====== IMAGES LABELS ====== ##

clothing_labels = ['top', 'shoes', 'pants', 'coats', 'skirt', 'dress', 'shorts', 'socks', 'combi', 'bra', 'underpants']
accessories_labels = ['earrings', 'clock', 'hat', 'neckwear', 'eyewear', 'wristlet', 'bag', 'belt', 'umbrella']
ok_detection_items = clothing_labels + accessories_labels

images_labels_query = f"""
SELECT 
    DISTINCT
        IMAGE_ID
        , LABEL_NAME
FROM MART_IMAGES_LABELS
WHERE (
    TYPE <> 'object_detection' 
    OR LABEL_NAME IN ({"'" + "','".join(ok_detection_items) + "'"})
)
"""

images_posts_labels_query = f"""
SELECT 
    IMAGES_LABELS.IMAGE_ID
    , MART_IMAGES_OF_POSTS.POST_ID
    , MART_IMAGES_OF_POSTS.AUTHORID
    , IMAGES_LABELS.LABEL_NAME
FROM ({images_labels_query}) IMAGES_LABELS
JOIN MART_IMAGES_OF_POSTS
USING(IMAGE_ID)
"""

authors_labels_occurences_query = f"""
SELECT 
    t.AUTHORID
    , t.LABEL_NAME
    , COUNT(*) LABEL_OCCURENCES 
    , COUNT(*) / ANY_VALUE(tt.TOTAL_IMAGES) AS LABEL_PERCENTAGE
FROM ({images_posts_labels_query}) t
JOIN (
    SELECT 
        AUTHORID 
        , COUNT(IMAGE_ID) AS TOTAL_IMAGES
    FROM ({images_posts_labels_query})
    GROUP BY AUTHORID
) tt
USING(AUTHORID)
GROUP BY t.AUTHORID, t.LABEL_NAME
"""

authors_labels_occurences_pivoted_query = f"""
SELECT *
FROM (
    SELECT 
        AUTHORID
        , LABEL_NAME
        , LABEL_OCCURENCES
    FROM ({authors_labels_occurences_query}) 
)
PIVOT ( MAX(LABEL_OCCURENCES) FOR LABEL_NAME IN(ANY) )
"""

authors_label_entropy_query = f"""
SELECT 
    AUTHORID
    , -SUM(LABEL_PERCENTAGE * LN(LABEL_PERCENTAGE)) AS LABEL_ENTROPY
FROM ({authors_labels_occurences_query})
GROUP BY AUTHORID
"""

authors_distinct_labels_query = f"""
SELECT 
    AUTHORID
    , COUNT(DISTINCT LABEL_NAME) AS NB_DISTINCT_LABELS
FROM ({authors_labels_occurences_query})
GROUP BY AUTHORID
"""

authors_labels_diversity_query = f"""
SELECT
    entropy.AUTHORID
    , entropy.LABEL_ENTROPY
    , dlabels.NB_DISTINCT_LABELS
FROM ({authors_label_entropy_query}) entropy
JOIN ({authors_distinct_labels_query}) dlabels
USING(AUTHORID)
"""


## ====== AUTHORS ENRICHED ====== ##

authors_enriched_query = f"""
SELECT 
    AUTHORS.AUTHORID
    , AUTHORS.NB_FOLLOWS
    , AUTHORS.NB_FOLLOWERS
    , AUTHORS.NB_FOLLOWERS_LN1P
    , AUTHORS.FASHION_INTEREST_SEGMENT
    , LABEL_DIVERSITY.LABEL_ENTROPY
    , LABEL_DIVERSITY.NB_DISTINCT_LABELS
    , POST_SUMMARY.AVG_LIKES
    , POST_SUMMARY.AVG_LIKES_LN1P
    , POST_SUMMARY.VAR_LIKES
    , POST_SUMMARY.AVG_COMMENTS
    , POST_SUMMARY.AVG_COMMENTS_LN1P
    , POST_SUMMARY.VAR_COMMENTS
    , POST_SUMMARY.NB_POSTS
    , POST_SUMMARY.NB_POSTS_LN1P
    , POST_SUMMARY.NB_IMAGES
    , POST_SUMMARY.NB_IMAGES_LN1P
    , POST_SUMMARY.NB_DAYS_SINCE_FIRST_POST
    , LABELS_PIVOTED.* EXCLUDE(AUTHORID)
FROM ({clean_authors_query}) AUTHORS
JOIN ({authors_labels_diversity_query}) LABEL_DIVERSITY
USING(AUTHORID)
JOIN ({authors_posts_summary_logged_query}) POST_SUMMARY
USING(AUTHORID)
JOIN ({authors_labels_occurences_pivoted_query}) LABELS_PIVOTED
USING(AUTHORID)
"""