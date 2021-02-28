import jscraper
import jmongo

scraper = jscraper.Scraper(6376)
#mongo = jmongo.JMongo("jeopardy", "clues")



for clue_id in scraper.clue_ids:

    print(clue_id)
    print(scraper.get_clue_by_cid(clue_id))
    print(scraper.get_answer_by_cid(clue_id))


