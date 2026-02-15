import asyncio
import json
import random
from typing import Optional, Dict, Any, List

from curl_cffi.requests import AsyncSession

from core.db.tables import Tweet


async def get_tweet_by_id(
    tweet_id: str,
    guest_token: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> Dict[str, Any]:
    """
    Получение данных твита по ID через GraphQL API X (неавторизованный запрос)

    Args:
        tweet_id: ID твита
        guest_token: Guest token для API (если None, нужно получить отдельно)
        session: Существующая сессия curl_cffi (опционально)

    Returns:
        Словарь с данными твита
    """
    url = "https://api.x.com/graphql/d6YKjvQ920F-D4Y1PruO-A/TweetResultByRestId"

    variables = {
        "tweetId": tweet_id,
        "withCommunity": False,
        "includePromotedContent": False,
        "withVoice": False,
    }

    features = {
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "premium_content_api_read_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
        "responsive_web_grok_analyze_post_followups_enabled": False,
        "responsive_web_jetfuel_frame": True,
        "responsive_web_grok_share_attachment_enabled": True,
        "responsive_web_grok_annotations_enabled": True,
        "articles_preview_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "responsive_web_grok_show_grok_translated_post": False,
        "responsive_web_grok_analysis_button_from_backend": True,
        "post_ctas_fetch_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "profile_label_improvements_pcf_label_in_post_enabled": True,
        "responsive_web_profile_redirect_enabled": False,
        "rweb_tipjar_consumption_enabled": False,
        "verified_phone_label_enabled": False,
        "responsive_web_grok_image_annotation_enabled": True,
        "responsive_web_grok_imagine_annotation_enabled": True,
        "responsive_web_grok_community_note_auto_translation_is_enabled": False,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    }

    field_toggles = {
        "withArticleRichContentState": True,
        "withArticlePlainText": False,
        "withGrokAnalyze": False,
        "withDisallowedReplyControls": False,
    }

    params = {
        "variables": json.dumps(variables, separators=(",", ":")),
        "features": json.dumps(features, separators=(",", ":")),
        "fieldToggles": json.dumps(field_toggles, separators=(",", ":")),
    }

    headers = {
        "accept": "*/*",
        "accept-language": "ru,en;q=0.9",
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://x.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://x.com/",
        "sec-ch-ua": '"Chromium";v="142", "YaBrowser";v="25.12", "Not_A Brand";v="99", "Yowser";v="2.5"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "ru",
    }

    if guest_token:
        headers["x-guest-token"] = guest_token

    close_session = False
    if session is None:
        session = AsyncSession(impersonate="chrome")
        close_session = True

    try:
        response = await session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    finally:
        if close_session:
            await session.close()


async def get_guest_token(session: Optional[AsyncSession] = None) -> str:
    """
    Получение guest token для неавторизованных запросов

    Returns:
        Guest token
    """
    url = "https://api.x.com/1.1/guest/activate.json"

    headers = {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }

    close_session = False
    if session is None:
        session = AsyncSession(impersonate="chrome")
        close_session = True

    try:
        response = await session.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["guest_token"]
    finally:
        if close_session:
            await session.close()


def extract_tweet_stats(data: dict) -> dict | None:
    """
    Быстрое извлечение статистики твита.
    Возвращает None если данных нет.
    """
    try:
        result = data["data"]["tweetResult"]["result"]

        # Проверка на пустой результат
        if not result or "legacy" not in result:
            return None

        legacy = result["legacy"]
        views = result.get("views", {})

        return {
            "views_count": int(views.get("count", 0)) if views.get("count") else 0,
            "bookmark_count": legacy.get("bookmark_count", 0),
            "favorite_count": legacy.get("favorite_count", 0),
            "retweet_count": legacy.get("retweet_count", 0),
            "quote_count": legacy.get("quote_count", 0),
            "reply_count": legacy.get("reply_count", 0),
        }
    except (KeyError, TypeError):
        return None


async def get_tweet_stats(
    tweet_id: str,
    guest_token: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> Dict[str, Any]:
    data = await get_tweet_by_id(tweet_id, guest_token, session)
    return extract_tweet_stats(data)


# Пример использования
async def get_stats(tweets: List[Tweet]):
    browsers = [
        # Chrome Desktop (65% всего трафика) - самый популярный
        "chrome142",
        "chrome136",
        "chrome133a",
        "chrome131",
        "chrome124",
        "chrome123",
        "chrome120",
        "chrome119",
        "chrome116",
        "chrome110",
        "chrome107",
        "chrome104",
        "chrome101",
        "chrome100",
        "chrome99",
        # Chrome Mobile Android (15%) - второй по популярности
        "chrome131_android",
        "chrome99_android",
        # Safari Desktop (6%) - macOS пользователи
        "safari260",
        "safari184",
        "safari180",
        "safari170",
        "safari155",
        "safari153",
        # Safari iOS (8%) - iPhone/iPad
        "safari260_ios",
        "safari184_ios",
        "safari180_ios",
        "safari172_ios",
        # Edge (3%) - Windows 10/11
        "edge101",
        "edge99",
        # Firefox (2.5%) - privacy-focused users
        "firefox144",
        "firefox135",
        "firefox133",
        # Tor (0.5%) - очень редко
        "tor145",
    ]

    # Веса соответствуют реальной статистике использования
    weights = [
        # Chrome Desktop (15 версий) - 65% / 15 = ~4.33% каждая
        0.045,
        0.045,
        0.045,
        0.045,
        0.045,  # Новые версии популярнее
        0.043,
        0.043,
        0.043,
        0.043,
        0.043,
        0.042,
        0.042,
        0.042,
        0.042,
        0.042,
        # Chrome Android (2 версии) - 15% / 2 = 7.5% каждая
        0.08,
        0.07,
        # Safari Desktop (6 версий) - 6% / 6 = 1% каждая
        0.012,
        0.011,
        0.010,
        0.010,
        0.009,
        0.008,
        # Safari iOS (4 версии) - 8% / 4 = 2% каждая
        0.022,
        0.020,
        0.020,
        0.018,
        # Edge (2 версии) - 3% / 2 = 1.5% каждая
        0.016,
        0.014,
        # Firefox (3 версии) - 2.5% / 3 = ~0.83% каждая
        0.009,
        0.008,
        0.008,
        # Tor (1 версия) - 0.5%
        0.005,
    ]

    browser_to_emulate = random.choices(browsers, weights)[0]

    semaphore = asyncio.Semaphore(10)

    tweet_ids = [tweet.tweet_id for tweet in tweets]

    async with AsyncSession(impersonate=browser_to_emulate) as session:
        # Получаем guest token
        guest_token = await get_guest_token(session)

        tasks = [get_tweet_stats(tweet, guest_token, session) for tweet in tweet_ids]
        async with semaphore:
            results = await asyncio.gather(*tasks)
    stats = {tweet_id: result for tweet_id, result in zip(tweet_ids, results)}

    return stats
