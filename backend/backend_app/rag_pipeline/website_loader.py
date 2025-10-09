import requests
from bs4 import BeautifulSoup
import re
import time

def extract_text_from_website(url: str) -> str:
    """
    Fetch a website and extract visible text content using BeautifulSoup.
    Filters out scripts, styles, and irrelevant tags.
    """
    # More realistic headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    max_retries = 3
    timeout = 30  # Increased timeout to 30 seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to fetch {url} (attempt {attempt + 1}/{max_retries})")
            
            # Create session for better connection handling
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove noise
            for tag in soup(["script", "style", "noscript", "header", "footer", "svg", "nav", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n")

            # Normalize whitespace
            text = re.sub(r'\n\s*\n+', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            
            if not text.strip():
                raise ValueError("No text content found on the page")
                
            print(f"Successfully extracted {len(text)} characters from {url}")
            return text.strip()

        except requests.exceptions.Timeout:
            print(f"Timeout error on attempt {attempt + 1} for {url}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retry
                continue
            else:
                raise RuntimeError(f"Failed to extract website text: Request timed out after {max_retries} attempts")
                
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempt {attempt + 1} for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise RuntimeError(f"Failed to extract website text: Connection error - {e}")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise RuntimeError(f"Failed to extract website text: Access denied (403) - The website may be blocking automated requests")
            elif e.response.status_code == 404:
                raise RuntimeError(f"Failed to extract website text: Page not found (404)")
            else:
                raise RuntimeError(f"Failed to extract website text: HTTP {e.response.status_code} - {e}")
                
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1} for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise RuntimeError(f"Failed to extract website text: {e}")
    
    raise RuntimeError(f"Failed to extract website text after {max_retries} attempts")
