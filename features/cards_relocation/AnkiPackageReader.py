
import tempfile,zipfile,sqlite3, os
import zstandard as zstd
from ... import flags
class AnkiPackageReader:
    def __init__(self, path: str):
        self.path = path
        self.temp_dir = None
        self.conn = None
        self.cursor = None

    def __enter__(self):
        
        self.temp_dir = tempfile.TemporaryDirectory()
        
        
        with zipfile.ZipFile(self.path, "r") as zip_read:
            db_name = None
            
            for candidate in ["collection.anki21b", "collection.anki21", "collection.anki2"]:
                if candidate in zip_read.namelist():
                    db_name = candidate
                    break
            
            if not db_name:
                raise ValueError("No valid database found in apkg")

            zip_read.extract(db_name, self.temp_dir.name)
            db_path = os.path.join(self.temp_dir.name, db_name)

            if flags.FLAGS["PRINT_DEBUG"]:
                print(db_name)


            if db_name == "collection.anki21b":
                decompressed_path = db_path + ".decompressed"
                with open(db_path, "rb") as compressed_file:
                    dctx = zstd.ZstdDecompressor()
                    with open(decompressed_path, "wb") as decompressed_file:
                        dctx.copy_stream(compressed_file, decompressed_file)
                db_path = decompressed_path


            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            

            return self.cursor,db_name

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        if self.conn:
            self.conn.close()
        if self.temp_dir:
            self.temp_dir.cleanup()