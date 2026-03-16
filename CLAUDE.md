# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python script that monitors a local news site (subotica.com) for electricity shutdown announcements. When a post from today is found, it scrapes the article, sends the text to Google Gemini AI to check if any configured addresses are affected (accounting for Serbian grammatical cases and house number ranges), and sends Discord notifications to matched users.

## Running

```bash
python3 main.py
```

No build step. No tests. The script runs as a one-shot (designed for cron scheduling).

### Docker

The project includes a Docker setup for containerized execution:

```bash
docker compose build
docker compose up -d
docker compose exec app python3 main.py
```

The `Dockerfile` uses `python:3.12-slim`, installs dependencies, and runs `sleep infinity` to keep the container alive. The `docker-compose.yml` mounts the project directory into `/app/` so code changes are reflected without rebuilding.

## Dependencies

- `requests` — HTTP calls to the news site and Discord webhook
- `htmldom` — HTML parsing (pip package: `htmldom`)
- `google-genai` — Google Gemini AI API client
- Python standard library: `datetime`, `html`, `json`, `re`

Install: `pip install requests htmldom google-genai`

## Architecture

Single-file script (`main.py`) with these functions:

1. **`get_last_post(page_url)`** — Fetches the search page (returns JSON with `html` field), parses it to extract the latest article link and title text.
2. **`strip_html(raw_html)`** — Strips HTML tags and normalizes whitespace from raw HTML content.
3. **`get_article_text(page_url)`** — Loads the article page, extracts text from all `<li>` elements, returns plain text.
4. **`build_addresses_list(checks)`** — Formats check entries into an indexed list for the AI prompt.
5. **`check_with_ai(article_text, checks)`** — Sends a single Gemini API call with the article text and all addresses. The prompt instructs the model to handle Serbian padezi (grammatical cases) and house number ranges. Returns a list of matched indices.
6. **`parse_page_fallback(page_url, checks)`** — Legacy string-matching fallback used when the AI call fails.
7. **`send_notification(person, link_to_check)`** — POSTs a Discord message mentioning the user with a link to the announcement.

The `__main__` block ties it together: only processes the latest post if today's date appears in the post title. Uses AI matching with fallback to simple string matching on error.

## Configuration

`env.json` (gitignored) provides:
- `discord_webhook` — Discord webhook URL
- `search_page_url` — News site search endpoint
- `gemini_api_key` — Google AI Studio API key
- `checks` — Array of `{street, user, number?}` objects:
  - `street` — Street name in Serbian
  - `user` — Discord mention string (e.g. `<@user_id>`)
  - `number` — (optional) House number. When present, AI checks if that specific number falls within any ranges mentioned in the article. When absent, any mention of the street triggers notification.

**`env.json` contains secrets (webhook URL, API key, user IDs) — never commit it.**

## Locale

The monitored news site (subotica.com) and all street names are in Serbian. The AI prompt handles all Serbian grammatical cases (padeži) for street name matching. The fallback uses simple string matching with `html.unescape()`.
