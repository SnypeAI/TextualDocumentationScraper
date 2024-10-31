import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict
from datetime import datetime

class TextualDocScraper:
    def __init__(self, base_url="https://textual.textualize.io"):
        self.base_url = base_url
        self.session = requests.Session()
        self.section_tree = defaultdict(list)  # Stores the document hierarchy

    def get_page(self, url):
        """Fetch a page and return its BeautifulSoup object."""
        response = self.session.get(url)
        return BeautifulSoup(response.text, 'html.parser')

    def clean_markdown(self, text):
        """Clean up markdown text."""
        # Remove multiple blank lines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove trailing whitespace
        text = re.sub(r' +$', '', text, flags=re.MULTILINE)
        return text.strip()

    def extract_content(self, soup, include_title=True):
        """Extract main content from the page."""
        content = []
        
        # Get the main article content
        article = soup.find('article', class_='md-content__inner')
        if not article:
            return None

        # Store the original heading level to adjust subsection levels
        base_heading_level = 2 if include_title else 1
        
        # Process each element
        for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre', 'ul', 'ol', 'table']):
            if element.name.startswith('h'):
                level = int(element.name[1]) + (base_heading_level - 1)
                header_text = element.get_text().strip()
                # Remove any trailing "¶" symbols often used in documentation
                header_text = re.sub(r'\s*¶\s*$', '', header_text)
                content.append(f"{'#' * level} {header_text}\n")
            
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    content.append(f"{text}\n")
            
            elif element.name == 'pre':
                code = element.get_text().strip()
                if code:
                    content.append(f"```python\n{code}\n```\n")
            
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    text = li.get_text().strip()
                    content.append(f"- {text}\n")
            
            elif element.name == 'table':
                # Process table headers
                headers = []
                for th in element.find_all('th'):
                    headers.append(th.get_text().strip())
                
                if headers:
                    content.append('| ' + ' | '.join(headers) + ' |')
                    content.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                
                # Process table rows
                for tr in element.find_all('tr')[1:]:  # Skip header row
                    row = []
                    for td in tr.find_all('td'):
                        row.append(td.get_text().strip())
                    if row:  # Only add non-empty rows
                        content.append('| ' + ' | '.join(row) + ' |')
                content.append('')

        return self.clean_markdown('\n'.join(content))

    def create_toc(self, sections):
        """Create a table of contents from the section tree."""
        toc = ["# Textual Reference Documentation\n"]
        toc.append("## Table of Contents\n")
        
        for section, pages in sections.items():
            # Add section header
            toc.append(f"- [{section}](#{self.make_anchor(section)})")
            # Add pages under section
            for page_title in pages:
                toc.append(f"  - [{page_title}](#{self.make_anchor(page_title)})")
        
        return '\n'.join(toc) + "\n\n---\n\n"

    def make_anchor(self, text):
        """Convert text to a markdown anchor."""
        return re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))

    def scrape_reference_section(self):
        """Scrape all reference documentation and combine into one document."""
        print("Starting documentation scrape...")
        
        # Start with the main reference page
        soup = self.get_page(f"{self.base_url}/reference/")
        
        # Find all reference section links
        nav = soup.find('nav', class_='md-nav--primary')
        reference_pages = defaultdict(list)
        
        if nav:
            # Find the Reference section
            for section in nav.find_all('li', class_='md-nav__item'):
                section_text = section.get_text().strip()
                if 'Reference' in section_text:
                    # Process each subsection
                    for subsection in section.find_all('li', class_='md-nav__item--nested'):
                        subsection_title = subsection.find('a', class_='md-nav__link').get_text().strip()
                        
                        # Get all pages in this subsection
                        for link in subsection.find_all('a', class_='md-nav__link'):
                            href = link.get('href')
                            if href and not href.startswith('#'):
                                page_title = link.get_text().strip()
                                full_url = urljoin(self.base_url, href)
                                reference_pages[subsection_title].append((page_title, full_url))

        # Create the combined document
        combined_content = []
        
        # Add document header
        combined_content.append("---")
        combined_content.append("title: Textual Reference Documentation")
        combined_content.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
        combined_content.append("---\n")

        # Build section tree for TOC
        for section, pages in reference_pages.items():
            self.section_tree[section] = [title for title, _ in pages]

        # Add table of contents
        combined_content.append(self.create_toc(self.section_tree))

        # Process each section and its pages
        for section, pages in reference_pages.items():
            # Add section header
            combined_content.append(f"# {section}\n")
            
            # Process each page in the section
            for page_title, url in pages:
                print(f"Processing: {page_title}")
                try:
                    soup = self.get_page(url)
                    content = self.extract_content(soup)
                    
                    if content:
                        combined_content.append(f"## {page_title}\n")
                        combined_content.append(content)
                        combined_content.append("\n---\n")
                except Exception as e:
                    print(f"Error processing {url}: {e}")

        # Save the combined document
        combined_text = '\n'.join(combined_content)
        os.makedirs('reference_docs', exist_ok=True)
        output_file = os.path.join('reference_docs', 'textual_reference.md')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        print(f"\nComplete! Documentation saved to {output_file}")

def main():
    scraper = TextualDocScraper()
    scraper.scrape_reference_section()

if __name__ == "__main__":
    main()
