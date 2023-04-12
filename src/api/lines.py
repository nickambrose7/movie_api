from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()
# Reference characters by name not by ID
@router.get("/lines/{character_id}", tags=["lines"]) #tags are used to
# group endpoints
def get_lines(character_id: int):
    """
    This endpoint returns a character and all the lines spoken by that
    character. 
    For each character it returns:
    * `character`: The name of the character.
    * `lines`: A list of lines spoken by the character. 
    The lines are ordered largest to smallest by the number of words in the line. 
    """
    

@router.get("/lines/{character_name}/conversations", tags=["conversations"])
def get_conversations(character_name: str):
    """
    This endpoint returns a character and all the conversations the character
    is in. For each character it returns:
    * `character`: The name of the character.
    * `conversations`: A list of conversations the character is in. 
    The conversations are ordered by the number of lines in the conversation. 
    """
    json = None
    
    return json

@router.get("/lines/{character_name}/longest", tags=["longest"])
def get_longest_lines(character_name: str, 
                      limit: int = 10, 
                      offset: int = 0):
    """
    This endpoint returns a character and the longest lines spoken by that
    character. 
    For each character it returns:
    * `character`: The name of the character.
    * `lines`: A list of the longest lines spoken by the character. 
    The lines are ordered by the number of words in the line. 

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.`
    """
    json = None
    
    return json