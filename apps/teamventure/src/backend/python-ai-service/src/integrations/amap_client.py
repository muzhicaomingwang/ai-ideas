from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from src.models.config import settings
from src.utils.ttl_cache import TTLCache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AmapPoi:
    name: str
    type: str | None
    address: str | None
    location: str | None


@dataclass(frozen=True)
class AmapGeocode:
    formatted_address: str | None
    province: str | None
    city: str | None
    district: str | None
    adcode: str | None
    location: str | None


class AmapClient:
    """
    Minimal Amap (高德地图) Web Service client for destination enrichment.
    Docs: https://lbs.amap.com/api/webservice/summary
    """

    def __init__(self) -> None:
        self._enabled = bool(settings.amap_enabled) and bool(settings.amap_api_key)
        self._base_url = settings.amap_base_url.rstrip("/")
        self._key = settings.amap_api_key
        self._timeout = float(settings.amap_timeout_seconds)
        self._cache = TTLCache[str, dict[str, Any]](
            ttl_seconds=int(settings.amap_cache_ttl_seconds),
            max_size=int(settings.amap_cache_max_size),
        )

    def is_enabled(self) -> bool:
        return self._enabled

    async def enrich_destination(
        self,
        *,
        destination: str,
        activity_types: list[str],
        accommodation_level: str,
    ) -> dict[str, Any] | None:
        if not self._enabled:
            return None
        dest = (destination or "").strip()
        if not dest:
            return None

        cache_key = f"amap:dest:{dest}:a={','.join(activity_types)}:h={accommodation_level}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
                geocode = await self._geocode(client, address=dest)
                destination_city = self._normalize_city_name(
                    (geocode.city or geocode.province or geocode.district) if geocode else None
                )
                city_hint = destination_city or (geocode.district or geocode.province or dest) if geocode else dest

                categories: list[tuple[str, str]] = [
                    ("团建拓展", f"{dest} 团建 拓展 基地"),
                    ("热门景点", f"{dest} 景点"),
                ]
                if "leisure" in activity_types:
                    categories.append(("休闲度假", f"{dest} 度假 温泉"))
                if "culture" in activity_types:
                    categories.append(("文化体验", f"{dest} 博物馆 古镇"))
                if "sports" in activity_types:
                    categories.append(("运动挑战", f"{dest} 徒步 漂流 攀岩"))

                categories.append(("餐饮推荐", f"{dest} 特色餐厅"))

                pois_by_category: dict[str, list[dict[str, Any]]] = {}
                for label, keywords in categories:
                    pois = await self._place_text(client, keywords=keywords, city=city_hint)
                    pois_by_category[label] = [self._poi_to_dict(p) for p in pois]

                result: dict[str, Any] = {
                    "provider": "amap",
                    "destination": dest,
                    "destination_city": destination_city,
                    "geocode": geocode.__dict__ if geocode else None,
                    "pois": pois_by_category,
                    "notes": [
                        "POI 来自高德 WebService 文本搜索，可能存在重名/缺少营业信息；生成时优先引用名称+大致区域。",
                        "行程安排应尽量围绕同一片区，减少跨城移动。",
                    ],
                }
                self._cache.set(cache_key, result)
                return result
        except Exception as e:
            logger.warning("amap enrichment failed: dest=%s err=%s", dest, e)
            return None

    async def _geocode(self, client: httpx.AsyncClient, *, address: str) -> AmapGeocode | None:
        r = await client.get(
            "/v3/geocode/geo",
            params={
                "key": self._key,
                "address": address,
                "output": "JSON",
            },
        )
        data = r.json()
        if str(data.get("status")) != "1":
            return None
        geocodes = data.get("geocodes") or []
        if not geocodes:
            return None
        g = geocodes[0]
        city = g.get("city")
        if isinstance(city, list):
            city = city[0] if city else None
        return AmapGeocode(
            formatted_address=g.get("formatted_address"),
            province=g.get("province"),
            city=city,
            district=g.get("district"),
            adcode=g.get("adcode"),
            location=g.get("location"),
        )

    @staticmethod
    def _normalize_city_name(city: str | None) -> str | None:
        if not city:
            return None
        c = city.strip()
        if not c:
            return None
        if c.endswith("市") and len(c) > 1:
            return c[:-1]
        return c

    async def _place_text(
        self, client: httpx.AsyncClient, *, keywords: str, city: str
    ) -> list[AmapPoi]:
        r = await client.get(
            "/v3/place/text",
            params={
                "key": self._key,
                "keywords": keywords,
                "city": city,
                "citylimit": "true",
                "offset": str(int(settings.amap_max_pois_per_category)),
                "page": "1",
                "extensions": "base",
                "output": "JSON",
            },
        )
        data = r.json()
        if str(data.get("status")) != "1":
            return []
        pois = data.get("pois") or []
        out: list[AmapPoi] = []
        for p in pois:
            out.append(
                AmapPoi(
                    name=p.get("name") or "",
                    type=p.get("type"),
                    address=p.get("address"),
                    location=p.get("location"),
                )
            )
        return out

    def _poi_to_dict(self, poi: AmapPoi) -> dict[str, Any]:
        return {
            "name": poi.name,
            "type": poi.type,
            "address": poi.address,
            "location": poi.location,
        }
