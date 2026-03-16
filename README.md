# Electricity notification :electric_plug:

Monitors a local news site (subotica.com) for electricity shutdown announcements and sends Discord notifications to affected users. Uses Google Gemini AI to match addresses — handling Serbian grammatical cases (padeži) and house number ranges — with a simple string-matching fallback if the AI call fails.

## Setup

### Dependencies

```bash
pip install requests htmldom google-genai
```

### Configuration

Create an **env.json** file:

```json
{
  "discord_webhook": "discord webhook url",
  "search_page_url": "search page of the local website",
  "gemini_api_key": "your Google AI Studio API key",
  "checks": [
    {
      "street": "Street Name",
      "user": "<@UserDiscordId>"
    },
    {
      "street": "Street Name 2",
      "user": "<@UserDiscordId2>",
      "number": "15"
    }
  ]
}
```

- `street` — Street name in Serbian
- `user` — Discord mention string
- `number` — (optional) House number. When present, the AI checks if that number falls within any ranges mentioned in the article. When absent, any mention of the street triggers a notification.

## Usage

```bash
python3 main.py
```

The script runs as a one-shot and is designed for cron scheduling.

### Docker

```bash
docker compose build
docker compose up -d
docker compose exec app python3 main.py
```

## How it works

1. Fetches the latest post from the news site search page
2. If today's date appears in the post title, scrapes the article text
3. Sends the text to Gemini AI along with all configured addresses
4. The AI identifies which addresses are affected, accounting for Serbian grammatical cases and house number ranges
5. Sends Discord notifications to matched users
6. Falls back to simple string matching if the AI call fails