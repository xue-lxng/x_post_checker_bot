from fastscheduler import FastScheduler
from loguru import logger

from config import DB_URL
from core.db.database_handler import DatabaseHandler
from core.services.stats import get_stats_service
from core.utils.telegram import send_message

scheduler = FastScheduler(quiet=True)


@scheduler.every(1).minutes.no_catch_up()
async def check_tweets():
    db = DatabaseHandler(DB_URL)
    tweets = await db.get_all_active_tweets()
    tweets_data, tweets_on_top = await get_stats_service(tweets)
    for tweet in tweets:
        if tweets_data.get(tweet.tweet_id) is None:
            await send_message(
                str(tweet.user_id),
                (
                    f"❌⚠️ ПОСТ УДАЛЁН ⚠️❌\n"
                    f"Tweet Url: {tweet.tweet_url}\n"
                    f"Tweet ID: <code>{tweet.tweet_id}</code>\n"
                    f"Community URL: https://x.com/i/communities/{tweet.community_id}\n"
                    if tweet.community_id
                    else f"❌⚠️ ПОСТ УДАЛЁН ⚠️❌\n"
                    f"Tweet Url: {tweet.tweet_url}\n"
                    f"Tweet ID: <code>{tweet.tweet_id}</code>\n"
                ),
            )
            await db.set_as_inactive(tweet.tweet_id)
        if tweets_on_top.get(tweet.tweet_id) is None:
            continue
        elif tweets_on_top[tweet.tweet_id]:
            if not tweet.on_top:
                await send_message(
                    str(tweet.user_id),
                    (
                        f"✅⚠️ ПОСТ В ТОПЕ ⚠️✅\n"
                        f"Tweet Url: {tweet.tweet_url}\n"
                        f"Tweet ID: <code>{tweet.tweet_id}</code>\n"
                        f"Community URL: https://x.com/i/communities/{tweet.community_id}\n"
                        if tweet.community_id
                        else ""
                    ),
                )
            logger.info(
                f"Tweet {tweet.tweet_id} on Top: {tweets_on_top[tweet.tweet_id]}"
            )
            await db.set_on_top_status(tweet.tweet_id, tweet.community_id, True)
        elif not tweets_on_top[tweet.tweet_id]:
            if tweet.on_top:
                await send_message(
                    str(tweet.user_id),
                    (
                        f"❌⚠️ ПОСТ НЕ В ТОПЕ ⚠️❌\n"
                        f"Tweet Url: {tweet.tweet_url}\n"
                        f"Tweet ID: <code>{tweet.tweet_id}</code>\n"
                        f"Community URL: https://x.com/i/communities/{tweet.community_id}\n"
                        if tweet.community_id
                        else ""
                    ),
                )
            logger.info(
                f"Tweet {tweet.tweet_id} on Top: {tweets_on_top[tweet.tweet_id]}"
            )
            await db.set_on_top_status(tweet.tweet_id, tweet.community_id, False)
