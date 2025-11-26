import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


BASE_URL = "https://www.cvbankas.lt/"


def build_search_url(keyword: str, page: int = 1) -> str:
    params = {
        "keyw": keyword,
        "page": page
    }
    return BASE_URL + "?" + urlencode(params)


def fetch_html(url: str) -> str:

    #grazina puslapio HTML teksta kaip string

    headers = {
# request faking
            "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_job_cards(html: str):
    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    articles = soup.select("article.list_article")
    print("Rasta article.list_article:", len(articles))

    for art in articles:
        title_el = art.select_one("h3.list_h3")
        link_el = art.select_one("a.list_a")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(" ", strip=True)
        href = link_el.get("href")

        if not href:
            continue

        # sutvarkom URL (santykinis ar pilnas)
        if href.startswith("/"):
            url = "https://www.cvbankas.lt" + href
        elif href.startswith("http"):
            url = href
        else:
            url = "https://www.cvbankas.lt/" + href.lstrip("/")

        jobs.append({
            "title": title,
            "url": url
        })

    return jobs


def scrape_search_page(keyword: str, page: int = 1):

    url = build_search_url(keyword, page)
    print("Kreipiuosi į:", url)

    html = fetch_html(url)

    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML išsaugotas į debug.html")

    jobs = parse_job_cards(html)
    print(f"parse_job_cards rado {len(jobs)} skelbimų '{keyword}' (p.{page})")
    return jobs


if __name__ == "__main__":
   #raktazodziai
    jobs = scrape_search_page("analitikas", page=1)

    print("\nPirmi 10 rezultatų:")
    for job in jobs[:10]:
        print(job["title"], "->", job["url"])
