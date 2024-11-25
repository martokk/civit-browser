from typing import Any

import httpx
from fastapi import HTTPException
from sqlmodel import Session

from app import crud


async def fetch_cursor_data(cursor: str, db: Session) -> dict[str, Any]:
    """Fetch images for a given cursor and return the JSON response"""
    settings = await crud.settings.get_current(db)

    if not settings or not settings.cookie_string:
        raise HTTPException(
            status_code=400, detail="Civitai cookie not configured. Please set it in Settings."
        )

    base_url = "https://civitai.com/api/trpc/orchestrator.queryGeneratedImages"
    params = (
        "?input=%7B%22json%22%3A%7B%22tags%22%3A%5B%22gen%22%5D%2C%22cursor%22%3A%22"
        f"{cursor}%22%2C%22authed%22%3Atrue%7D%7D"
    )
    url = base_url + params

    headers = {
        "Host": "civitai.com",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Cookie": settings.cookie_string,
        "X-Client": "web",
        "X-Client-Version": "5.0.289",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise HTTPException(
                    status_code=response.status_code, detail=f"Civitai API error: {data['error']}"
                )

            if "result" not in data or "data" not in data["result"]:
                raise HTTPException(
                    status_code=500, detail="Invalid response format from Civitai API"
                )

            # Extract relevant data
            result = {"next_cursor": data["result"]["data"]["json"].get("nextCursor"), "images": []}

            # Process each item's images
            for item in data["result"]["data"]["json"]["items"]:
                for step in item["steps"]:
                    for image in step["images"]:
                        result["images"].append(image)

            return result

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cursor data: {str(e)}")
