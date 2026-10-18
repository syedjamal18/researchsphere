# ResearchSphere

Scientific Paper Searcher via the arXiv API.

## Project goal

Build a research discovery application that retrieves genuine scientific papers from arXiv, displays paper metadata and abstracts, links to PDFs, and exports bibliography information.

## Planned technology stack

* Python and the arXiv API
* `urllib.request`, `urllib.parse`, and `xml.etree.ElementTree`
* FastAPI backend
* React, TypeScript, and Tailwind CSS frontend
* SQLite for optional saved-paper persistence
* Git and GitHub for collaboration

## Current milestone

Implement and verify a command-line paper search that retrieves up to five results, sorts by last-updated date, formats authors and exports the results to `research_results.txt`.

## Running the initial prototype

Requires a supported Python 3 installation and internet access.

```powershell
python src/paper_search.py
```

The application will request a research topic, query arXiv, display paper metadata, and save the results locally.

## Team workflow

* Work on separate feature branches.
* Commit small, meaningful changes.
* Open pull requests for review.
* Keep `main` in a working state.
* Never commit credentials or API secrets.

## Data source

arXiv API documentation: https://info.arxiv.org/help/api/index.html
