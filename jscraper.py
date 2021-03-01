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
        self.daily_doubles = None
        self.clue_values = None
        self.triple_stumpers = None
        self.setup(game_id)

    def setup(self, game_id):
        self.__set_soup(game_id)
        self.__get_clue_ids()
        self.__get_categories()
        self.__get_answers()
        self.__get_questions()
        self.__get_images()
        self.__get_daily_doubles()
        self.__get_clue_values()
        self.__get_triple_stumpers()

    def __set_soup(self, link):
        """ Sets the soup Id"""
        #gid = str(game_id)
        page = requests.get(link)
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
            if tag == "clue_FJ" or tag == "clue_TB":
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
        self.clue_ids = []
        for event_tag in self.soup.findAll(onmouseout=True):
            tag = event_tag['onmouseover'].strip("toggle(").split(",")[0].strip("'")
            self.clue_ids.append(tag)


    def __get_daily_doubles(self):
        self.daily_doubles = []
        for header in self.soup.find_all('table', class_="clue_header"):
            if header.find(class_='clue_value_daily_double') is not None:
                self.daily_doubles.append(header.find(class_='clue_unstuck').get('id').rstrip("_stuck"))

    def __get_clue_values(self):
        self.clue_values = {}

        for header in self.soup.find_all('table', class_="clue_header"):
            clue_id = header.find(class_='clue_unstuck').get('id').rstrip("_stuck")
            if header.find(class_='clue_value_daily_double') is not None:
                value = int(header.find(class_='clue_value_daily_double').get_text().lstrip("DD: $").replace(",", ""))
                self.clue_values[clue_id] = value
            else:
                value = int(header.find(class_='clue_value').get_text().lstrip("$"))
                self.clue_values[clue_id] = value

    def __get_triple_stumpers(self):
        self.triple_stumpers = []
        for event_tag in self.soup.findAll(onmouseout=True):
            tag = event_tag['onmouseover'].strip("toggle(").split(",")[0].strip("'")
            clue_answer = bs(event_tag["onmouseover"], "html.parser")
            if clue_answer.find(class_="wrong") is not None:
                if clue_answer.find(class_="wrong").get_text() == "Triple Stumper":
                    self.triple_stumpers.append(tag)

    @staticmethod
    def get_clue_id(category_idx, clue_idx, mode):
        """ Returns a formatted clue id given the category index(1-6), clue index(1-6), and mode("J","DJ","FJ")"""
        return "_".join(["clue", mode, str(category_idx), str(clue_idx)])

    def get_clue(self, category_idx, clue_idx, mode):
        """Gets the text of a clue given the category index(1-6), clue index(1-6), and mode("J","DJ","FJ")"""
        clue_id = self.get_clue_id(category_idx, clue_idx, mode)
        if mode == "FJ":
            return self.questions["clue_FJ"]
        elif mode == "TB":
            return self.questions["clue_TB"]
        else:
            clue = self.soup.find_all('td', id=clue_id)
            if len(clue) == 0:
                return "Clue not found"
            else:
                return clue[0].get_text()

    def get_clue_by_cid(self, clue_id):
        if self.is_FJ_clue(clue_id):
            return self.get_FJ_clue()
        elif self.is_TB_clue(clue_id):
            return self.get_TB_clue()
        else:
            args = clue_id.split("_")
            return self.get_clue(args[2], args[3], args[1])

    def valid_clue(self, category_idx, clue_idx, mode):
        """Returns whether the given the category index(1-6), clue index(1-6), and mode("J","DJ","FJ") is a clue"""
        clue_id = self.get_clue_id(category_idx, clue_idx, mode)
        clue = self.soup.find_all('td', id=clue_id)
        return len(clue) > 0

    def get_answer(self, category_idx, clue_idx, mode):
        """Returns the answer for the given category index(1-6), clue index(1-6), and mode("J","DJ","FJ") """
        if mode == "FJ":
            return self.answers["clue_FJ"]
        elif mode == "TB":
            return self.answers["clue_TB"]
        else:
            if self.valid_clue(category_idx, clue_idx, mode):
                clue_id = self.get_clue_id(category_idx, clue_idx, mode)
                return self.answers[clue_id]
            else:
                return "Invalid Clue Id"

    def get_answer_by_cid(self, clue_id):
        if self.is_FJ_clue(clue_id):
            return self.get_FJ_answer()
        elif self.is_TB_clue(clue_id):
            return self.get_TB_answer()
        else:
            args = clue_id.split("_")
            return self.get_answer(args[2], args[3], args[1])

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
        game_info = str(self.soup.title.get_text())
        show_info = game_info.strip("J! Archive - Show #").split(", aired ")
        return [int(show_info[0]),show_info[1]]

    def has_image(self, category_idx, clue_idx, mode):
        """ Returns with the clue is associated with an image"""
        clue_id = self.get_clue_id(category_idx, clue_idx, mode)
        return clue_id in self.clue_images

    def has_image_by_cid(self, clue_id):
        return clue_id in self.clue_images

    def get_FJ_clue(self):
        return self.questions["clue_FJ"]

    def get_FJ_answer(self):
        return self.answers["clue_FJ"]

    def get_TB_clue(self):
        return self.questions["clue_TB"]

    def get_TB_answer(self):
        return self.answers["clue_TB"]

    def get_category(self, idx, mode):
        index = int(idx)
        if mode == "FJ":
            return self.categories[12]
        elif mode == "DJ":
            return self.categories[index - 1 + 6]
        elif mode == "TB":
            return self.categories[13]
        else:
            return self.categories[index - 1]

    def get_category_by_cid(self, clue_id):
        category_idx = self.get_category_idx(clue_id)
        mode = self.get_clue_mode(clue_id)
        return self.get_category(category_idx,mode)


    def get_clue_ids(self):
        return self.clue_ids

    def is_daily_double(self, category_idx, clue_idx, mode):
        if mode == "FJ" or mode == "TB":
            return False
        else:
            clue_id = self.get_clue_id(category_idx, clue_idx, mode)
            return clue_id in self.daily_doubles

    def is_daily_double_by_cid(self, clue_id):
        return clue_id in self.daily_doubles

    def get_daily_doubles(self):
        return self.daily_doubles

    def get_category_idx(self, clue_id):
        if self.is_FJ_clue(clue_id) or self.is_TB_clue(clue_id):
            return -1
        else:
            args = clue_id.split("_")
            return int(args[2])

    def get_clue_idx(self, clue_id):
        if self.is_FJ_clue(clue_id) or self.is_TB_clue(clue_id):
            return -1
        else:
            args = clue_id.split("_")
            return int(args[3])

    def get_clue_mode(self, clue_id):
        if self.is_FJ_clue(clue_id):
            return "FJ"
        elif self.is_TB_clue(clue_id):
            return "TB"
        else:
            args = clue_id.split("_")
            return args[1]

    def get_value_by_cid(self, clue_id):
        if self.is_FJ_clue(clue_id) or self.is_TB_clue(clue_id):
            return 0
        else:
            return self.clue_values[clue_id]

    def get_value(self, category_idx, clue_idx, mode):
        if mode == "FJ" or mode == "TB":
            return 0
        else:
            clue_id = self.get_clue_id(category_idx, clue_idx, mode)
            return self.clue_values[clue_id]

    def get_triple_stumpers(self):
        return self.triple_stumpers

    def is_triple_stumper_by_cid(self, clue_id):
        return clue_id in self.triple_stumpers

    def is_FJ_clue(self, clue_id):
        return clue_id.find("FJ") >= 0

    def is_TB_clue(self, clue_id):
        return clue_id.find("TB") >= 0

    def is_triple_stumper(self, category_idx, clue_idx, mode):
        if mode == "FJ":
            return "clue_FJ" in self.triple_stumpers
        elif mode == "TB":
            return "clue_TB" in self.triple_stumpers
        else:
            clue_id = self.get_clue_id(category_idx, clue_idx, mode)
            return clue_id in self.triple_stumpers

    def is_tournament(self):
        return self.soup.find(id="game_comments").get_text().find('final') >= 0

    def get_tournament(self):
        return self.soup.find(id="game_comments").get_text()

