import csv
from src.datatypes import Character, Movie, Conversation, Line


def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None


with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    # movies is a dictionary of movie_id to Movie objects
    movies = {
        try_parse(int, row["movie_id"]): Movie(
            try_parse(int, row["movie_id"]),
            row["title"] or None,
            row["year"] or None,
            try_parse(float, row["imdb_rating"]),
            try_parse(int, row["imdb_votes"]),
            row["raw_script_url"] or None,
        )
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    # characters is a dictionary of character_id to Character objects
    characters = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        char = Character(
            try_parse(int, row["character_id"]),
            row["name"] or None,
            try_parse(int, row["movie_id"]),
            row["gender"] or None,
            try_parse(int, row["age"]),
            0,
            [],
            [],
        )
        characters[char.id] = char

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    # conversations is a dictionary of conversation_id to Conversation objects
    conversations = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        conv = Conversation(
            try_parse(int, row["conversation_id"]),
            try_parse(int, row["character1_id"]),
            try_parse(int, row["character2_id"]),
            try_parse(int, row["movie_id"]),
            0,
        )
        conversations[conv.id] = conv
        characters[conv.c1_id].conversations.append(conv.id)
        characters[conv.c2_id].conversations.append(conv.id)

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    # lines is a dictionary of line_id to Line objects
    lines = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        line = Line(
            try_parse(int, row["line_id"]),
            try_parse(int, row["character_id"]),
            try_parse(int, row["movie_id"]),
            try_parse(int, row["conversation_id"]),
            try_parse(int, row["line_sort"]),
            row["line_text"],
        )
        lines[line.id] = line
        # c is a Character object
        c = characters.get(line.c_id)
        if c:
            c.num_lines += 1
            c.lines.append(line.line_text) # keep track of all lines for this character
        # conv is a Conversation object
        conv = conversations.get(line.conv_id)
        if conv:
            conv.num_lines += 1
        
