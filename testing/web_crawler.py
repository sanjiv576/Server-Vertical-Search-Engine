import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self, start_url, max_depth=2):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited_urls = set()
        self.base_domain = urlparse(start_url).netloc

    def crawl(self, url, current_depth=0):
        # Stop if we hit max depth or have already visited this link
        if current_depth > self.max_depth or url in self.visited_urls:
            return

        # Stay within the starting website domain to avoid wandering off
        if urlparse(url).netloc != self.base_domain:
            return

        print(f"[{current_depth}] Crawling: {url}")
        self.visited_urls.add(url)

        try:
            # Step 1: Download the page
            response = requests.get(url, headers={"User-Agent": "MyCustomCrawler/1.0"}, timeout=5)
            if response.status_code != 200:
                return

            # Step 2: Parse the content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # (Optional) Extract page data here, like the title
            title = soup.title.string if soup.title else "No Title"
            print(f" -> Found Page Title: {title.strip()}")

            # Step 3: Find and extract all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                # Convert relative links (like /about) to absolute URLs
                absolute_url = urljoin(url, href)
                
                # Recursively crawl the discovered link
                self.crawl(absolute_url, current_depth + 1)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

if __name__ == "__main__":
    # Test the crawler on an open sandbox site
    target_site = "http://quotes.toscrape.com/"
    crawler = WebCrawler(start_url=target_site, max_depth=2)
    crawler.crawl(target_site)
