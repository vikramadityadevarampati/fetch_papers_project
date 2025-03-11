import argparse
import csv
from fetch_papers import fetch_pubmed_ids, fetch_paper_details, parse_paper_details

def save_to_csv(papers, filename):
    """Save results to CSV."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"])
        writer.writeheader()
        writer.writerows(papers)

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-f", "--file", type=str, help="Output CSV file name")

    args = parser.parse_args()

    if args.debug:
        print(f"Fetching PubMed papers for query: {args.query}")

    pubmed_ids = fetch_pubmed_ids(args.query)
    xml_data = fetch_paper_details(pubmed_ids)
    papers = parse_paper_details(xml_data)

    if args.file:
        save_to_csv(papers, args.file)
        print(f"Results saved to {args.file}")
    else:
        for paper in papers:
            print(paper)

if __name__ == "__main__":
    main()
