import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tgstat_client import TGStatClient

load_dotenv()

_TOKEN = os.environ.get("TGSTAT_TOKEN", "")
if not _TOKEN:
    raise RuntimeError("TGSTAT_TOKEN env variable is required")

mcp = FastMCP("tgstat")


def _client() -> TGStatClient:
    return TGStatClient(_TOKEN)


# ──────────────────────────────────────────────
# Каналы
# ──────────────────────────────────────────────

@mcp.tool()
async def get_channel(channel_id: str) -> dict:
    """Получить информацию о Telegram-канале или чате.

    channel_id: @username, t.me/username, t.me/joinchat/... или числовой ID в TGStat.
    """
    async with _client() as c:
        return await c.channel_get(channel_id)


@mcp.tool()
async def search_channels(
    query: str,
    limit: int = 20,
    peer_type: str = "channel",
    country: Optional[str] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
    participants_min: Optional[int] = None,
    participants_max: Optional[int] = None,
    er_min: Optional[float] = None,
    er_max: Optional[float] = None,
    verified: Optional[int] = None,
) -> dict:
    """Поиск Telegram-каналов и чатов по названию или описанию.

    peer_type: channel | chat
    limit: макс. 100
    """
    async with _client() as c:
        return await c.channel_search(
            q=query,
            limit=limit,
            peer_type=peer_type,
            country=country,
            language=language,
            category=category,
            participants_min=participants_min,
            participants_max=participants_max,
            er_min=er_min,
            er_max=er_max,
            verified=verified,
        )


@mcp.tool()
async def get_channel_stat(channel_id: str) -> dict:
    """Получить основные показатели канала: подписчики, охват, ERR, ER, ИЦ и т.д.

    channel_id: @username, t.me/username или числовой ID в TGStat.
    """
    async with _client() as c:
        return await c.channel_stat(channel_id)


@mcp.tool()
async def get_channel_posts(
    channel_id: str,
    limit: int = 20,
    offset: int = 0,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    hide_forwards: bool = False,
    hide_deleted: bool = False,
    extended: bool = False,
) -> dict:
    """Получить список публикаций канала.

    start_time / end_time: unix timestamp (не startDate/endDate!).
    extended=True добавляет объект канала в ответ.
    """
    async with _client() as c:
        return await c.channel_posts(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            hide_forwards=hide_forwards,
            hide_deleted=hide_deleted,
            extended=extended,
        )


@mcp.tool()
async def get_channel_stories(
    channel_id: str,
    limit: int = 20,
    offset: int = 0,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    hide_expired: bool = False,
) -> dict:
    """Получить список историй канала.

    start_time / end_time: unix timestamp.
    hide_expired=True скрывает истёкшие истории.
    """
    async with _client() as c:
        return await c.channel_stories(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            hide_expired=hide_expired,
        )


@mcp.tool()
async def get_channel_mentions(
    channel_id: str,
    limit: int = 20,
    offset: int = 0,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    extended: bool = False,
) -> dict:
    """Получить список упоминаний канала в других каналах.

    start_date / end_date: unix timestamp.
    """
    async with _client() as c:
        return await c.channel_mentions(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            extended=extended,
        )


@mcp.tool()
async def get_channel_forwards(
    channel_id: str,
    limit: int = 20,
    offset: int = 0,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    extended: bool = False,
) -> dict:
    """Получить список репостов публикаций канала в другие каналы.

    start_date / end_date: unix timestamp.
    """
    async with _client() as c:
        return await c.channel_forwards(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            extended=extended,
        )


@mcp.tool()
async def get_channel_subscribers(
    channel_id: str,
    group: str = "day",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list:
    """Динамика подписчиков канала по периодам.

    group: hour | day | week | month
    """
    async with _client() as c:
        return await c.channel_subscribers(
            channel_id=channel_id,
            group=group,
            start_date=start_date,
            end_date=end_date,
        )


@mcp.tool()
async def get_channel_views(
    channel_id: str,
    group: str = "day",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list:
    """Динамика просмотров канала по периодам.

    group: day | week | month
    """
    async with _client() as c:
        return await c.channel_views(
            channel_id=channel_id,
            group=group,
            start_date=start_date,
            end_date=end_date,
        )


@mcp.tool()
async def get_channel_avg_reach(
    channel_id: str,
    group: str = "day",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list:
    """Динамика среднего охвата публикаций канала.

    group: day | week | month
    """
    async with _client() as c:
        return await c.channel_avg_posts_reach(
            channel_id=channel_id,
            group=group,
            start_date=start_date,
            end_date=end_date,
        )


@mcp.tool()
async def get_channel_er(
    channel_id: str,
    group: str = "day",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list:
    """Динамика ER (Engagement Rate) канала — вовлечённость во взаимодействия.

    group: day | week | month
    """
    async with _client() as c:
        return await c.channel_er(
            channel_id=channel_id,
            group=group,
            start_date=start_date,
            end_date=end_date,
        )


@mcp.tool()
async def get_channel_err(
    channel_id: str,
    group: str = "day",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list:
    """Динамика ERR (Engagement Rate by Reach) канала — вовлечённость относительно охвата.

    group: day | week | month
    """
    async with _client() as c:
        return await c.channel_err(
            channel_id=channel_id,
            group=group,
            start_date=start_date,
            end_date=end_date,
        )


@mcp.tool()
async def get_channel_err24(
    channel_id: str,
    group: str = "day",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> list:
    """Динамика ERR24 (ERR за первые 24 часа после публикации) канала.

    group: day | week | month
    """
    async with _client() as c:
        return await c.channel_err24(
            channel_id=channel_id,
            group=group,
            start_date=start_date,
            end_date=end_date,
        )


@mcp.tool()
async def add_channel(channel_id: str) -> dict:
    """Добавить канал в TGStat для начала отслеживания статистики."""
    async with _client() as c:
        return await c.channel_add(channel_id)


# ──────────────────────────────────────────────
# Публикации
# ──────────────────────────────────────────────

@mcp.tool()
async def get_post(post_id: str) -> dict:
    """Получить данные публикации: просмотры, дата, текст, медиа.

    post_id: t.me/username/123, t.me/c/1256804429/1230 или числовой ID в TGStat.
    """
    async with _client() as c:
        return await c.post_get(post_id)


@mcp.tool()
async def get_post_stat(post_id: str, group: str = "day") -> dict:
    """Подробная статистика публикации: просмотры, репосты, реакции, динамика.

    post_id: t.me/username/123 или числовой ID в TGStat.
    group: hour | day
    """
    async with _client() as c:
        return await c.post_stat(post_id, group=group)


@mcp.tool()
async def get_posts_stat_multi(channel_id: str, post_ids: list[str]) -> list:
    """Статистика нескольких публикаций одного канала за один запрос (макс. 50).

    channel_id: @username или ID канала в TGStat.
    post_ids: список числовых ID публикаций в TGStat.
    """
    async with _client() as c:
        return await c.post_stat_multi(channel_id, post_ids)


@mcp.tool()
async def search_posts(
    query: str,
    limit: int = 20,
    offset: int = 0,
    peer_type: str = "all",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    country: Optional[str] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
    hide_forwards: bool = False,
    hide_deleted: bool = False,
    strong_search: bool = False,
    minus_words: Optional[str] = None,
    extended: bool = True,
) -> dict:
    """Поиск публикаций в Telegram по ключевому слову.

    peer_type: channel | chat | all
    start_date / end_date: unix timestamp
    extended=True добавляет объекты каналов в ответ.
    """
    async with _client() as c:
        return await c.posts_search(
            query=query,
            limit=limit,
            offset=offset,
            peer_type=peer_type,
            start_date=start_date,
            end_date=end_date,
            country=country,
            language=language,
            category=category,
            hide_forwards=hide_forwards,
            hide_deleted=hide_deleted,
            strong_search=strong_search,
            minus_words=minus_words,
            extended=extended,
        )


# ──────────────────────────────────────────────
# Истории
# ──────────────────────────────────────────────

@mcp.tool()
async def get_story(story_id: str) -> dict:
    """Получить данные истории: просмотры, дата, медиа, подпись.

    story_id: t.me/username/s/123, t.me/c/1256804429/s/1230 или числовой ID в TGStat.
    """
    async with _client() as c:
        return await c.story_get(story_id)


@mcp.tool()
async def get_story_stat(story_id: str) -> dict:
    """Статистика истории: просмотры, репосты, реакции, динамика по часам."""
    async with _client() as c:
        return await c.story_stat(story_id)


@mcp.tool()
async def get_stories_stat_multi(channel_id: str, story_ids: list[str]) -> list:
    """Статистика нескольких историй одного канала за один запрос (макс. 50).

    channel_id: @username или ID канала в TGStat.
    story_ids: список числовых ID историй в TGStat.
    """
    async with _client() as c:
        return await c.story_stat_multi(channel_id, story_ids)


# ──────────────────────────────────────────────
# Ключевые слова
# ──────────────────────────────────────────────

@mcp.tool()
async def get_keyword_mentions_by_period(
    query: str,
    group: str = "day",
    peer_type: str = "all",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    hide_forwards: bool = False,
    strong_search: bool = False,
    minus_words: Optional[str] = None,
) -> dict:
    """Динамика упоминаний ключевого слова в Telegram по дням/неделям/месяцам.

    group: day | week | month
    peer_type: channel | chat | all
    По умолчанию возвращает последние 10 дней.
    """
    async with _client() as c:
        return await c.words_mentions_by_period(
            q=query,
            group=group,
            peer_type=peer_type,
            start_date=start_date,
            end_date=end_date,
            hide_forwards=hide_forwards,
            strong_search=strong_search,
            minus_words=minus_words,
        )


@mcp.tool()
async def get_keyword_mentions_by_channels(
    query: str,
    peer_type: str = "all",
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    hide_forwards: bool = False,
    strong_search: bool = False,
    minus_words: Optional[str] = None,
) -> dict:
    """Упоминания ключевого слова с группировкой по каналам (кто чаще пишет на тему).

    peer_type: channel | chat | all
    """
    async with _client() as c:
        return await c.words_mentions_by_channels(
            q=query,
            peer_type=peer_type,
            start_date=start_date,
            end_date=end_date,
            hide_forwards=hide_forwards,
            strong_search=strong_search,
            minus_words=minus_words,
        )


# ──────────────────────────────────────────────
# Callback API
# ──────────────────────────────────────────────

@mcp.tool()
async def set_callback_url(callback_url: str) -> dict:
    """Установить Callback URL для получения webhook-уведомлений от TGStat.

    Требует подтверждения URL: TGStat отправит POST-запрос и ожидает verify_code в ответе.
    """
    async with _client() as c:
        return await c.callback_set_url(callback_url)


@mcp.tool()
async def get_callback_info() -> dict:
    """Получить информацию о текущем Callback URL, ошибках и размере очереди."""
    async with _client() as c:
        return await c.callback_get_info()


@mcp.tool()
async def subscribe_channel_events(
    channel_id: str,
    event_types: list[str],
    subscription_id: Optional[int] = None,
) -> dict:
    """Подписаться на события Telegram-канала через Callback API.

    channel_id: @username или ID в TGStat.
    event_types: список из new_post, edit_post, remove_post.
    subscription_id: передать для редактирования существующей подписки.
    """
    async with _client() as c:
        return await c.callback_subscribe_channel(
            channel_id=channel_id,
            event_types=event_types,
            subscription_id=subscription_id,
        )


@mcp.tool()
async def subscribe_keyword_events(
    query: str,
    event_types: Optional[list[str]] = None,
    strong_search: bool = False,
    minus_words: Optional[str] = None,
    peer_types: str = "channel",
    subscription_id: Optional[int] = None,
) -> dict:
    """Подписаться на упоминания ключевого слова через Callback API.

    event_types: ['new_post'] (единственный поддерживаемый тип).
    peer_types: channel | chat | all.
    subscription_id: передать для редактирования существующей подписки.
    """
    async with _client() as c:
        return await c.callback_subscribe_word(
            q=query,
            event_types=event_types,
            strong_search=strong_search,
            minus_words=minus_words,
            peer_types=peer_types,
            subscription_id=subscription_id,
        )


@mcp.tool()
async def list_subscriptions(
    subscription_id: Optional[int] = None,
    subscription_type: Optional[str] = None,
) -> dict:
    """Получить список активных Callback-подписок.

    subscription_type: channel | keyword (не указывать = все).
    """
    async with _client() as c:
        return await c.callback_subscriptions_list(
            subscription_id=subscription_id,
            subscription_type=subscription_type,
        )


@mcp.tool()
async def unsubscribe(subscription_id: int) -> dict:
    """Отменить Callback-подписку по её ID."""
    async with _client() as c:
        return await c.callback_unsubscribe(subscription_id)


# ──────────────────────────────────────────────
# Использование API
# ──────────────────────────────────────────────

@mcp.tool()
async def get_usage_stat() -> list:
    """Статистика использования TGStat API: тарифы, квоты, лимиты, расход запросов."""
    async with _client() as c:
        return await c.usage_stat()


# ──────────────────────────────────────────────
# Справочники
# ──────────────────────────────────────────────

@mcp.tool()
async def get_countries() -> list:
    """Список стран для фильтрации каналов и публикаций."""
    async with _client() as c:
        return await c.get_countries()


@mcp.tool()
async def get_languages() -> list:
    """Список языков для фильтрации каналов и публикаций."""
    async with _client() as c:
        return await c.get_languages()


@mcp.tool()
async def get_categories() -> list:
    """Список категорий каналов для фильтрации."""
    async with _client() as c:
        return await c.get_categories()


# ──────────────────────────────────────────────
# Агрегированные инструменты
# ──────────────────────────────────────────────

@mcp.tool()
async def analyze_audience(
    query: str,
    limit: int = 50,
    country: Optional[str] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """Анализ аудитории Telegram-каналов по поисковому запросу.

    Возвращает сводную статистику вовлечённости, распределение каналов по размеру
    и анализ типов контента на основе публикаций по запросу.
    """
    async with _client() as c:
        results = await c.posts_search(
            query=query,
            limit=min(limit, 50),
            country=country,
            language=language,
            category=category,
            extended=True,
        )

    items: list = results.get("items", [])
    channels: list = results.get("channels", [])

    total_views = sum(p.get("views", 0) for p in items)
    total_shares = sum(p.get("shares_count", 0) for p in items)
    total_comments = sum(p.get("comments_count", 0) for p in items)
    n = len(items) or 1

    size_buckets: dict[str, int] = {"small": 0, "medium": 0, "large": 0, "mega": 0}
    total_participants = 0
    for ch in channels:
        p = ch.get("participants_count", 0)
        total_participants += p
        if p < 1_000:
            size_buckets["small"] += 1
        elif p < 10_000:
            size_buckets["medium"] += 1
        elif p < 100_000:
            size_buckets["large"] += 1
        else:
            size_buckets["mega"] += 1

    media_types: dict[str, int] = {}
    for post in items:
        media = post.get("media")
        if media:
            mt = media.get("media_type", "unknown")
            media_types[mt] = media_types.get(mt, 0) + 1

    return {
        "query": query,
        "total_posts_found": results.get("total_count", 0),
        "analyzed_posts": len(items),
        "unique_channels": len(channels),
        "engagement": {
            "total_views": total_views,
            "total_shares": total_shares,
            "total_comments": total_comments,
            "avg_views": round(total_views / n, 1),
            "avg_shares": round(total_shares / n, 1),
        },
        "channels": {
            "total_participants": total_participants,
            "avg_participants": round(total_participants / (len(channels) or 1)),
            "size_distribution": size_buckets,
        },
        "content": {
            "media_types": media_types,
            "posts_with_text": sum(1 for p in items if p.get("text")),
        },
    }


@mcp.tool()
async def get_audience_insights(
    keywords: list[str],
    country: Optional[str] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """Сравнительный анализ аудитории по нескольким ключевым словам.

    Возвращает анализ по каждому слову и итоговую сводную таблицу.
    """
    analyses = []
    for kw in keywords:
        async with _client() as c:
            results = await c.posts_search(
                query=kw, limit=30, country=country,
                language=language, category=category, extended=True,
            )
        items = results.get("items", [])
        channels = results.get("channels", [])
        n = len(items) or 1
        total_views = sum(p.get("views", 0) for p in items)
        analyses.append({
            "keyword": kw,
            "posts_found": results.get("total_count", 0),
            "analyzed": len(items),
            "channels": len(channels),
            "total_participants": sum(ch.get("participants_count", 0) for ch in channels),
            "total_views": total_views,
            "avg_views": round(total_views / n, 1),
        })

    return {
        "keywords": keywords,
        "analyses": analyses,
        "summary": {
            "total_posts": sum(a["posts_found"] for a in analyses),
            "total_channels": sum(a["channels"] for a in analyses),
            "total_audience": sum(a["total_participants"] for a in analyses),
            "total_views": sum(a["total_views"] for a in analyses),
        },
    }


if __name__ == "__main__":
    mcp.run()
