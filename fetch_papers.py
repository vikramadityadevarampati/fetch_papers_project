import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def fetch_pubmed_ids(query: str, max_results: int = 50) -> List[str]:
    """Fetch PubMed IDs based on a query."""
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": max_results}
    response = requests.get(PUBMED_SEARCH_URL, params=params)
    response.raise_for_status()
    return response.json().get("esearchresult", {}).get("idlist", [])

def fetch_paper_details(pubmed_ids: List[str]) -> str:
    """Fetch detailed paper information in XML format."""
    if not pubmed_ids:
        return ""
    params = {"db": "pubmed", "id": ",".join(pubmed_ids), "retmode": "xml"}
    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()
    return response.text

def parse_paper_details(xml_data: str) -> List[Dict]:
    """Parse XML and extract paper details."""
    root = ET.fromstring(xml_data)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        pubmed_id = article.find(".//PMID").text if article.find(".//PMID") else ""
        title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") else ""
        pub_date = article.find(".//PubDate/Year").text if article.find(".//PubDate/Year") else ""

        authors, companies, email = [], [], ""

        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            affiliation = author.find("..//AffiliationInfo/Affiliation")

            if last_name is not None and fore_name is not None:
                author_name = f"{fore_name.text} {last_name.text}"
                authors.append(author_name)

                if affiliation is not None and any(keyword in affiliation.text.lower() for keyword in ["pharma", "biotech", "inc", "ltd", "gmbh"]):
                    companies.append(affiliation.text)

        papers.append({
            "PubmedID": pubmed_id,
            "Title": title,
            "Publication Date": pub_date,
            "Non-academic Author(s)": ", ".join(authors),
            "Company Affiliation(s)": ", ".join(set(companies)),
            "Corresponding Author Email": email
        })

    return papers
