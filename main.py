import datetime
import requests
import html
import json
import re
from htmldom import htmldom

with open("env.json") as file:
    env = json.load(file)


def get_last_post(page_url):
    response = requests.get(page_url)

    if response.status_code == 200:
        response_html = response.json()['html']
        if response_html:
            dom = htmldom.HtmlDom().createDom(response_html)
            post = dom.find("a.articles__title").first()
            return {
                'url': post.attr('href'),
                'text': post.text()
            }
        return None
    return None


def strip_html(raw_html):
    text = html.unescape(raw_html)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_article_text(page_url):
    dom = htmldom.HtmlDom(page_url).createDom()
    content_parts = []
    for li in dom.find("li"):
        content_parts.append(strip_html(li.html()))
    return "\n".join(content_parts)


def build_addresses_list(checks):
    addresses = []
    for i, check in enumerate(checks):
        addr = f"{i}: {check['street']}"
        if "number" in check and check["number"]:
            addr += f" {check['number']}"
        addresses.append(addr)
    return "\n".join(addresses)


def check_with_ai(article_text, checks):
    from google import genai

    client = genai.Client(api_key=env["gemini_api_key"])

    addresses_list = build_addresses_list(checks)

    prompt = f"""You are analyzing a Serbian electricity shutdown announcement. Your task is to determine which of the listed addresses are affected by the power outage described in the article.

IMPORTANT RULES:
1. Street names in the article may appear in ANY Serbian grammatical case (padež): nominativ, genitiv, dativ, akuzativ, vokativ, instrumental, or lokativ. You must match the street name regardless of the grammatical case used. For example, "Mitra Bakića" and "Mitru Bakića" and "Mitre Bakića" all refer to the same street. Use the root/stem of the words to match.
2. If an address includes a house number, check if that specific number is affected. The article may specify:
   - Exact numbers (e.g., "broj 5") — match only that number
   - Ranges (e.g., "1-8" or "od 1 do 8") — match only numbers within that range (inclusive)
   - Odd/even specifications (e.g., "neparni brojevi 1-9") — match accordingly
   - If the article mentions the street but does NOT specify any house numbers, consider ALL numbers on that street as affected
3. If an address has no house number listed, any mention of that street means it's affected.

Here is the article text:
---
{article_text}
---

Here are the addresses to check (format: "index: street_name [house_number]"):
---
{addresses_list}
---

Respond ONLY with a valid JSON array of the indices (as integers) of addresses that ARE affected. For example: [0, 2, 5]
If none are affected, respond with: []
Do not include any other text, explanation, or markdown formatting — just the JSON array."""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    response_text = response.text.strip()
    # Clean potential markdown code block wrapping
    if response_text.startswith("```"):
        response_text = re.sub(r'^```\w*\n?', '', response_text)
        response_text = re.sub(r'\n?```$', '', response_text)
        response_text = response_text.strip()

    matched_indices = json.loads(response_text)
    return matched_indices


def parse_page_fallback(page_url, checks):
    dom = htmldom.HtmlDom(page_url).createDom()
    for announcement in dom.find("li"):
        for check in checks:
            if check["street"] in html.unescape(announcement.text()):
                send_notification(check["user"], page_url, method="fallback")


def send_notification(person, link_to_check, method="ai"):
    if method == "ai":
        tag = "**Match type:** :robot: _AI Match_"
    else:
        tag = "**Match type:** :mag: _Fallback Match_"

    message = (
        f"**:zap: Electricity Shutdown Alert**\n"
        f"{person} Your street may be affected by a planned power outage!\n\n"
        f"**Details:** {link_to_check}\n"
        f"{tag}"
    )

    requests.post(env['discord_webhook'], json={"content": message})


if __name__ == '__main__':
    today = datetime.datetime.today().day
    last_post = get_last_post(env['search_page_url'])

    if last_post and str(today) + "." in last_post["text"]:
        checks = env['checks']
        page_url = last_post["url"]

        try:
            article_text = get_article_text(page_url)
            matched_indices = check_with_ai(article_text, checks)

            for idx in matched_indices:
                if 0 <= idx < len(checks):
                    send_notification(checks[idx]["user"], page_url)
            print(f"AI check completed. Matched indices: {matched_indices}")
        except Exception as e:
            print(f"AI check failed ({type(e).__name__}: {e}), falling back to simple parsing.")
            parse_page_fallback(page_url, checks)
