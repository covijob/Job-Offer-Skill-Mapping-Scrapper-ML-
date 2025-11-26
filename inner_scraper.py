import time
import csv
import json
import requests
from bs4 import BeautifulSoup

input_csv = r"C:\Users\mangi\PycharmProjects\Job-Offer-Skill-Mapping-Scrapper-ML-\CVB_IT_tvarkyta.csv"
output_jsonl = r"C:\Users\mangi\PycharmProjects\Job-Offer-Skill-Mapping-Scrapper-ML-\CVB_IT_full.jsonl"


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


# istraukia pag. teksta
def parse_description(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    blocks = soup.select(".jobad_txt")

    if blocks:
        text = " ".join(b.get_text(" ", strip=True) for b in blocks)
        return text

    body = soup.find("body")
    return body.get_text(" ", strip=True) if body else ""


def load_rows_from_csv(path: str):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    rows = load_rows_from_csv(input_csv)
    total = len(rows)
    print(f"Įkelta {total} eilučių iš {input_csv}")

    written = 0

    with open(output_jsonl, "w", encoding="utf-8-sig") as out_f: # *(2)
        for i,row in enumerate(rows, start=1):
            url = row.get("url", "").strip()

#bandoma nuskaityti puslapi, jeigu nepavyksta ismetama klaida ir skaitoma kaip blank
            try:
                html = fetch_html(url)
                desc = parse_description(html) # *(1)
            except Exception as e:
                print(f"[{i}/{total}] KLAIDA ({url}): {e}")
                desc = ""
#padaroma kopija
            doc = dict(row)
            doc["description"] = desc # *(1)

            out_f.write(json.dumps(doc, ensure_ascii=False) + "\n") # *(2)
            written += 1

            print(
                f"[{i}/{total}] OK | title='{row.get('title', '')[:40]}...' "
                f"| desc_len={len(desc)}"
            )

            time.sleep(0.12)  # kad nespaustum per greitai serverio

    print(f"\nBaigta. Parašyta {written} JSONL eilučių į:\n{output_jsonl}")

if __name__ == "__main__":
    main()
    #te