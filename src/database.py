import csv
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

#print(supabase.storage.from_('movie-api').list())

# # Reading in the log file from the supabase bucket
# log_csv = (
#     supabase.storage.from_("movie-api")
#     .download("movie_conversations_log.csv")
#     .decode("utf-8")
# )

# logs = []
# for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
#     logs.append(row)


# # Writing to the log file and uploading to the supabase bucket
# # I want to write "this is a test" to the log file"
# def upload_new_log():
#     output = io.StringIO() 
#     #output.write("this is a test")
#     csv_writer = csv.DictWriter(
#         output, fieldnames=["post_call_time", "movie_id_added_to"]
#     )
#     csv_writer.writeheader()
#     csv_writer.writerows(logs)
#     supabase.storage.from_("movie-api").upload(
#         "movie_conversations_log.csv",
#         bytes(output.getvalue(), "utf-8"),
#         {"x-upsert": "true"},
#     )


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


# Reading in the conversations and lines from the supabase bucket
    convo_csv = (
        supabase.storage.from_("movie-api")
        .download("conversations.csv")
        .decode("utf-8")
    )
    conversations = {} # conversations is a dictionary of conversation_id to Conversation objects
    for row in csv.DictReader(io.StringIO(convo_csv), skipinitialspace=True):
        # row is a dictionary of column name to value
        #print(row)
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
    last_convo_id = conv.id
    print(conversations[83076])
   

    lines_csv = (
        supabase.storage.from_("movie-api")
        .download("lines.csv")
        .decode("utf-8")
    )
    lines = {} # lines is a dictionary of line_id to Line objects
    for row in csv.DictReader(io.StringIO(lines_csv), skipinitialspace=True):
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
    last_line_id = line.id
    print(lines[666226])
def add_new_convo(convo):
    #add to supabase
    conversations_csv = (
    supabase.storage.from_("movie-api")
    .download("conversations.csv")
    .decode("utf-8")
    )
    conversations_list = list(csv.DictReader(conversations_csv.splitlines(), skipinitialspace=True))
    conversations_list.append(convo)
    output_csv = io.StringIO(conversations_csv)
    fieldnames = ["conversation_id", "character1_id", "character2_id", "movie_id"]
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(conversations_list)
    supabase.storage.from_("movie-api").upload(
        "conversations.csv",
        bytes(output_csv.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )
    # add to in-memory conversations
    conversations[convo["conversation_id"]] = Conversation(
        convo["conversation_id"],
        convo["character1_id"],
        convo["character2_id"],
        convo["movie_id"],
        0,
    )

def add_new_lines(new_lines):
    #add to supabase
    lines_csv = (
    supabase.storage.from_("movie-api")
    .download("lines.csv")
    .decode("utf-8")
    )
    lines_list = list(csv.DictReader(lines_csv.splitlines(), skipinitialspace=True))
    lines_list = lines_list + new_lines
    output_csv = io.StringIO(lines_csv)
    fieldnames = ["line_id", "character_id", "movie_id", "conversation_id", "line_sort", "line_text"]
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(lines_list)
    supabase.storage.from_("movie-api").upload(
        "lines.csv",
        bytes(output_csv.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )
    # add to in-memory lines
    for line in new_lines:
        lines[line["line_id"]] = Line(
            line["line_id"],
            line["character_id"],
            line["movie_id"],
            line["conversation_id"],
            line["line_sort"],
            line["line_text"],
        )