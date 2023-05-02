from fastapi import APIRouter, HTTPException
from enum import Enum
from fastapi.params import Query
from src import database as db
import sqlalchemy

router = APIRouter()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    character_stmt = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name,
            db.movies.c.title.label("movie"),
            db.characters.c.gender,
        )
        .select_from(db.characters.join(db.movies)) 
        .where(db.characters.c.character_id == id)
        .limit(1)
    )

    with db.engine.connect() as conn:
        character_result = conn.execute(character_stmt)
        character_row = character_result.fetchone()
        if character_row is None:
            raise HTTPException(status_code=404, detail="Character not found")
        character = {
            "character_id": character_row.character_id,
            "character": character_row.name,
            "movie": character_row.movie,
            "gender": character_row.gender,
        }

    # get top conversations
    top_conversations_stmt = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name.label("character"),
            db.characters.c.gender,
            sqlalchemy.func.count(db.lines.c.line_id).label("number_of_lines_together"),
        )
        .select_from(
            db.lines.join(db.conversations)
            .join(db.characters, db.characters.c.character_id == db.conversations.c.character2_id)
        )
        .where(
            (db.lines.c.character_id == id) &
            ((db.conversations.c.character1_id == id) | (db.conversations.c.character2_id == id))
        )
        .group_by(db.characters.c.character_id)
        .order_by(sqlalchemy.desc("number_of_lines_together"))
    )

    with db.engine.connect() as conn:
        top_conversations_result = conn.execute(top_conversations_stmt)
        top_conversations = []
        for row in top_conversations_result:
            top_conversations.append(
                {
                    "character_id": row.character_id,
                    "character": row.character,
                    "gender": row.gender,
                    "number_of_lines_together": row.number_of_lines_together,
                }
            )

    character["top_conversations"] = top_conversations

    return character



class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    sort_column_mapping = {
        "character": db.characters.c.name,
        "movie": db.movies.c.title,
        "number_of_lines": sqlalchemy.func.count(db.lines.c.line_text)
    }


    characters_stmt = (
        sqlalchemy.select(
        db.characters.c.character_id,
        db.characters.c.name.label("character"),
        db.movies.c.title.label("movie"),
        sqlalchemy.func.count(db.lines.c.line_text.distinct()).label("number_of_lines"),
        )
        .select_from(
            db.characters.join(db.movies)
            .join(db.lines, db.lines.c.character_id == db.characters.c.character_id, isouter=True)
        )
        .where(db.characters.c.name.ilike(f"%{name}%"))
        .group_by(db.characters.c.character_id, db.movies.c.title)
    )

    if sort == character_sort_options.number_of_lines:
        characters_stmt = characters_stmt.order_by(sqlalchemy.desc("number_of_lines"))
    elif sort == character_sort_options.character:
        characters_stmt = characters_stmt.order_by(db.characters.c.name)
    elif sort == character_sort_options.movie:
        characters_stmt = characters_stmt.order_by(db.movies.c.title)
    characters_stmt = characters_stmt.limit(limit).offset(offset)

    with db.engine.connect() as conn:
        character_result = conn.execute(characters_stmt)
        characters = []
        for row in character_result:
            characters.append(
                {
                    "character_id": row.character_id,
                    "character": row.character,
                    "movie": row.movie,
                    "number_of_lines": row.number_of_lines,
                }
            )

    return characters
