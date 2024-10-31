# Textual Documentation Scraper

A Python tool to scrape and consolidate the Textual TUI framework's reference documentation into a single, well-organized markdown file.

## Features

- Downloads all reference documentation from textual.textualize.io
- Creates a single consolidated markdown document
- Includes auto-generated table of contents
- Preserves section hierarchy and formatting
- Handles code blocks, tables, and lists
- Creates clickable navigation anchors

## Installation

1. Clone this repository:
```bash
git clone https://github.com/SnypeAI/TextualDocumentationScraper
cd TextualDocumentationScraper
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python app.py
```

This will:
1. Create a `reference_docs` directory
2. Download and process all reference documentation
3. Generate a single `textual_reference.md` file

## Output Structure

The generated documentation will include:
- YAML frontmatter with title and date
- Auto-generated table of contents
- Hierarchical sections matching the original documentation
- Clean formatting and section breaks
- Internal navigation links

Example structure:
```markdown
---
title: Textual Reference Documentation
date: 2024-03-26
---

# Textual Reference Documentation

## Table of Contents
- [CSS Types](#css-types)
  - [Border](#border)
  - [Color](#color)
...
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
