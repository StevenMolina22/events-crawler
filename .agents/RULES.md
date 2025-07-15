# 📜 Rules

This document outlines the rules and guidelines for the Show Up Crawler project.

1.  **Adhere to the `AGENT.md` guide**: All development must follow the instructions in `.agents/AGENT.md`.
2.  **Respect `robots.txt`**: The crawler must respect the `robots.txt` file of the websites it crawls.
3.  **Set a reasonable crawl rate**: Do not overload the servers of the target websites. Implement a download delay and other throttling settings in Scrapy.
4.  **Use a proper User-Agent**: The crawler should identify itself with a clear User-Agent string (e.g., `ShowUpCrawler/1.0`).
5.  **Handle errors gracefully**: The crawler should be resilient to errors and handle them gracefully (e.g., by logging them and continuing).
6.  **Write clean and maintainable code**: Follow the code style and conventions defined in `.agents/PLANNING.md`.
7.  **Keep documentation up-to-date**: Ensure that the `README.md` and `.agents` files are always in sync with the codebase.
