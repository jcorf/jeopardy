import jscraper
import jmongo
import requests
from bs4 import BeautifulSoup as bs
import time

global mongo

def insert_clues(link, season):
    scraper = jscraper.Scraper(link)
    for clue_id in scraper.clue_ids:
        clue_info = {"season": season,
                     "show_id": scraper.get_show_info()[0], "airdate": scraper.get_show_info()[1], "clue_id": clue_id,
                     "type": scraper.get_clue_mode(clue_id), "text": scraper.get_clue_by_cid(clue_id),
                     "response": scraper.get_answer_by_cid(clue_id), "image": scraper.has_image_by_cid(clue_id),
                     "daily_double": scraper.is_daily_double_by_cid(clue_id),
                     "triple_stumper": scraper.is_triple_stumper_by_cid(clue_id),
                     "category": scraper.get_category_by_cid(clue_id)}

        if scraper.is_FJ_clue(clue_id) is False:
            clue_info["clue_value"] = scraper.get_value_by_cid(clue_id)
            clue_info["category_idx"] = scraper.get_category_idx(clue_id)
            clue_info["clue_idx"] = scraper.get_clue_idx(clue_id)

        mongo.insert_clue(clue_info)


def insert_season(s):
    season = str(s)

    page = requests.get("https://j-archive.com/showseason.php?season=" + season)
    soup = bs(page.content, 'html.parser')

    for game in soup.find_all("tr"):
        link = game.find("a").get("href")
        insert_clues(link, s)
        time.sleep(60)  # not to overload; wait 60 seconds per game


def main():
    global mongo
    mongo = jmongo.JMongo("jeopardy", "clues")
    mongo.delete_all()

    for i in range(32, 37):
        insert_season(i)
