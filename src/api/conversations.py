from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime


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
def add_conversation(movie_id: int, conversation: ConversationJson):
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

    # TODO: Remove the following two lines. This is just a placeholder to show
    # how you could implement persistent storage.
    #placeholder code:
    # print(conversation)
    # db.logs.append({"post_call_time": datetime.now(), "movie_id_added_to": movie_id})
    # db.upload_new_log()

    #My code:
    # ensure that all characters are part of the referenced movie:
    if not db.characters[conversation.character_1_id].movie_id == movie_id:
        raise HTTPException(status_code=403, detail="Character 1 not in movie")
    if not db.characters[conversation.character_2_id].movie_id == movie_id:
        raise HTTPException(status_code=403, detail="Character 2 not in movie")
    # ensure that the characters are not the same:
    if conversation.character_1_id == conversation.character_2_id:
        raise HTTPException(status_code=403, detail="Characters are the same")
    # ensure that the lines of a conversation match the characters involved in the conversation:
    for line in conversation.lines:
        if line.character_id != conversation.character_1_id and line.character_id != conversation.character_2_id:
            raise HTTPException(status_code=403, detail="Line does not match characters")
    # create and add conversation:
    db.last_convo_id += 1
    convo = {"conversation_id": db.last_convo_id, "character1_id": conversation.character_1_id, "character2_id": conversation.character_2_id, "movie_id": movie_id}
    db.add_new_convo(convo)
    
    #create and add lines:
    

