import os
import logging
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid

from config import SOURCE_PDF_DIR

class ArticleScraper:
    def __init__(self, base_url, output_folder=SOURCE_PDF_DIR):
        self.base_url = base_url
        self.driver = self.initialize_driver()
        self.output_folder = output_folder 
        self.logger = self.setup_logger()

        os.makedirs(self.output_folder, exist_ok=True)

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger()

    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver

    def get_article_urls(self, start_page=1, max_articles=2):
        article_urls = []
        article_titles = []
        page_number = start_page

        self.logger.info(f"Starting URL scraping from page {start_page}...")

        while len(article_urls) < max_articles:
            current_url = f'{self.base_url}{page_number}'
            self.logger.info(f"Scraping page: {current_url}")
            try:
                self.driver.get(current_url)
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'dt.search-results-title a'))
                )
                title_elements = self.driver.find_elements(By.CSS_SELECTOR, 'dt.search-results-title a')

                if not title_elements:
                    self.logger.info(f'No articles found on page {page_number}. Stopping.')
                    break

                for title_element in title_elements:
                    if len(article_urls) >= max_articles:
                        break
                    href = title_element.get_attribute('href')
                    title = title_element.text.strip()
                    if href and title:
                        article_urls.append(href)
                        article_titles.append(title)
                        self.logger.debug(f"Found article: {title} ({href})")
                    else:
                         self.logger.warning(f"Skipping element with missing href or title on page {page_number}")


                page_number += 1

            except Exception as e:
                self.logger.error(f"Error extracting URLs from page {page_number} ({current_url}): {e}")
                break
        self.logger.info(f"Finished URL scraping. Found {len(article_urls)} articles.")
        return article_urls, article_titles

    def download_pdf(self, url):
        self.logger.info(f"Attempting to download PDF from {url}")
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, 'downloadPdf'))
            )
            pdf_link_element = self.driver.find_element(By.ID, 'downloadPdf')
            pdf_link = pdf_link_element.get_attribute('href')

            if not pdf_link:
                 self.logger.error(f"Could not find PDF download link on page {url}")
                 return None

            response = requests.get(pdf_link, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' not in content_type:
                self.logger.error(f'Invalid Content-Type "{content_type}" from {pdf_link}. Expected application/pdf.')
                return None

            pdf_data = BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                pdf_data.write(chunk)
            pdf_data.seek(0)

            self.logger.info(f"Successfully downloaded PDF from {url}")
            return pdf_data

        except requests.exceptions.RequestException as req_e:
            self.logger.error(f'Request error downloading PDF from {url}: {req_e}')
            return None
        except Exception as e:
            self.logger.error(f'Failed to download PDF from {url}: {e}')
            return None

    def sanitize_filename(self, title):
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title).strip()
        safe_title = safe_title.replace(" ", "_")
        safe_title = safe_title[:100].rstrip('_')
        if not safe_title:
             return "downloaded_article" + str(uuid.uuid4())[:8]
        return safe_title


    def save_pdf(self, title, pdf_data):
        if pdf_data is None:
            self.logger.warning(f"No PDF data to save for article: {title}")
            return

        try:
            safe_title = self.sanitize_filename(title)
            file_path = os.path.join(self.output_folder, f"{safe_title}.pdf")

            counter = 1
            original_file_path = file_path
            while os.path.exists(file_path):
                 file_path = f"{original_file_path.rsplit('.', 1)[0]}_{counter}.pdf"
                 counter += 1


            with open(file_path, 'wb') as f:
                f.write(pdf_data.getvalue())
            self.logger.info(f"Saved PDF: {file_path}")
        except Exception as e:
            self.logger.error(f'Failed to save PDF for article {title}: {e}')

    def scrape(self):
        self.logger.info(f"Starting article scraping into folder: {self.output_folder}")
        try:
            article_urls, article_titles = self.get_article_urls()
            self.logger.info(f"Attempting to download {len(article_urls)} PDFs.")
            for i, (url, title) in enumerate(zip(article_urls, article_titles)):
                 self.logger.info(f"Processing article {i+1}/{len(article_urls)}: {title}")
                 pdf_data = self.download_pdf(url)
                 if pdf_data:
                     self.save_pdf(title, pdf_data)
                 else:
                     self.logger.warning(f"Skipping save for article {title} due to failed download.")
        except Exception as e:
             self.logger.critical(f"An error occurred during scraping: {e}")
        finally:
            self.driver.quit()
            self.logger.info("Scraping finished. Browser closed.")

if __name__ == "__main__":
    scraper = ArticleScraper(
        base_url='https://journals.plos.org/plosone/search?filterArticleTypes=Research%20Article&filterSections=Title&q=menopause&sortOrder=RELEVANCE&page=',
        output_folder=SOURCE_PDF_DIR
        )
    scraper.scrape()