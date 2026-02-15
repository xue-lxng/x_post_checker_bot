from typing import Dict, Any, List, Tuple

from core.db.tables import Tweet
from core.utils.x_community_checker import get_community_posts
from core.utils.x_post_checker import get_stats


async def get_stats_service(
    tweets: List[Tweet],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    tweet_data = await get_stats(tweets)
    tweets_in_community = [tweet for tweet in tweets if tweet.community_id is not None]
    tweet_on_top = await get_community_posts(tweets_in_community)
    return tweet_data, tweet_on_top
