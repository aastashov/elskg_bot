import asyncio
import re
from typing import List

import httpx

url = "https://dash.els.kg/find_tracking?q={}"
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/javascript",
}


def _get_status_text(text: str) -> str:
    html = text.replace('document.getElementById("package").innerHTML = ', "")[1:-1].replace("\\n", "")
    status = group[-1] if (group := re.findall(r"text-white.+>(.*)<.+\/span", html)) else ""
    return re.compile(r'\s+').sub(" ", status).strip()


async def check_packages(packages_tracks: List[str]) -> dict:
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = (client.get(url.format(track)) for track in packages_tracks)
        reqs = await asyncio.gather(*tasks)

    return {str(req.url).split("q=")[-1]: _get_status_text(req.text) for req in reqs}
