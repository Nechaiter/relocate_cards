"""
Docstring for features.cards_relocation.new_deck

Reads user new import and relocate old cards, also can generate dumps ifs needed
"""

import tempfile,zipfile,sqlite3, os
# TODO CREAR UN BINARIO DENTRO DEL ADDON SEGUN PLATAFORMA
import zstandard as zstd
import logging 
logger = logging.getLogger("aqt.mediasrv")
from ...shared.io_utils import write_file
import json
#TODO for nechaiter: Entender como zipfile funciona por dentro, os y sqlite
from datetime import datetime
from aqt import mw

from ... import flags 

def dump_sql_tables(cursor,dbname: str):
    """
    Generate a file with all the data from apkg databases.

    I used this method because I was lazy trying to find and understand apgk logic from
    source code. 
    
    :param cursor: Sqlite cursor
    :param dbname: database name version
    """
    data = f"{dbname}"
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    data+= f"\n{tables}\n"
    for table_tuple in tables:
        table_name = table_tuple[0]
        
        
        data += f"\n{'='*40}\n"
        data += f" TABLE: {table_name}\n"
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if cursor.description:
                headers = [description[0] for description in cursor.description]
                data += f"COLUMNS: {headers}\n"
                data += f"ROW COUNT: {len(rows)}\n"
                data += "-"*40 + "\n"

            for row in rows:
                formatted_row = "\n".join(str(item) for item in row)
                data += f"--- ROW ---\n{formatted_row}\n"
        
            data += f"{'='*40}\n"
        
        except Exception as table_e:
            data += f"Error reading {table_name}: {table_e}\n"

    write_file(f"logs/tables{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt",data)


def get_notes_info_from_file(cards_to_move:list,cursor: sqlite3.Cursor,db_name: str) -> dict:
    

    nids = ",".join(str(x.id.nid) for x in cards_to_move)
    
    def get_notes_by_nids() -> None:
        cursor.execute(f"SELECT notes.guid,cards.did FROM cards JOIN notes ON cards.nid = notes.id WHERE notes.id IN ({nids});")
        data = cursor.fetchall()
        for row in data:
            if decks.get(row[1]) is not None:

                # {guid,}
                card_info[row[0]]=decks[row[1]]


    #sqlite3 always return a tuple 
    # https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.fetchone
    card_info = {}
    """Card info after get_notes
    card_info= {guid:deck_name}
    """
    decks = {}
    """Deck after decks loops
    decks= {deck_id=deck_name}
    """



    if db_name == "collection.anki21b":
        cursor.execute("SELECT id,name FROM decks;")
        data=cursor.fetchall()
        for row in data:
            if row[1] == "Default" or not row[1]:
                continue
            decks[row[0]]= row[1].replace('\x1f', '::')
        get_notes_by_nids()
    
    elif db_name == "collection.anki21":
        cursor.execute("SELECT decks FROM col;")
        data=cursor.fetchone()
        data = json.loads(data[0])
        for deck in data.values():
            if deck["name"] == "Default" or not deck["name"]:
                continue
            decks[deck["id"]]= deck["name"] 
        get_notes_by_nids()
    elif db_name == "collection.anki2":
        cursor.execute("SELECT decks FROM col;")
        data=cursor.fetchone()
        data = json.loads(data[0])
        for deck in data.values():
            if deck["name"] == "Default" or not deck["name"]:
                continue
            decks[deck["id"]]= deck["name"]
        get_notes_by_nids()
        
        
    if flags.FLAGS["PRINT_DEBUG"]:
        logger.debug(db_name)
    if flags.FLAGS["SQL_DEBUG"]:
        dump_sql_tables(cursor,db_name)

    return card_info


def rename_old_deck_who_match(cursor: sqlite3.Cursor,db_name: str) -> bool:
    
    deck_name=""

    if db_name == "collection.anki21":
        cursor.execute("SELECT decks FROM col;")
        data=cursor.fetchone()
        data = json.loads(data[0])
        for deck in data.values():
            if deck["name"] == "Default" or not deck["name"]:
                continue
            deck_name=deck["name"]
        
    elif db_name == "collection.anki21b":
        cursor.execute("SELECT id,name FROM decks;")
        data=cursor.fetchall()
        for row in data:
            if row[1] == "Default" or not row[1]:
                continue
            deck_name=row[1].replace('\x1f', '::')

    elif db_name == "collection.anki2":
        cursor.execute("SELECT decks FROM col;")
        data=cursor.fetchone()
        data = json.loads(data[0])
        for deck in data.values():
            if deck["name"] == "Default" or not deck["name"]:
                continue
            deck_name=deck["name"]

        
    if flags.FLAGS["PRINT_DEBUG"]:
        logger.debug(db_name)
    if flags.FLAGS["SQL_DEBUG"]:
        dump_sql_tables(cursor,db_name)

    deck_name = deck_name.split('::')[0]  
    
    if flags.FLAGS["PRINT_DEBUG"]:
        print(f"mw.col is {type(mw.col)}")
        print(deck_name)

    # assert mw.col is not None
    if mw.col is None:
        return False
    
    deck = mw.col.decks.by_name(deck_name)
    
    if flags.FLAGS["PRINT_DEBUG"]:
        print(f"mw.col.decks.by_name(deck_name) is {type(deck)}")

    if deck is None:
        return False
    mw.col.decks.rename(deck["id"],deck_name + " OLD")

    return True

def dump_user_tables(database) -> None:
    assert mw.col is not None
    assert mw.col.db is not None
    data=''
    try:
        data+="Tables\n"
        db_response=mw.col.db.all("SELECT name FROM sqlite_master WHERE type='table';")
        data+=str(db_response)
        data+="\n"
        for table_tuple in db_response:
            table_name = table_tuple[0]
            data += f"\n{'='*40}\n"
            data += f" TABLE: {table_name}\n"
            data+= str(mw.col.db.all(f"PRAGMA table_info({table_name})"))
            data += f"{'='*40}\n"
            
            rows = mw.col.db.all(f"SELECT * FROM {table_name};")

            for row in rows:
                formatted_row = "\n".join(str(item) for item in row)
                data += f"--- ROW ---\n{formatted_row}\n"
            data += f"{'='*40}\n"

        
    
    except Exception as e:
        data+=str(e)
        print(e)

    write_file(f"logs/anki_tables.txt",data)

def move_conflicted_cards(notes_info : dict) -> tuple:
    """
    Does the relocation by iterating by the cards who are duplicated and also updated by anki by the implication that those are the ones
    that already exists in user db and them are also present in the new import file
    """
    assert mw.col is not None
    assert mw.col.db is not None
    if flags.FLAGS["SQL_DEBUG"]:
        dump_user_tables(mw.col.db)
    

    card_moved = 0
    card_not_moved = 0

    for note_guid,note_deck_name  in notes_info.items():

        get_note_sql=f"SELECT guid,id FROM notes WHERE guid='{note_guid}';"
        note = mw.col.db.first(get_note_sql)
        if note is None:
            card_not_moved += 1
            deck_dict_to_move_at=None
            continue
        
        deck_dict_to_move_at= mw.col.decks.by_name(note_deck_name)
        if deck_dict_to_move_at is None:
            card_not_moved += 1
            continue

        target_deck_id = deck_dict_to_move_at['id']
        card = mw.col.find_cards(f"nid:{note[1]}")
        mw.col.set_deck(card,target_deck_id)

        card_moved+=1

    return card_moved,card_not_moved




