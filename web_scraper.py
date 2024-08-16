import requests
from bs4 import BeautifulSoup
from typing import Optional, List
from dataclasses import dataclass, asdict
import json
import os

# Define a dataclass to store the article metadata and content
@dataclass
class Article:
    url: str  # The URL of the article
    post_id: Optional[int]  # The post ID of the article, if available
    title: Optional[str]  # The title of the article
    keywords: Optional[List[str]]  # Keywords associated with the article
    thumbnail: Optional[str]  # URL of the article's thumbnail image
    publication_date: Optional[str]  # The publication date of the article
    last_updated_date: Optional[str]  # The last updated date of the article
    author: Optional[str]  # The author of the article
    content: Optional[str]  # The full text content of the article

# Class responsible for parsing the sitemap and extracting article URLs
class SitemapParser:
    def __init__(self, sitemap_index_url: str):
        self.sitemap_index_url = sitemap_index_url  # URL of the sitemap index

    # Method to retrieve URLs of monthly sitemaps from the sitemap index
    def get_monthly_sitemap_urls(self) -> List[str]:
        try:
            response = requests.get(self.sitemap_index_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "xml")
            sitemaps = soup.find_all("loc")  # Find all <loc> tags in the XML
            sitemap_urls = [sitemap.string for sitemap in sitemaps if 'sitemap-' in sitemap.string]  # Filter for monthly sitemaps
            return sitemap_urls
        except Exception as e:
            print(f"Failed to parse sitemaps: {e}")
            return []

    # Method to extract article URLs from a given monthly sitemap URL
    def extract_article_urls(self, monthly_sitemap_url: str) -> List[str]:
        try:
            response = requests.get(monthly_sitemap_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'xml')
            article_urls = [loc.string for loc in soup.find_all('loc')]  # Extract URLs from <loc> tags
            return article_urls
        except Exception as e:
            print(f"Failed to extract article URLs from {monthly_sitemap_url}: {e}")
            return []

# Class responsible for scraping individual articles
class ArticleScraper:
    def __init__(self):
        self.session = requests.Session()  # Use a session for persistent connections

    # Method to scrape an article given its URL
    def scrape_article(self, url: str) -> Optional[Article]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract metadata from the JSON-encoded <script> tag
            metadata_script = soup.find('script', type='application/ld+json')
            metadata = json.loads(metadata_script.string) if metadata_script else {}

            # Create an Article object with the extracted metadata and content
            article = Article(
                url=url,
                post_id=metadata.get('post_id'),
                title=metadata.get('headline'),
                keywords=metadata.get('keywords'),
                thumbnail=metadata.get('image'),
                publication_date=metadata.get('datePublished'),
                last_updated_date=metadata.get('dateModified'),
                author=metadata.get('author', {}).get('name') if metadata.get('author') else None,
                content=' '.join(p.get_text() for p in soup.find_all('p'))  # Combine text from all <p> tags
            )
            return article
        except Exception as e:
            print(f"Failed to scrape article at {url}: {e}")
            return None

# Class for handling file operations, such as saving articles to JSON
class FileUtility:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)  # Create the output directory if it doesn't exist

    # Method to save a list of articles to a JSON file
    def save_to_json(self, articles: List[Article], year: str, month: str):
        filename = f'articles_{year}_{month}.json'  # Create a filename based on year and month
        file_path = os.path.join(self.output_directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(article) for article in articles if article], f, ensure_ascii=False, indent=4)

# Main function to coordinate the scraping process
def main():
    sitemap_index_url = "https://www.almayadeen.net/sitemaps/all.xml"  # URL of the sitemap index

    # Initialize the classes
    sitemap_parser = SitemapParser(sitemap_index_url)
    article_scraper = ArticleScraper()
    file_utility = FileUtility(output_directory='output')

    # Retrieve the monthly sitemaps
    monthly_sitemaps = sitemap_parser.get_monthly_sitemap_urls()

    if not monthly_sitemaps:
        print("No monthly sitemaps found.")
        return

    total_articles_scraped = 0
    limit_articles = 10000  # limited number of articles to scrape

    # Loop through each monthly sitemap
    for monthly_sitemap in monthly_sitemaps:
        if total_articles_scraped >= limit_articles:
            break  # Stop if we have reached the limit

        print(f"Processing sitemap: {monthly_sitemap}")

        # Extract article URLs from the monthly sitemap
        article_urls = sitemap_parser.extract_article_urls(monthly_sitemap)

        articles = []
        for url in article_urls:
            if total_articles_scraped >= limit_articles:
                break  # Stop if we have reached the limit

            article = article_scraper.scrape_article(url)
            if article:
                articles.append(article)
                total_articles_scraped += 1
                print(f"Scraped article: {article.title} (Number of articles scraped: {total_articles_scraped})")

        # Extract year and month from the sitemap URL
        year_month = monthly_sitemap.split('-')[-2:]  # Extract 'YYYY-MM' from the URL
        year = year_month[0]
        month = year_month[1].replace('.xml', '')

        # Save articles to JSON
        file_utility.save_to_json(articles, year, month)

    print(f"Successfull scraping {total_articles_scraped} articles.")

# Entry point of the script
if __name__ == "__main__":
    main()
