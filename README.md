# Social Media Fashion Insights

## Setup

### Install Requirements

```sh
pip install -r requirements.txt
```

### Setup Env variables

- copy paste `.env.default` to `.env` file newly created.
- go to your account details in snowflake and fill the user infos + password
- test your connection: get first 3 authors in the db

```sh
python3 snowflake_utils.py
```

## Data Exploration

In the first notebook, I conducted an initial exploration of the provided data. Here are the key takeaways:

- _Followers distribution_: The log-transformed number of followers follows an approximately normal distribution, with a slight deviation suggesting at least two overlapping distributions. The number of followers and accounts followed appear uncorrelated, as expected.
- _Image labels_: The table results from a two-step image recognition process, including object coordinates that will be omitted as they are irrelevant to segmentation. Some labels, such as clothing items (top, shoes, dress, etc.) and accessories (earrings, hat, bag, etc.), are particularly relevant to the business.
- _Log Distributions_: Exploiting the log distribution of NB_FOLLOWERS, average NB_LIKES and average COMMENTS_COUNT will be easier than their original distribution.
- Text fields excluded: Free-text fields will not be considered due to challenges in processing multilingual content, varying alphabets, and emojis, which require a separate study.

Although this section is not particularly exciting, it helped me grasp the subtleties of the data and laid the groundwork for designing the transformation pipeline for downstream tasks.

## Segmentation Analysis and Discussion

### What kind of analysis would you do to evaluate the quality of a segmentation methodology?

Simple analysis can still be powerfull to have a good opinion on segmentation quality:

- _Correlation between Followers and Engagement_: strong correlation between the number of followers and the average likes/comments across accounts. This suggests that, generally, larger accounts tend to have higher engagement.
- _Imbalance in Account Categories_: There is a significant imbalance in the distribution of account types within the dataset. Mainstream accounts dominate the dataset, with far fewer accounts categorized as trendy or edgy.
- _Engagement by Account Type_: Edgy accounts show the highest engagement, followed by trendy accounts, then mainstream accounts which have the most outliers in engagement metrics.

The alignment with business reality (correlation and decreasing population with a higher number of followers) suggests that this segmentation is a solid starting point. However, the mainstream category is overly populated, leading to more outliers overall. It might be beneficial to either split this category or design a more refined and nuanced segmentation approach.

### What biases can you identify in the panel creation or in the accounts selection that might distort insights and how would you correct them?

One bias in the panel creation or account selection process is the presence of extreme values, which can distort distributions and affect segmentation quality. In the context of social media influence, these outliers often represent highly impactful individuals, making their exclusion problematic. Rather than removing them outright, I chose to apply a log transformation to normalize the distribution while preserving their relative importance. This approach smooths discrepancies and allows for more meaningful comparisons across different account sizes.

Alternatively, a stricter approach could involve filtering out these extreme values entirely, but this might lead to an incomplete representation of the influencer landscape, depending on the business objective.

### What do you think about the current segmentation?

Fashion can be divided into three categories based on cultural norms and adoption cycles:

- _Mainstream_ Fashion: Widely accepted and practical, often seen in major retailers and luxury brands. Includes timeless styles like tailored suits or denim, influenced by traditional fashion authorities (runways, celebrities). It has mass adoption and long-lasting trends.

- _Trendy_ Fashion: Popular for a short period, driven by social media and influencers. It features rapid shifts and experimental styles within socially acceptable limits (e.g., oversized blazers, chunky sneakers). Trends peak quickly but fade fast.

- _Edgy_ Fashion: Challenges conventions with alternative, rebellious aesthetics (e.g., punk, goth). Often seen in avant-garde designers and niche communities. It has a cult following and may occasionally influence mainstream fashion.

The proposed approach suggests a segmentation that follows an intuitive logic: mainstream represents the largest share, followed by a smaller trendy group, and an even more limited edgy segment. This aligns with reality, where dominant fashion is the most visible and widely adopted, while more avant-garde styles remain niche.

However, this segmentation relies only on the number of followers, a metric that measures popularity rather than actual fashion influence. In the fashion world, there is a common tendency to overestimate the importance of edgy styles. Artistic circles often perceive avant-garde fashion as more influential than it actually is, partly because they focus on it more. In reality, mainstream fashion remains dominant—it is more accessible, less expensive, and widely distributed.

The trendy segment, on the other hand, occupies a middle ground, constantly shifting with the rise and fall of trends. What is trendy today often becomes mainstream tomorrow. This transition can happen quickly, with some trends taking only a few months to be absorbed into the mainstream. In contrast, influences from the avant-garde take much longer to trickle down—what is considered edgy today may take years before becoming widely adopted.

This is why, while the proposed segmentation is simple and easy to understand, it does not accurately reflect the business reality of fashion. A more refined analysis would need to go beyond follower count and incorporate elements such as actual influence on trends and the time dynamics between edgy, trendy, and mainstream.

### What is your take on the way the information is stored?

With a rule as simple as splitting on a column, partitioning or sharding could be a solution to explicitly enforce physical data segmentation. However, there is no proper partitioning in either of the provided tables, MART_AUTHORS or MART_AUTHORS_SEGMENTATIONS. While this is acceptable given the provided data volume—since segmentation can be computed at query time—it does not explicitly reflect the business logic at the presentation layer.

Another approach could be deriving a categorical feature from NB_FOLLOWERS to store the segment directly as an attribute. This would make queries more efficient and self-explanatory while allowing for more complex segmentation rules beyond simple thresholding. However, this would require clear governance on how and when the segmentation is updated.

### Which approach would you prefer (Statistical, Machine Learning or Hybrid approach) to improve the segmentation methodology ? What would be the advantages/limits of each of these methods?

In the context of this question, I explored three approaches, although none provided definitive results. However, each method offers distinct insights and advances the debate in a meaningful way:

- _NMF on image labels_: Non-Negative Matrix Factorization is particularly effective for uncovering latent themes within fashion styles, making it valuable for content categorization. It can help identify patterns that might not be immediately obvious from the raw data. However, its success heavily relies on the quality and granularity of the image labels, as poor labeling or oversimplified categories may lead to less meaningful topics. Additionally, NMF doesn’t provide direct user segmentation, but it’s instrumental in identifying themes that could be incorporated into other models.
- _K-Means on user features:_ This approach is a widely used technique for segmenting users based on their behaviors. It’s simple and computationally efficient, providing clear-cut groupings. However, it assumes that the data clusters in a spherical shape, which might not always reflect the true structure of user behaviors. Furthermore, K-Means is sensitive to the choice of the number of clusters and initial centroids, which could lead to suboptimal partitions if not carefully tuned.
- _Hybrid approach NMF > K-Means_: In this combined approach, fashion topics derived from NMF are used as additional features for K-Means clustering. This method takes advantage of both content-based insights (fashion themes) and behavioral patterns (user features), allowing for a more nuanced segmentation. By incorporating fashion topics as features, the model can group users not only by their engagement patterns but also by their affinity for specific fashion themes, leading to more sophisticated user segments. While this hybrid approach adds complexity, it may offer the most balanced and insightful segmentation, especially when dealing with diverse user interests in fashion.

In conclusion, the hybrid approach of combining NMF and K-Means offers a more refined segmentation by integrating both fashion themes and user behaviors. While more complex, it could provide a better representation of user interests, addressing the limitations of individual methods and improving segmentation accuracy.

## Annex

For an overview of the transformations, see [here](transformation_diagram.jpg)
