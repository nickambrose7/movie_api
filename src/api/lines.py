from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
router = APIRouter()

@router.get("/lines/{character_id}", tags=["lines"]) #tags are used to group endpoints
def get_lines(character_id: int):
    """
    This endpoint returns a character and all the lines spoken by that
    character. 
    For each character it returns:
    * `character`: The name of the character.
    * `lines`: A list of lines spoken by the character. 
    The lines are ordered largest to smallest by the number of words in the line.
    
    """

    character_stmt = (
        sqlalchemy.select(db.characters.c.name)
        .where(db.characters.c.character_id == character_id)
        .limit(1)
    )

    with db.engine.connect() as conn:
        character_result = conn.execute(character_stmt)
        character_row = character_result.fetchone()
        if character_row is None:
            raise HTTPException(status_code=404, detail="Character not found")
        character_name = character_row.name

    lines_stmt = (
        sqlalchemy.select(db.lines.c.line_text)
        .where(db.lines.c.character_id == character_id)
        .order_by(sqlalchemy.desc(sqlalchemy.func.length(db.lines.c.line_text)))
    )

    with db.engine.connect() as conn:
        lines_result = conn.execute(lines_stmt)
        lines = [row.line_text for row in lines_result]

    return {"character": character_name, "lines": lines}


@router.get("/lines/{char_id}/conversations", tags=["lines"])
def get_conversations(char_id: int):
    """
    This endpoint returns a character's name and all the conversations the character
    is in. For each character it returns:
    * `character`: The name of the character.
    * `conversations`: A list of conversation_ID's representing the 
    conversations the character is in.
    """
    character_stmt = (
        sqlalchemy.select(db.characters.c.name)
        .where(db.characters.c.character_id == char_id)
        .limit(1)
    )

    with db.engine.connect() as conn:
        character_result = conn.execute(character_stmt)
        character_row = character_result.fetchone()
        if character_row is None:
            raise HTTPException(status_code=404, detail="Character not found")
        character_name = character_row.name

    conversations_stmt = (
        sqlalchemy.select(db.conversations.c.conversation_id)
        .where((db.conversations.c.character1_id == char_id) | (db.conversations.c.character2_id == char_id))
    )

    with db.engine.connect() as conn:
        conversations_result = conn.execute(conversations_stmt)
        conversations = [row.conversation_id for row in conversations_result]

    return {"character": character_name, "conversations": conversations}
    

@router.get("/lines/longest/{char_id}", tags=["lines"])
def get_longest_lines(char_id: int, 
                      limit: int = 10, 
                      offset: int = 0):
    """
    This endpoint returns a character and the longest lines spoken by that
    character. 
    For each character it returns:
    * `character`: The name of the character.
    * `lines`: A list of the longest lines spoken by the character. 
    The lines are ordered by the number of words in the line largest to smallest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.`
    """
    character_stmt = (
        sqlalchemy.select(db.characters.c.name)
        .where(db.characters.c.character_id == char_id)
        .limit(1)
    )

    with db.engine.connect() as conn:
        character_result = conn.execute(character_stmt)
        character_row = character_result.fetchone()
        if character_row is None:
            raise HTTPException(status_code=404, detail="Character not found")
        character_name = character_row.name

    lines_stmt = (
        sqlalchemy.select(db.lines.c.line_text)
        .where(db.lines.c.character_id == char_id)
        .order_by(sqlalchemy.desc(sqlalchemy.func.length(db.lines.c.line_text)))
        .limit(limit)
        .offset(offset)
    )

    with db.engine.connect() as conn:
        lines_result = conn.execute(lines_stmt)
        lines = [row.line_text for row in lines_result]

    return {"character": character_name, "lines": lines}
