import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import pandas
import csv
import os


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

# DI generuoti keywords
KEYWORDS = [
    # Programavimo
    "python", "java", "javascript", "c#", "c++", "php", "go", "typescript",
    "ruby", "rust", "scala", "node", "react", "angular", "vue",

    # Duomenų
    "data", "analitikas", "duomenų analitikas", "data analyst", "data engineer",
    "sql", "power bi", "excel", "tableau", "etl", "bi", "dbt", "airflow",

    # DevOps / Cloud
    "devops", "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "terraform",

    # Quality / Security
    "testuotojas", "qa", "automation", "cybersecurity", "pentest", "security",

    # Kitos IT pozicijos
    "sistemų administratorius", "it administratorius", "backend", "frontend",
    "fullstack", "support", "helpdesk", "sysadmin"
]


if __name__ == "__main__":
    all_jobs = [] #pildomas sarasas

    for kw in KEYWORDS:
        print(f"\n--- Ieškomi skelbimai pagal raktinį žodį: {kw} ---")
        jobs = scrape_search_page(keyword=kw, page=1)

        for job in jobs:
            job["keyword"] = kw
            all_jobs.append(job)

    print(f"\nIš viso surinkta skelbimų: {len(all_jobs)}")

    # Parodome pirmus 20
    for j in all_jobs[:20]:
        print(j["keyword"], " | ", j["title"], "->", j["url"])


    with open('CVB_IT.csv', 'w', newline='',encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=['keyword', 'title', 'url'])
        writer.writeheader()
        writer.writerows(all_jobs)

    print(f"Duomenys išsaugoti: {file}.")