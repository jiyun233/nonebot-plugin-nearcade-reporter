from typing import Any, Optional

import httpx

_client = httpx.AsyncClient(base_url="https://nearcade.phizone.cn", timeout=10.0)


class NearcadeHttp:
    def __init__(self, api_token: str) -> None:
        self.api_token = api_token

    async def list_shops(
        self,
        keyword: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        resp = await _client.get(
            "/api/shops",
            params={
                "q": keyword,
                "page": page,
                "limit": limit,
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def update_attendance(
        self,
        *,
        arcade_id: int,
        source: str,
        games: list[tuple[int, int]],
        comment: str = "Update by Sakiko-ChuniBot",
    ) -> bool:
        resp = await _client.post(
            f"/api/shops/{source}/{arcade_id}/attendance",
            headers={
                "Authorization": f"Bearer {self.api_token}",
            },
            json={
                "games": [
                    {
                        "id": game_id,
                        "currentAttendances": count,
                    }
                    for game_id, count in games
                ],
                "comment": comment,
            },
        )
        resp.raise_for_status()
        return bool(resp.json().get("success"))
