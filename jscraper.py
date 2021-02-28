import requests
from bs4 import BeautifulSoup as bs


class Scraper:
    def __init__(self, game_id):
        self.soup = None
        self.answers = None
        self.categories = None
        self.questions = None
        self.questions_answers = None
        self.clue_images = None
        self.clue_ids = None
        self.setup(game_id)

    def setup(self, game_id):
        self.__set_soup(game_id)
        self.__get_clue_ids()
        self.__get_categories()
        self.__get_answers()
        self.__get_questions()
        self.__get_images()

    def __set_soup(self, game_id):
        """ Sets the soup Id"""
        gid = str(game_id)
        page = requests.get("https://www.j-archive.com/showgame.php?game_id=" + gid)
        self.soup = bs(page.content, 'html.parser')

    def __get_categories(self):
        """ Gets the categories"""
        self.categories = []

        for category in self.soup.find_all('td', class_="category_name"):
            self.categories.append(category.get_text().title())

    def __get_answers(self):
        self.answers = {}
        """ Gets the answers with the associated clue ids"""
        for event_tag in self.soup.findAll(onmouseout=True):
            tag = event_tag['onmouseover'].strip("toggle(").split(",")[0].strip("'")
            clue_answer = bs(event_tag["onmouseover"], "html.parser")
            if tag == "clue_FJ":
                clue_answer = bs(event_tag["onmouseover"], "html.parser")
                self.answers[tag] = clue_answer.find('em').get_text()
            else:
                self.answers[tag] = clue_answer.find(class_="correct_response").get_text()

    def __get_questions(self):
        """ Gets the questions with associated clue id"""
        self.questions = {}

        for clue_id in self.clue_ids:
            for answer in self.soup.find_all('td', id=clue_id):
                self.questions[clue_id] = answer.get_text()

    def __get_images(self):
        """ Sets the clue images """
        self.clue_images = []
        for x in self.soup.findAll(class_="clue_text"):
            if x.find('a') is not None:
                self.clue_images.append(x.get('id'))

    def __get_clue_ids(self):
        self.clue_ids = [self.get_clue_id(i, j, mode) for mode in ["J", "DJ"] for i in range(1, 7) for j in range(1, 6)]
        self.clue_ids.append("clue_FJ")
        # for mode in ["J","DJ"]:
        #     for i in range(1,7):
        #         for j in range(1,6):
        #             self.clself.get_clue_id(i,j,mode)

    @staticmethod
    def get_clue_id(category_idx, clue_idx, mode):
        """ Returns a formatted clue id given the category index(1-6), clue index(1-6), and mode("J","DJ","FJ")"""
        return "_".join(["clue", mode, str(category_idx), str(clue_idx)])

    def get_clue(self, category_idx, clue_idx, mode):
        """Gets the text of a clue given the category index(1-6), clue index(1-6), and mode("J","DJ","FJ")"""
        clue_id = self.get_clue_id(category_idx, clue_idx, mode)
        if mode == "FJ":
            return self.questions["clue_FJ"]
        else:
            clue = self.soup.find_all('td', id=clue_id)
            if len(clue) == 0:
                return "Clue not found"
            else:
                return clue[0].get_text()


    def get_clue_by_cid(self, clue_id):
        if clue_id.find("FJ") >= 0:
            return self.get_FJ_clue()
        else:
            args = clue_id.split("_")
            return self.get_clue(args[2],args[3],args[1])

    def valid_clue(self, category_idx, clue_idx, mode):
        """Returns whether the given the category index(1-6), clue index(1-6), and mode("J","DJ","FJ") is a clue"""
        clue_id = self.get_clue_id(category_idx, clue_idx, mode)
        clue = self.soup.find_all('td', id=clue_id)
        return len(clue) > 0

    def get_answer(self, category_idx, clue_idx, mode):
        """Returns the answer for the given category index(1-6), clue index(1-6), and mode("J","DJ","FJ") """
        if mode == "FJ":
            return self.answers["clue_FJ"]
        else:
            if self.valid_clue(category_idx, clue_idx, mode):
                clue_id = self.get_clue_id(category_idx, clue_idx, mode)
                return self.answers[clue_id]
            else:
                return "Invalid Clue Id"

    def get_answer_by_cid(self, clue_id):
        if clue_id.find("FJ") >= 0:
            return self.get_FJ_answer()
        else:
            args = clue_id.split("_")
            return self.get_answer(args[2],args[3],args[1])

    def get_regular(self):
        """ Gets a list of the regular (first round) of categories"""
        return self.categories[0:6]

    def get_double(self):
        """ Gets a list of the double jeopardy (second round) of categories """
        return self.categories[7:12]

    def get_final(self):
        """ Gets a list of the final jeopardy category """
        return self.categories[12:13]

    def get_show_info(self):
        """ Gets the gameID and the air date"""
        game_info = str(self.soup.title.str)
        return game_info.strip("J! Archive - Show ").split(", aired ")

    def has_image(self, category_idx, clue_idx, mode):
        """ Returns with the clue is associated with an image"""
        clue_id = self.get_clue_id(category_idx, clue_idx, mode)
        return clue_id in self.clue_images

    def get_FJ_clue(self):
        return self.questions["clue_FJ"]

    def get_FJ_answer(self):
        return self.answers["clue_FJ"]

    def get_category(self, idx, mode):
        if mode == "FJ":
            return self.categories[12]
        elif mode == "DJ":
            return self.categories[idx - 1 + 6]
        else:
            return self.categories[idx - 1]

    def get_clue_ids(self):
        return self.clue_ids

