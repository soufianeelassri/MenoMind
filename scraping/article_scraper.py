import os
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

class ArticleScraper:
    def __init__(self, base_url, output_folder="../data/pdfs"):
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

    def get_article_urls(self, start_page=1, max_articles=100):
        article_urls = []
        article_titles = []
        page_number = start_page

        while len(article_urls) < max_articles:
            try:
                self.driver.get(f'{self.base_url}{page_number}')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'dt.search-results-title a'))
                )
                title_elements = self.driver.find_elements(By.CSS_SELECTOR, 'dt.search-results-title a')

                if not title_elements:
                    self.logger.info(f'No articles found on page {page_number}. Stopping...')
                    break

                for title_element in title_elements:
                    if len(article_urls) >= max_articles:
                        break
                    article_urls.append(title_element.get_attribute('href'))
                    article_titles.append(title_element.text)

                page_number += 1

            except Exception as e:
                self.logger.error(f"Error extracting URLs from page {page_number}: {e}")
                break

        return article_urls, article_titles

    def download_pdf(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'downloadPdf'))
            )
            pdf_link = self.driver.find_element(By.ID, 'downloadPdf').get_attribute('href')

            response = requests.get(pdf_link)
            response.raise_for_status()

            if 'application/pdf' not in response.headers.get('Content-Type', ''):
                self.logger.error(f'Invalid PDF file from {url}')
                return None

            return BytesIO(response.content)

        except Exception as e:
            self.logger.error(f'Failed to download PDF from {url}: {e}')
            return None

    def sanitize_filename(self, title):
        return "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:100]

    def save_pdf(self, title, pdf_data):
        try:
            safe_title = self.sanitize_filename(title)
            file_path = os.path.join(self.output_folder, f"{safe_title}.pdf")
            with open(file_path, 'wb') as f:
                f.write(pdf_data.getvalue())
            self.logger.info(f"Saved PDF: {file_path}")
        except Exception as e:
            self.logger.error(f'Failed to save PDF for article {title}: {e}')

    def scrape(self):
        self.logger.info("Starting article scraping...")
        try:
            article_urls, article_titles = self.get_article_urls()
            for url, title in zip(article_urls, article_titles):
                pdf_data = self.download_pdf(url)
                if pdf_data:
                    self.save_pdf(title, pdf_data)
        finally:
            self.driver.quit()
            
if __name__ == "__main__":
    scraper = ArticleScraper('https://journals.plos.org/plosone/search?filterArticleTypes=Research%20Article&filterSections=Title&q=menopause&sortOrder=RELEVANCE&page=')
    scraper.scrape()