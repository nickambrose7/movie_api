from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()
# Reference characters by name not by ID
@router.get("/lines/{character_id}", tags=["lines"]) #tags are used to group endpoints
def get_lines(character_id: int):
    """
    This endpoint returns a character and all the lines spoken by that
    character. 
    For each character it returns:
    * `character`: The name of the character.
    * `lines`: A list of lines spoken by the character. 
    The lines are ordered largest to smallest by the number of words in the line.
    
    The URL to test this endpoint is http://0.0.0.0:3001/lines/1 
    """
    character = db.characters.get(character_id)
    if character:
        lines = db.characters.get(character_id).lines
        # Sort lines by number of words
        lines.sort(key=lambda line: len(line.split()), reverse=True)
        json = {
            "character": character.name,
            "lines": lines
        }   
        return json
   
    raise HTTPException(status_code=404, detail="Character not found")


@router.get("/lines/{char_id}/conversations", tags=["conversations"])
def get_conversations(char_id: int):
    """
    This endpoint returns a character's name and all the conversations the character
    is in. For each character it returns:
    * `character`: The name of the character.
    * `conversations`: A list of conversation_ID's representing the 
    conversations the character is in.
    """
    character = db.characters.get(char_id)
    if character:
        conversations = db.characters.get(char_id).conversations
        json = {
            "character": character.name,
            "conversations": conversations
        }
        return json
   
    raise HTTPException(status_code=404, detail="Character not found")
    

@router.get("/lines/longest/{char_id}", tags=["longest"])
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
    character = db.characters.get(char_id)
    if character:
        lines = db.characters.get(char_id).lines
        # Sort lines by number of words
        lines.sort(key=lambda line: len(line.split()), reverse=True)
        json = {
            "character": character.name,
            "lines": lines[offset:offset+limit]
        }   
        return json
    raise HTTPException(status_code=404, detail="Character not found")
