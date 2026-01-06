"""
Este archivo modifica el import dialog
"""

from aqt.import_export.import_dialog import ImportDialog,CsvArgs,AnkiPackageArgs
from aqt import mw
from ... import flags
from ...shared import io_utils
    

JS_INJECTION = io_utils.load_file_to_string('general_container.js') 
JS_AFTER_RELOCATE = io_utils.load_file_to_string('result_screen.js')
JS_DOM_DUMP= io_utils.load_file_to_string("extract_dom.js")
# Save method reference, setup_ui basically generate the dialog view
original_setup_ui = ImportDialog._setup_ui




def mp_import_dialog_setup(self: ImportDialog) -> None:
    """
    Injects a new secction in import dialog interface
    """

    def mp_anki_webview_onBridgeCmd(cmd:str) -> None:
        """
        Captures addon flag and write it, if cmd is not a custom flag, does normal behavior.
        PythonQt implements the bridge method between the js string to python
        
        :param cmd: key_function
        :type cmd: str
        """
        assert self.web is not None 
        orginal_onBridgeCmd = self.web.onBridgeCmd
        if cmd.startswith("relocate_cards_toggle:"):
            if cmd.split(":")[1] == "true":
                mw.addonManager.writeConfig(__name__, {'is_relocate_activated': True})
            else:
                mw.addonManager.writeConfig(__name__, {'is_relocate_activated': False})
        elif cmd.startswith("DUMP_HTML:"):
            content = cmd[len("DUMP_HTML:"):]
            io_utils.write_file("Doms/test.html", content)
        else:
            orginal_onBridgeCmd(cmd)
    
    original_setup_ui(self)

    assert self.web is not None 

    """
    sets custom behav, it needs instance contexts "self" # aqt/webview 828-834
    by default the onBridgeCmd from AnkiWebView is a place holder and its sets initial behavior
    with this method using the instance context and the arguments in the classes of the import file type
    """
    self.web.set_bridge_command(mp_anki_webview_onBridgeCmd, self)
    
    if flags.FLAGS["ENABLE_DOM_DEBUG"]:
        
        self.web.eval(JS_DOM_DUMP)

    config_js_bool="false"
    config = mw.addonManager.getConfig(__name__)
    if config is not None:
        is_relocate_activated=config['is_relocate_activated']
        if is_relocate_activated:
            config_js_bool="true"
        else:
            config_js_bool="false"


    self.web.eval(f'(function(){{window.is_relocate_activated = {config_js_bool}}})();')

    if self.args.kind == CsvArgs.kind:
        pass

    self.web.eval(JS_INJECTION)
    
    self.web.eval(JS_AFTER_RELOCATE)


# Change method def by my custom one, it exec his orginal logic and some extra 
ImportDialog._setup_ui = mp_import_dialog_setup