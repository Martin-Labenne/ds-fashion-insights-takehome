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

## ====== IMAGES LABELS ====== ##

images_types_query = """
SELECT 
    DISTINCT 
        IMAGE_ID
        , TYPE 
        , 1 AS is_type
FROM MART_IMAGES_LABELS
"""

images_labels_query = """
SELECT 
    DISTINCT
        IMAGE_ID
        , LABEL_NAME
        , 1 AS is_label
FROM MART_IMAGES_LABELS
"""

images_types_labels_query = """
SELECT 
    DISTINCT
        IMAGE_ID
        , TYPE
        , LABEL_NAME
FROM MART_IMAGES_LABELS
"""

images_types_pivoted_query = f"""
SELECT *
FROM ({images_types_query}) 
PIVOT ( COUNT(is_type) FOR TYPE IN(ANY) )
"""

images_labels_pivoted_query = f"""
SELECT *
FROM ({images_labels_query}) 
PIVOT ( COUNT(is_label) FOR LABEL_NAME IN(ANY) )
"""