import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import certifi


ARXIV_API_URL = "https://export.arxiv.org/api/query"

ATOM_NAMESPACE = "{http://www.w3.org/2005/Atom}"
ARXIV_NAMESPACE = "{http://arxiv.org/schemas/atom}"


def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """
    Search arXiv for scientific papers and return structured results.

    Args:
        query: The keyword or phrase to search for.
        max_results: Maximum number of papers to retrieve (up to 5).

    Returns:
        A list of dictionaries containing paper metadata.
    """

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    # This project currently limits each search to five papers.
    max_results = max(1, min(max_results, 5))

    # Encode the search parameters safely for the URL.
    parameters = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
    }

    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(parameters)}"

    # Verify HTTPS certificates using certifi.
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ResearchSphere/0.1"},
    )

    with urllib.request.urlopen(
        request,
        context=ssl_context,
        timeout=30,
    ) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    papers = []

    for entry in root.findall(f"{ATOM_NAMESPACE}entry"):
        title_element = entry.find(f"{ATOM_NAMESPACE}title")
        abstract_element = entry.find(f"{ATOM_NAMESPACE}summary")

        title = (
            " ".join(title_element.itertext()).strip()
            if title_element is not None
            else "Untitled"
        )

        abstract = (
            " ".join(abstract_element.itertext()).strip()
            if abstract_element is not None
            else ""
        )

        authors = []

        for author in entry.findall(f"{ATOM_NAMESPACE}author"):
            name_element = author.find(f"{ATOM_NAMESPACE}name")

            if name_element is not None and name_element.text:
                authors.append(name_element.text.strip())

        published_element = entry.find(f"{ATOM_NAMESPACE}published")
        updated_element = entry.find(f"{ATOM_NAMESPACE}updated")
        id_element = entry.find(f"{ATOM_NAMESPACE}id")

        arxiv_id = ""

        if id_element is not None and id_element.text:
            arxiv_id = id_element.text.strip().rsplit("/", 1)[-1]

        pdf_url = ""

        for link in entry.findall(f"{ATOM_NAMESPACE}link"):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break

        abstract_url = (
            id_element.text.strip()
            if id_element is not None and id_element.text
            else ""
        )

        papers.append(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published": (
                    published_element.text.strip()
                    if published_element is not None
                    and published_element.text
                    else ""
                ),
                "updated": (
                    updated_element.text.strip()
                    if updated_element is not None
                    and updated_element.text
                    else ""
                ),
                "abstract_url": abstract_url,
                "pdf_url": pdf_url,
            }
        )

    return papers