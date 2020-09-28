import datetime
import requests
import html
import json
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


def parse_page(page_url, checks):
    dom = htmldom.HtmlDom(page_url).createDom()
    for announcement in dom.find("li"):
        for check in checks:
            if check["street"] in html.unescape(announcement.text()):
                send_notification(check["user"], page_url)


def send_notification(person, link_to_check):
    requests.post(env['discord_webhook'], {
        "content": person + " I think electricity will be shutdown in your street, please check more at: " +
        link_to_check
    })


if __name__ == '__main__':
    today = datetime.datetime.today().day
    last_post = get_last_post(env['search_page_url'])

    if last_post and str(today) + "." in last_post["text"]:
        parse_page(last_post["url"], env['checks'])
