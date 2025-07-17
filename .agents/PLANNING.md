# 🗺️ Planning

This document outlines the architecture, goals, and conventions for the Show Up Crawler project.

## 🚀 Project Goals

The primary goal of this project is to create a web crawler that extracts information about crypto-related events happening in Buenos Aires from various event websites. The initial focus will be on `lu.ma`.

The extracted data should include:
- Event title
- Date and time
- Location
- Description
- Organizer
- Event URL

## 🏗️ Architecture

The project will be built using Python and the Scrapy framework.

- **Crawler**: A Scrapy spider will be developed to crawl `lu.ma` and other target websites.
- **Data Storage**: Initially, the scraped data will be stored in a JSON file. In the future, we might consider a database like PostgreSQL or MongoDB.
- **Configuration**: Project settings and configurations will be managed in `scrapy.cfg` and the Scrapy settings file.

## 🎨 Code Style & Conventions

- **Language**: Python 3.13+ with modern type hints.
- **Package Manager**: `uv` will be used for managing Python dependencies.
- **Testing**: `pytest` will be used for testing.
- **Linting & Formatting**: `ruff` will be used for linting and formatting to ensure code quality.
- **Modularity**: Code will be organized into spiders, items, and pipelines as per Scrapy's conventions.

## ⛓️ Constraints

- Adhere to the rules in `.agents/RULES.md`.
- Do not add any new dependencies without prior discussion and approval.
- All code must be tested.
