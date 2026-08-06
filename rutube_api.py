from dataclasses import dataclass
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


@dataclass(frozen=True)
class Episode:
    title: str
    url: str

def get_tv_show_series(show_id: str, season: int):
    url = f"https://rutube.ru/metainfo/tv/{show_id}/season{season}/"
    episodes: list[Episode] = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        items = page.locator(".wdp-grid-module__item")
        for i in range(items.count()):
            link = items.nth(i).locator(
                ".wdp-link-module__link.wdp-card-description-module__titleV2"
            )
            title = link.inner_text()
            full_url = urljoin(url, link.get_attribute("href"))
            episodes.append(Episode(title=title, url=full_url))
        browser.close()

    return episodes
