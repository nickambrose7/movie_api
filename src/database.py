import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

print(supabase.storage.from_('movie-api').list())

# Reading in the log file from the supabase bucket
verlog_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_log.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_log.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


# END PLACEHOLDER CODE


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
        
