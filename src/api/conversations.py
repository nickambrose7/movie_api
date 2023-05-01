from asyncio import sleep
from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlalchemy


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
async def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """
    character_ids = {conversation.character_1_id, conversation.character_2_id}
    if len(character_ids) != 2:
        raise HTTPException(status_code=400, detail="Characters must be different")

    characters_stmt = (
        sqlalchemy.select(db.characters.c.character_id)
        .where((db.characters.c.character_id.in_(character_ids)) & (db.characters.c.movie_id == movie_id))
    )

    with db.engine.connect() as conn:
        characters_result = conn.execute(characters_stmt)
        fetched_character_ids = {row.character_id for row in characters_result}

    if fetched_character_ids != character_ids:
        raise HTTPException(status_code=400, detail="Invalid characters for movie")

    next_conversation_id_stmt = (
        sqlalchemy.select(sqlalchemy.func.max(db.conversations.c.conversation_id) + 1)
    )

    new_conversation_stmt = (
        sqlalchemy.insert(db.conversations)
        .values(
            conversation_id=sqlalchemy.select(next_conversation_id_stmt.scalar_subquery()),
            movie_id=movie_id,
            character1_id=conversation.character_1_id,
            character2_id=conversation.character_2_id,
        )
        .returning(db.conversations.c.conversation_id)
    )

    with db.engine.connect() as conn:
        new_conversation_result = conn.execute(new_conversation_stmt)
        new_conversation_id = new_conversation_result.fetchone().conversation_id

        for idx, line in enumerate(conversation.lines, start=1):
            if line.character_id not in character_ids:
                raise HTTPException(status_code=400, detail="Line does not match conversation characters")

            new_line_id_stmt = (
                sqlalchemy.select(sqlalchemy.func.max(db.lines.c.line_id) + 1)
            )

            new_line_stmt = (
                sqlalchemy.insert(db.lines)
                .values( line_id=sqlalchemy.select(new_line_id_stmt.scalar_subquery()),
                character_id=line.character_id,
                movie_id=movie_id,
                conversation_id=new_conversation_id,
                line_sort=idx,
                line_text=line.line_text)
            )

            # with db.engine.connect() as conn:
            conn.execute(new_line_stmt)

    return {"conversation_id": new_conversation_id}
