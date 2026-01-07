
from ...features.cards_relocation.protobuf_responses.protobuf_responses import *
from ...features.cards_relocation.cards_algo import *
from ... import flags 

import anki.import_export_pb2 as pb2
from anki._backend import RustBackend
import logging 
logger = logging.getLogger("aqt.mediasrv")

from aqt import mw
from aqt.import_export.import_dialog import ImportDialog
from ...features.cards_relocation.AnkiPackageReader import AnkiPackageReader

def force_injection_into_active_dialog(count):
    injected = False
    
    for widget in mw.app.topLevelWidgets():
        
        if isinstance(widget, ImportDialog):
            try:
                
                if hasattr(widget, "web") and widget.web:
                    js = f"""
                    (function() {{
                        window.relocateCount = {count};
                    }})();
                    """
                    
                    widget.web.eval(js)
                    injected = True
            except Exception as e:
                if flags.FLAGS["PRINT_DEBUG"]:
                    print(f"{e}")
    if not injected:
        if flags.FLAGS["PRINT_DEBUG"]:
            print("Not injected")
# Save original method behavior to exec it normally
original_import_raw = RustBackend.import_anki_package_raw




def mp_import_anki_package_raw(self, message):
    """
    This patch intervenes the normal bytes return doing extra stuff, then returns normally
    :param backend_instance: Description
    :param bytes_data: Description
    """


    config = mw.addonManager.getConfig(__name__)

    
    is_relocate_activated = config.get('is_relocate_activated', False) if config else False


    did_rename_occur = False
    tempfile,cursor,bdname=None,None,""
    if is_relocate_activated:
        new_file_path = pb2.ImportAnkiPackageRequest.FromString(message).package_path
        path=new_file_path
        if not path.endswith(".apkg"):
            return original_import_raw(self, message)
        tempfile=AnkiPackageReader(path)
        try:
            cursor,bdname=tempfile.__enter__()
        except Exception as e:
            if flags.FLAGS["PRINT_DEBUG"]:
                print(f"Error trying to open apgk file: {e}")
            return original_import_raw(self, message)
        did_rename_occur = rename_old_deck_who_match(cursor,bdname)
        if flags.FLAGS["PRINT_DEBUG"]:
            print(f"did_rename_occur: {did_rename_occur}")
        
    # Save the binary response from the original method
    normal_behavior_bytes  = original_import_raw(self, message)

    # binary parser to string
    response= pb2.ImportResponse.FromString(normal_behavior_bytes)
    
    
    if flags.FLAGS["ANKI_RESPONSE"]:
        dump_import_response_to_json(response)

    if is_relocate_activated and did_rename_occur:
        #Response tags cards inside of the file giving their nid, not in the anki bd
        if response.HasField("log"):
            cards_to_move = (
                list(response.log.conflicting) + 
                list(response.log.updated) + 
                list(response.log.duplicate)
            )


            # cards_to_move = (
            #     list(response.log.conflicting) + 
            #     list(response.log.updated) + 
            #     list(response.log.duplicate) + 
            #     list(response.log.first_field_match)
            # )


            assert cursor,bdname is not None
            notes_info=get_notes_info_from_file(cards_to_move,cursor,bdname)


            cards_moved,cards_not_moved=move_conflicted_cards(notes_info)
            mw.taskman.run_on_main(
                lambda: force_injection_into_active_dialog(cards_moved)
            )



    if is_relocate_activated:
        assert tempfile is not None
        tempfile.__exit__()
    

    # After execute modded code on the orginal method, we return the original binary value to prevent issues with the return value to
    # any caller of the method 
    return normal_behavior_bytes


RustBackend.import_anki_package_raw = mp_import_anki_package_raw


