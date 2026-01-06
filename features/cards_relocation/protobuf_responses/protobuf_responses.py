
from datetime import datetime
import anki.import_export_pb2 as pb2
from google.protobuf.json_format import MessageToJson
from ....shared.io_utils import write_file
from .... import flags
import logging
logger = logging.getLogger("aqt.mediasrv")

def dump_import_response_to_json(response: pb2.ImportResponse) -> None:
    if flags.FLAGS["PRINT_DEBUG"]:
        logger.debug(f"Dumping protobuf import response")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"logs/import_response_{ts}.json"
    json_text = MessageToJson(
        response,
        preserving_proto_field_name=True,
        indent=2,
        sort_keys=True,
    )
    write_file(out_path,json_text)


