"""
datascrap.py
------------
A unified data scraping class for the VerdictInsightEngine pipeline.

Sources:
  1. UNICEF        – https://www.unicef.org/reports
  2. Ofcom         – Children & Parents: Media Use and Attitudes 2025
  3. Alan Turing   – Research Publications hub

Each source is a method on the single `DataScrap` class so the rest of
the pipeline can call them consistently:

    ds = DataScrap()
    ds.scrape_unicef()
    ds.scrape_ofcom()
    ds.scrape_turing()
"""

import requests
from bs4 import BeautifulSoup


class DataScrap:
    """
    Centralised scraper for the three primary data sources used by the
    VerdictInsightEngine.

    Every method returns a list of dicts so downstream ingest / indexing
    steps receive a predictable structure regardless of source.
    """

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    # Realistic browser headers – avoids 403s from sites that block obvious bots
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    def _get_soup(self, url: str, extra_headers: dict | None = None) -> BeautifulSoup:
        """Fetch *url* and return a BeautifulSoup parse tree."""
        headers = {**self.HEADERS, **(extra_headers or {})}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    # ------------------------------------------------------------------ #
    # 1. UNICEF Reports
    # ------------------------------------------------------------------ #

    def scrape_unicef(self) -> list[dict]:
        """ Scrape UNICEF reports page for PDF download links. """
        BASE_URL = "https://www.unicef.org"
        PAGE_URL = f"{BASE_URL}/reports"

        print(f"[UNICEF] Fetching {PAGE_URL} …")
        soup = self._get_soup(PAGE_URL)

        results = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if ".pdf" in href.lower():
                full_url = href if href.startswith("http") else BASE_URL + href
                title = link.get_text(strip=True) or full_url
                results.append({"source": "unicef", "title": title, "url": full_url})

        print(f"[UNICEF] Found {len(results)} PDF link(s).")
        return results

    # ------------------------------------------------------------------ #
    # 2. Ofcom – Children & Parents: Media Use and Attitudes
    # ------------------------------------------------------------------ #

    def scrape_ofcom(self) -> list[dict]:
        """
        Scrape the Ofcom Children & Parents Media Use and Attitudes report
        page (2025 edition) for downloadable assets (PDFs, XLSX tables,
        methodology documents, questionnaires).

        Key data categories captured from the report:
          - Device ownership (smartphone ownership by age)
          - Platform use (YouTube, TikTok usage rates)
          - Screen time (hours per day)
          - Parental controls & monitoring behaviours
          - Digital literacy / awareness of online risks
        """
        BASE_URL = "https://www.ofcom.org.uk"

        # 2025 landing page – Ofcom keeps a stable slug for the main report
        REPORT_URL = (
            "https://www.ofcom.org.uk/media-use-and-attitudes/media-habits-children"
            "/children-and-parents-media-use-and-attitudes-report-2025"
        )

        print(f"[Ofcom] Fetching {REPORT_URL} …")
        soup = self._get_soup(REPORT_URL)

        ASSET_EXTENSIONS = (".pdf", ".xlsx", ".xls", ".csv", ".docx")
        results = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            lower_href = href.lower()

            if any(lower_href.endswith(ext) for ext in ASSET_EXTENSIONS):
                full_url = href if href.startswith("http") else BASE_URL + href
                title = link.get_text(strip=True) or full_url

                # Determine file type for downstream routing
                if ".pdf" in lower_href:
                    file_type = "pdf"
                elif lower_href.endswith((".xlsx", ".xls", ".csv")):
                    file_type = "xlsx"
                else:
                    file_type = "other"

                results.append({
                    "source": "ofcom",
                    "title": title,
                    "url": full_url,
                    "file_type": file_type,
                })

        # Always include the canonical 2025 download link as a fallback
        CANONICAL = (
            "https://www.ofcom.org.uk/media-use-and-attitudes/media-habits-children"
            "/children-and-parents-media-use-and-attitudes-report-2025"
        )
        if not any(r["url"] == CANONICAL for r in results):
            results.append({
                "source": "ofcom",
                "title": "Children and Parents: Media Use and Attitudes 2025 (main report)",
                "url": CANONICAL,
                "file_type": "pdf",
            })

        print(f"[Ofcom] Found {len(results)} asset(s).")
        return results

    # ------------------------------------------------------------------ #
    # 3. Alan Turing Institute – Research Publications
    # ------------------------------------------------------------------ #

    def scrape_turing(self) -> list[dict]:
        """
        Scrape the Alan Turing Institute publications hub for research
        relevant to the VerdictInsightEngine:

          - Responsible AI  → model evaluation
          - AI governance   → citation verification
          - Trustworthy ML  → hallucination mitigation
          - Data-centric AI → dataset quality
        """
        BASE_URL = "https://www.turing.ac.uk"
        PUBLICATIONS_URL = f"{BASE_URL}/research/publications"

        # Keywords mapped to their engine-use label
        TOPIC_MAP = {
            "responsible ai": "Responsible AI – model evaluation",
            "ai governance": "AI governance – citation verification",
            "trustworthy": "Trustworthy ML – hallucination mitigation",
            "data-centric": "Data-centric AI – dataset quality",
            "data centric": "Data-centric AI – dataset quality",
            "algorithmic": "Responsible AI – model evaluation",
            "fairness": "Responsible AI – model evaluation",
            "transparency": "AI governance – citation verification",
        }

        print(f"[Turing] Fetching {PUBLICATIONS_URL} …")

        # ------------------------------------------------------------
        # Attempt live scrape; fall back gracefully if site blocks us
        # (the Turing site occasionally returns 403 for non-browser UA)
        # ------------------------------------------------------------
        try:
            soup = self._get_soup(PUBLICATIONS_URL)
            live_scrape = True
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            print(f"[Turing] WARNING: HTTP {status} fetching live page – using curated fallback records.")
            live_scrape = False
        except requests.exceptions.RequestException as exc:
            print(f"[Turing] WARNING: Network error ({exc}) – using curated fallback records.")
            live_scrape = False

        if not live_scrape:
            # Curated static records so the pipeline always has Turing data
            fallback = [
                {
                    "source": "turing", "topic": "Responsible AI – model evaluation",
                    "title": "Responsible AI: principles into practice",
                    "url": "https://www.turing.ac.uk/research/research-projects/responsible-ai",
                },
                {
                    "source": "turing", "topic": "AI governance – citation verification",
                    "title": "AI governance and accountability frameworks",
                    "url": "https://www.turing.ac.uk/research/interest-groups/ai-ethics",
                },
                {
                    "source": "turing", "topic": "Trustworthy ML – hallucination mitigation",
                    "title": "Trustworthy and ethical AI",
                    "url": "https://www.turing.ac.uk/research/research-programmes/trustworthy-and-ethical-ai",
                },
                {
                    "source": "turing", "topic": "Data-centric AI – dataset quality",
                    "title": "Data-centric AI and dataset quality",
                    "url": "https://www.turing.ac.uk/research/research-programmes/data-centric-engineering",
                },
            ]
            print(f"[Turing] Using {len(fallback)} curated fallback record(s).")
            return fallback

        results = []
        seen_urls = set()

        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href = link["href"]
            full_url = href if href.startswith("http") else BASE_URL + href

            if not title or full_url in seen_urls:
                continue

            title_lower = title.lower()
            matched_topic = None
            for keyword, label in TOPIC_MAP.items():
                if keyword in title_lower:
                    matched_topic = label
                    break

            if matched_topic:
                results.append({
                    "source": "turing",
                    "title": title,
                    "url": full_url,
                    "topic": matched_topic,
                })
                seen_urls.add(full_url)

        print(f"[Turing] Found {len(results)} relevant publication(s).")
        return results


# ------------------------------------------------------------------ #
# Entry point – run all three scrapers and summarise results
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    ds = DataScrap()

    unicef_data = ds.scrape_unicef()
    ofcom_data  = ds.scrape_ofcom()
    turing_data = ds.scrape_turing()

    print("\n=== Summary ===")
    print(f"  UNICEF   : {len(unicef_data):>4} item(s)")
    print(f"  Ofcom    : {len(ofcom_data):>4} item(s)")
    print(f"  Turing   : {len(turing_data):>4} item(s)")