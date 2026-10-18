
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import ssl
import certifi
from pathlib import Path
import sys

BASE_URL = "https://export.arxiv.org/api/query"
RESULTS_FILE = Path("research_results.txt")

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom"
}

def clean_text(element, tag):
    """Return readable text from an Atom XML element."""
    node = element.find(f"atom:{tag}", NAMESPACES)

    if node is None or node.text is None:
        return ""

    return " ".join(node.text.split())

def parse_papers(xml_data):
    """Extract genuine paper metadata from the Atom XML response."""
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall("atom:entry", NAMESPACES):
        title = clean_text(entry, "title")
        abstract = clean_text(entry, "summary")
        abstract_url = clean_text(entry, "id")
        published = clean_text(entry, "published")
        updated = clean_text(entry, "updated")

        authors = []
        for author in entry.findall("atom:author", NAMESPACES):
            name = clean_text(author, "name")
            if name:
                authors.append(name)

        pdf_url = ""
        for link in entry.findall("atom:link", NAMESPACES):
            href = link.get("href", "")
            link_title = link.get("title", "").lower()
            link_type = link.get("type", "").lower()

            if link_title == "pdf" or link_type == "application/pdf":
                pdf_url = href
                break

        # The API normally supplies a PDF link. If it doesn't,
        # keep the result usable via its abstract page.
        if not pdf_url and abstract_url:
            pdf_url = abstract_url.replace("/abs/", "/pdf/", 1)

        papers.append({
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "abstract_url": abstract_url,
            "pdf_url": pdf_url,
            "published": published,
            "updated": updated,
        })

    return papers

def search_arxiv(topic, max_results=5):
    """Search arXiv and return the most recently updated matches."""
    topic = topic.strip().replace('"', "")

    if not topic:
        raise ValueError("Research topic cannot be empty.")

    if not 1 <= max_results <= 5:
        raise ValueError("The number of results must be between 1 and 5.")

    params = {
        "search_query": f'all:"{topic}"',
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
    }

    url = BASE_URL + "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ResearchSphere/0.1 (student research project)"
        },
    )

    try:
        ssl_context = ssl.create_default_context(
        cafile=certifi.where()
        )

        with urllib.request.urlopen(
           request,
           timeout=25,
           context=ssl_context
        ) as response:
            xml_data = response.read()

        return parse_papers(xml_data)

    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"arXiv returned HTTP {exc.code}: {exc.reason}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not connect to arXiv: {exc.reason}"
        ) from exc

    except ET.ParseError as exc:
        raise RuntimeError(
            "The response from arXiv was not valid XML."
        ) from exc

def save_bibliography(papers):
    """Save paper metadata and abstracts for offline reference."""
    lines = []

    for index, paper in enumerate(papers, start=1):
        authors = ", ".join(paper["authors"]) or "Authors unavailable"

        lines.extend([
            f"{index}. {paper['title']}",
            f"Authors: {authors}",
            f"Published: {paper['published'] or 'Unavailable'}",
            f"Last updated: {paper['updated'] or 'Unavailable'}",
            f"Abstract page: {paper['abstract_url']}",
            f"PDF: {paper['pdf_url']}",
            f"Abstract: {paper['abstract']}",
            "-" * 70,
            "",
        ])

    RESULTS_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

def main():
    print("=" * 60)
    print("       RESEARCHSPHERE - SCIENTIFIC PAPER SEARCHER")
    print("=" * 60)

    topic = input("Enter a research topic: ").strip()

    try:
        papers = search_arxiv(topic)

        if not papers:
            print("\nNo papers were found for this query.")
            RESULTS_FILE.write_text(
                "No papers found for this search.\n",
                encoding="utf-8"
            )
            return

        print(f"\nFound {len(papers)} paper(s).\n")

        for index, paper in enumerate(papers, start=1):
            authors = ", ".join(paper["authors"]) or "Unavailable"

            print(f"{index}. TITLE: {paper['title']}")
            print(f"   AUTHORS: {authors}")
            print(f"   UPDATED: {paper['updated'] or 'Unavailable'}")
            print(f"   ABSTRACT: {paper['abstract']}")
            print(f"   PDF: {paper['pdf_url']}")
            print(f"   ARXIV: {paper['abstract_url']}")
            print("-" * 60)

        save_bibliography(papers)
        print(f"\nSaved results to: {RESULTS_FILE.resolve()}")

    except (ValueError, RuntimeError) as exc:
        print(f"\nSearch failed: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()