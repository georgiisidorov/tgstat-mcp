import aiohttp
from typing import Any, Optional

BASE_URL = "https://api.tgstat.ru"


class TGStatError(Exception):
    pass

class TGStatTokenError(TGStatError):
    pass

class TGStatQuotaError(TGStatError):
    pass

class TGStatFloodControlError(TGStatError):
    pass

class TGStatSubscriptionError(TGStatError):
    pass


_ERROR_MAP: dict[str, tuple[type, str]] = {
    "empty_token": (TGStatTokenError, "Не передан токен TGStat API"),
    "token_invalid": (TGStatTokenError, "Невалидный токен TGStat API"),
    "flood_control_10": (TGStatFloodControlError, "Слишком частые запросы (10 сек)"),
    "flood_control_60": (TGStatFloodControlError, "Слишком частые запросы (60 сек)"),
    "no_active_subscription": (TGStatSubscriptionError, "Нет активной подписки TGStat API"),
    "quota_requests_reached": (TGStatQuotaError, "Превышена квота запросов в месяц"),
    "quota_channel_reached": (TGStatQuotaError, "Превышена квота уникальных каналов"),
    "quota_keywords_reached": (TGStatQuotaError, "Превышена квота ключевых слов"),
    "quota_foreign_channel": (TGStatQuotaError, "Доступ к чужим каналам недоступен на текущем тарифе"),
    "quota_callback_objects_reached": (TGStatQuotaError, "Превышена квота подписок Callback"),
    "outdated_statistics": (TGStatError, "Устаревшие данные, повторите через 15 минут"),
}


class TGStatClient:
    def __init__(self, token: str) -> None:
        self._token = token
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "TGStatClient":
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._session:
            await self._session.close()

    def _inject_token(self, params: dict[str, Any]) -> dict[str, Any]:
        params["token"] = self._token
        return params

    async def _get(self, endpoint: str, params: dict[str, Any]) -> Any:
        if not self._session:
            raise RuntimeError("Client not initialized — use async with")
        self._inject_token(params)
        async with self._session.get(f"{BASE_URL}{endpoint}", params=params) as resp:
            if resp.status != 200:
                raise TGStatError(f"HTTP {resp.status}: {resp.reason}")
            data = await resp.json()
        if data.get("status") != "ok":
            code = data.get("error", "unknown_error")
            exc_cls, msg = _ERROR_MAP.get(code, (TGStatError, f"TGStat error: {code}"))
            raise exc_cls(msg)
        return data.get("response")

    async def _post(self, endpoint: str, data: dict[str, Any]) -> Any:
        if not self._session:
            raise RuntimeError("Client not initialized — use async with")
        self._inject_token(data)
        async with self._session.post(f"{BASE_URL}{endpoint}", data=data) as resp:
            if resp.status != 200:
                raise TGStatError(f"HTTP {resp.status}: {resp.reason}")
            result = await resp.json()
        if result.get("status") != "ok":
            code = result.get("error", "unknown_error")
            exc_cls, msg = _ERROR_MAP.get(code, (TGStatError, f"TGStat error: {code}"))
            raise exc_cls(msg)
        return result.get("response")

    # ──────────────────────────────────────────────
    # Каналы
    # ──────────────────────────────────────────────

    async def channel_get(self, channel_id: str) -> dict:
        """Получение информации о канале. channel_id — username, ссылка или tgstat-id."""
        return await self._get("/channels/get", {"channelId": channel_id}) or {}

    async def channel_search(
        self,
        q: str,
        limit: int = 20,
        country: Optional[str] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
        peer_type: str = "channel",
        verified: Optional[int] = None,
        participants_min: Optional[int] = None,
        participants_max: Optional[int] = None,
        er_min: Optional[float] = None,
        er_max: Optional[float] = None,
    ) -> dict:
        """Поиск каналов и чатов. peer_type: channel | chat."""
        params: dict[str, Any] = {
            "q": q,
            "limit": min(limit, 100),
            "peerType": peer_type,
        }
        if country:
            params["country"] = country
        if language:
            params["language"] = language
        if category:
            params["category"] = category
        if verified is not None:
            params["verified"] = verified
        if participants_min is not None:
            params["participantsCountMin"] = participants_min
        if participants_max is not None:
            params["participantsCountMax"] = participants_max
        if er_min is not None:
            params["erMin"] = er_min
        if er_max is not None:
            params["erMax"] = er_max
        return await self._get("/channels/search", params) or {}

    async def channel_stat(self, channel_id: str) -> dict:
        """Основные показатели статистики канала."""
        return await self._get("/channels/stat", {"channelId": channel_id}) or {}

    async def channel_posts(
        self,
        channel_id: str,
        limit: int = 20,
        offset: int = 0,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        hide_forwards: bool = False,
        hide_deleted: bool = False,
        extended: bool = False,
    ) -> dict:
        """Список публикаций канала. start_time/end_time — unix timestamp."""
        params: dict[str, Any] = {
            "channelId": channel_id,
            "limit": min(limit, 50),
            "offset": offset,
            "hideForwards": int(hide_forwards),
            "hideDeleted": int(hide_deleted),
            "extended": int(extended),
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._get("/channels/posts", params) or {}

    async def channel_stories(
        self,
        channel_id: str,
        limit: int = 20,
        offset: int = 0,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        hide_expired: bool = False,
    ) -> dict:
        """Список историй канала. start_time/end_time — unix timestamp."""
        params: dict[str, Any] = {
            "channelId": channel_id,
            "limit": min(limit, 50),
            "offset": offset,
            "hideExpired": int(hide_expired),
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._get("/channels/stories", params) or {}

    async def channel_mentions(
        self,
        channel_id: str,
        limit: int = 20,
        offset: int = 0,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        extended: bool = False,
    ) -> dict:
        """Список упоминаний канала в других каналах."""
        params: dict[str, Any] = {
            "channelId": channel_id,
            "limit": min(limit, 50),
            "offset": offset,
            "extended": int(extended),
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/mentions", params) or {}

    async def channel_forwards(
        self,
        channel_id: str,
        limit: int = 20,
        offset: int = 0,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        extended: bool = False,
    ) -> dict:
        """Список репостов из канала в другие каналы."""
        params: dict[str, Any] = {
            "channelId": channel_id,
            "limit": min(limit, 50),
            "offset": offset,
            "extended": int(extended),
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/forwards", params) or {}

    async def channel_subscribers(
        self,
        channel_id: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
    ) -> list:
        """Динамика подписчиков канала. group: hour | day | week | month."""
        params: dict[str, Any] = {"channelId": channel_id, "group": group}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/subscribers", params) or []

    async def channel_views(
        self,
        channel_id: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
    ) -> list:
        """Динамика просмотров канала. group: day | week | month."""
        params: dict[str, Any] = {"channelId": channel_id, "group": group}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/views", params) or []

    async def channel_avg_posts_reach(
        self,
        channel_id: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
    ) -> list:
        """Средний охват публикаций канала в динамике. group: day | week | month."""
        params: dict[str, Any] = {"channelId": channel_id, "group": group}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/avg-posts-reach", params) or []

    async def channel_er(
        self,
        channel_id: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
    ) -> list:
        """ER (Engagement Rate) канала в динамике. group: day | week | month."""
        params: dict[str, Any] = {"channelId": channel_id, "group": group}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/er", params) or []

    async def channel_err(
        self,
        channel_id: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
    ) -> list:
        """ERR (Engagement Rate by Reach) канала в динамике. group: day | week | month."""
        params: dict[str, Any] = {"channelId": channel_id, "group": group}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/err", params) or []

    async def channel_err24(
        self,
        channel_id: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
    ) -> list:
        """ERR24 (ERR за последние 24 часа) канала в динамике. group: day | week | month."""
        params: dict[str, Any] = {"channelId": channel_id, "group": group}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._get("/channels/err24", params) or []

    async def channel_add(self, channel_id: str) -> dict:
        """Добавить канал в TGStat для отслеживания."""
        return await self._post("/channels/add", {"channelId": channel_id}) or {}

    # ──────────────────────────────────────────────
    # Публикации
    # ──────────────────────────────────────────────

    async def post_get(self, post_id: str) -> dict:
        """Данные публикации по ID или ссылке (t.me/username/123)."""
        return await self._get("/posts/get", {"postId": post_id}) or {}

    async def post_stat(self, post_id: str, group: str = "day") -> dict:
        """Статистика публикации: просмотры, репосты, реакции, динамика. group: hour | day."""
        return await self._get("/posts/stat", {"postId": post_id, "group": group}) or {}

    async def post_stat_multi(self, channel_id: str, post_ids: list[str]) -> list:
        """Статистика нескольких публикаций одного канала (макс. 50)."""
        return await self._get(
            "/posts/stat-multi",
            {"channelId": channel_id, "postsIds": ",".join(post_ids[:50])},
        ) or []

    async def posts_search(
        self,
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
        extended_syntax: bool = False,
        extended: bool = False,
    ) -> dict:
        """Поиск публикаций по ключевому слову. peer_type: channel | chat | all."""
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, 50),
            "offset": min(offset, 1000),
            "peerType": peer_type,
            "hideForwards": int(hide_forwards),
            "hideDeleted": int(hide_deleted),
            "strongSearch": int(strong_search),
            "extendedSyntax": int(extended_syntax),
            "extended": int(extended),
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if country:
            params["country"] = country
        if language:
            params["language"] = language
        if category:
            params["category"] = category
        if minus_words:
            params["minusWords"] = minus_words
        return await self._get("/posts/search", params) or {}

    # ──────────────────────────────────────────────
    # Истории
    # ──────────────────────────────────────────────

    async def story_get(self, story_id: str) -> dict:
        """Данные истории по ID или ссылке (t.me/username/s/123)."""
        return await self._get("/stories/get", {"storyId": story_id}) or {}

    async def story_stat(self, story_id: str) -> dict:
        """Статистика истории: просмотры, репосты, реакции, динамика по часам."""
        return await self._get("/stories/stat", {"storyId": story_id}) or {}

    async def story_stat_multi(self, channel_id: str, story_ids: list[str]) -> list:
        """Статистика нескольких историй одного канала (макс. 50)."""
        return await self._get(
            "/stories/stat-multi",
            {"channelId": channel_id, "storiesIds": ",".join(story_ids[:50])},
        ) or []

    # ──────────────────────────────────────────────
    # Ключевые слова
    # ──────────────────────────────────────────────

    async def words_mentions_by_period(
        self,
        q: str,
        peer_type: str = "all",
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        group: str = "day",
        hide_forwards: bool = False,
        strong_search: bool = False,
        minus_words: Optional[str] = None,
        extended_syntax: bool = False,
    ) -> dict:
        """Динамика упоминаний ключевого слова по периодам. group: day | week | month."""
        params: dict[str, Any] = {
            "q": q,
            "peerType": peer_type,
            "group": group,
            "hideForwards": int(hide_forwards),
            "strongSearch": int(strong_search),
            "extendedSyntax": int(extended_syntax),
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if minus_words:
            params["minusWords"] = minus_words
        return await self._get("/words/mentions-by-period", params) or {}

    async def words_mentions_by_channels(
        self,
        q: str,
        peer_type: str = "all",
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        hide_forwards: bool = False,
        strong_search: bool = False,
        minus_words: Optional[str] = None,
        extended_syntax: bool = False,
    ) -> dict:
        """Упоминания ключевого слова с группировкой по каналам."""
        params: dict[str, Any] = {
            "q": q,
            "peerType": peer_type,
            "hideForwards": int(hide_forwards),
            "strongSearch": int(strong_search),
            "extendedSyntax": int(extended_syntax),
        }
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if minus_words:
            params["minusWords"] = minus_words
        return await self._get("/words/mentions-by-channels", params) or {}

    # ──────────────────────────────────────────────
    # API Callback
    # ──────────────────────────────────────────────

    async def callback_set_url(self, callback_url: str) -> dict:
        """Установить URL для получения Callback-уведомлений (POST)."""
        return await self._post("/callback/set-callback-url", {"callback_url": callback_url}) or {}

    async def callback_get_info(self) -> dict:
        """Информация о текущем Callback URL, ошибках и очереди."""
        return await self._get("/callback/get-callback-info", {}) or {}

    async def callback_subscribe_channel(
        self,
        channel_id: str,
        event_types: list[str],
        subscription_id: Optional[int] = None,
    ) -> dict:
        """Подписаться на события канала (POST). event_types: new_post, edit_post, remove_post."""
        data: dict[str, Any] = {
            "channel_id": channel_id,
            "event_types": ",".join(event_types),
        }
        if subscription_id is not None:
            data["subscription_id"] = subscription_id
        return await self._post("/callback/subscribe-channel", data) or {}

    async def callback_subscribe_word(
        self,
        q: str,
        event_types: Optional[list[str]] = None,
        strong_search: bool = False,
        minus_words: Optional[str] = None,
        extended_syntax: bool = False,
        peer_types: str = "channel",
        subscription_id: Optional[int] = None,
    ) -> dict:
        """Подписаться на упоминания ключевого слова (POST). peer_types: channel | chat | all."""
        data: dict[str, Any] = {
            "q": q,
            "strong_search": int(strong_search),
            "extended_syntax": int(extended_syntax),
            "peer_types": peer_types,
        }
        if event_types:
            data["event_types"] = ",".join(event_types)
        if minus_words:
            data["minus_words"] = minus_words
        if subscription_id is not None:
            data["subscription_id"] = subscription_id
        return await self._post("/callback/subscribe-word", data) or {}

    async def callback_subscriptions_list(
        self,
        subscription_id: Optional[int] = None,
        subscription_type: Optional[str] = None,
    ) -> dict:
        """Список активных Callback-подписок. subscription_type: channel | keyword."""
        params: dict[str, Any] = {}
        if subscription_id is not None:
            params["subscription_id"] = subscription_id
        if subscription_type:
            params["subscription_type"] = subscription_type
        return await self._get("/callback/subscriptions-list", params) or {}

    async def callback_unsubscribe(self, subscription_id: int) -> dict:
        """Отменить Callback-подписку по ID (POST)."""
        return await self._post("/callback/unsubscribe", {"subscription_id": subscription_id}) or {}

    # ──────────────────────────────────────────────
    # Использование API
    # ──────────────────────────────────────────────

    async def usage_stat(self) -> list:
        """Статистика использования API: тарифы, квоты, лимиты, расход запросов."""
        return await self._get("/usage/stat", {}) or []

    # ──────────────────────────────────────────────
    # Справочники
    # ──────────────────────────────────────────────

    async def get_countries(self) -> list:
        return await self._get("/database/countries", {}) or []

    async def get_languages(self) -> list:
        return await self._get("/database/languages", {}) or []

    async def get_categories(self) -> list:
        return await self._get("/database/categories", {}) or []
