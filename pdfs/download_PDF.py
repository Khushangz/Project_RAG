import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_pdf_from_url(pdf_url, filename):
    """
    Attempt to download a PDF from the given URL.
    If the response is HTML, use BeautifulSoup to search for a link containing "PDF".
    Otherwise, assume it's the PDF content and save it directly.
    """
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL {pdf_url}: {e}")
        return

    content_type = response.headers.get("Content-Type", "").lower()
    
    # If the URL returns HTML, parse it for a PDF link.
    if "text/html" in content_type:
        print(f"URL returned HTML; parsing page for PDF link: {pdf_url}")
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for an <a> tag with text containing "pdf" (case-insensitive)
        pdf_link_tag = soup.find("a", string=lambda t: t and "pdf" in t.lower())
        if pdf_link_tag and pdf_link_tag.get("href"):
            # Construct an absolute URL in case the link is relative.
            pdf_link = urljoin(pdf_url, pdf_link_tag.get("href"))
            print(f"Found PDF link in page: {pdf_link}")
            try:
                pdf_response = requests.get(pdf_link)
                pdf_response.raise_for_status()
                with open(filename, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"Downloaded PDF from parsed link: {filename}")
            except Exception as e:
                print(f"Error downloading PDF from parsed link {pdf_link}: {e}")
        else:
            print("Could not find a PDF link in the HTML page. Skipping download.")
    else:
        # Otherwise, assume the URL returns PDF content.
        try:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded PDF directly: {filename}")
        except Exception as e:
            print(f"Error saving PDF from {pdf_url}: {e}")

def main():
    # Load metadata from JSON file (which includes PDF URLs)
    metadata_file = "metadata.json"
    if not os.path.exists(metadata_file):
        print(f"Metadata file {metadata_file} not found!")
        return

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    # Create a directory to store the downloaded PDFs
    os.makedirs("pdfs_bs", exist_ok=True)
    
    # Loop over each record in the metadata and download the PDF
    for record in metadata_list:
        pdf_url = record.get("pdf_url")
        if not pdf_url:
            print("No pdf_url found in record; skipping.")
            continue
        
        paper_id = record.get("paper_id", "unknown")
        filename = os.path.join("pdfs_bs", f"{paper_id}.pdf")
        print(f"Downloading PDF for paper: {paper_id} from URL: {pdf_url}")
        download_pdf_from_url(pdf_url, filename)

if __name__ == "__main__":
    main()
