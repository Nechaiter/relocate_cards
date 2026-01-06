(function(){
function attemptInjection(){

    if (document.getElementById("addon-options-row")) return false;


        let mainContainer = document.querySelector('[class*="container-columns"]') || 
                           document.querySelector('.container.container-sm') ||
                           document.querySelector('.pre-import-page .container');
        
        if (!mainContainer) {
            
            return false;
        }
        
        // Finds Import Options container to insert a new one below it
        // there is one when importing apgk, txt, cvs so i assume is always present
        // FIX IF ABOVE STATEMENT IS WRONG  
        let importOptionsRow = null;
        let allRows = mainContainer.querySelectorAll('[class*="row"]');
        
        for (let i = 0; i < allRows.length; i++) {
            let h1 = allRows[i].querySelector('h1');
            if (h1 && h1.textContent.trim().match(/Import\s+options/i)) {
                importOptionsRow = allRows[i];
                break;
            }
        }
        
        if (!importOptionsRow) {
            return false;
        }

    let classes = {
            // Header
            row: 'row d-block svelte-hl5xdk',
            container: 'container svelte-dkvlwr light',
            containerStyle: '--gutter-block: 2px; --container-margin: 0;',
            positionRelative: 'position-relative',
            h1: 'svelte-dkvlwr',

            // Body

            // row option
            wrapper: 'svelte-css-wrapper',
            innerRow: 'row svelte-hl5xdk',
            
            col: 'col svelte-1wesuxj col-xs',
            label: 'svelte-og1n8p',
            settingTitle: 'setting-title svelte-11kx1hj',
            configInput: 'config-input position-relative justify-content-end svelte-ldggmw',
            formSwitch: 'form-check form-switch svelte-xmrb6j',
            checkbox: 'form-check-input svelte-xmrb6j'
        };

    let container = importOptionsRow.querySelector('[class*="container"]');
        if (container) {
            classes.container = container.className;
            classes.containerStyle = container.getAttribute('style') || classes.containerStyle;
        }
        
        let row = importOptionsRow.querySelector('[class*="row"]:not([class*="d-block"])');
        if (row) classes.innerRow = row.className;
        
        classes.row = importOptionsRow.className;
        
        let posRel = importOptionsRow.querySelector('[class*="position-relative"]');
        if (posRel) classes.positionRelative = posRel.className;
        
        let h1 = importOptionsRow.querySelector('h1');
        if (h1) classes.h1 = h1.className;
        
        let col = importOptionsRow.querySelector('[class*="col"]');
        if (col) classes.col = col.className;
        
        let label = importOptionsRow.querySelector('label');
        if (label) classes.label = label.className;
        
        let settingTitle = importOptionsRow.querySelector('[class*="setting-title"]');
        if (settingTitle) classes.settingTitle = settingTitle.className;
        
        let configInput = importOptionsRow.querySelector('[class*="config-input"]');
        if (configInput) classes.configInput = configInput.className;
        
        let formSwitch = importOptionsRow.querySelector('[class*="form-switch"]');
        if (formSwitch) classes.formSwitch = formSwitch.className;
        
        let checkbox = importOptionsRow.querySelector('input[type="checkbox"]');
        if (checkbox) classes.checkbox = checkbox.className;

    let addonRowHTML = 
            '<div class="' + classes.row + '" id="addon-options-row">' +
                '<div class="' + classes.container + '" style="' + classes.containerStyle + '">' +
                    '<div class="' + classes.positionRelative + '">' +
                        '<h1 class="' + classes.h1 + '">Relocate Option</h1>' +
                    '</div>' +
                    '<' + classes.wrapper.split(' ')[0] + ' style="display: contents; --cols: 6;">' +
                        '<div class="' + classes.innerRow + '">' +
                            '<' + classes.wrapper.split(' ')[0] + ' style="display: contents; --col-size: 4;">' +
                                '<div class="' + classes.col + '">' +
                                    '<label class="' + classes.label + '" for="relocate_cards_id">' +
                                        '<div class="' + classes.settingTitle + '">Relocate existing cards to imported deck</div>' +
                                    '</label>' +
                                '</div>' +
                            '</' + classes.wrapper.split(' ')[0] + '>' +
                            '<' + classes.wrapper.split(' ')[0] + ' style="display: contents; --col-justify: flex-end;">' +
                                '<div class="' + classes.col + '">' +
                                    '<div class="' + classes.configInput + '">' +
                                        '<div class="' + classes.formSwitch + '">' +
                                            '<input type="checkbox" id="relocate_cards_id" class="' + classes.checkbox + '">' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</' + classes.wrapper.split(' ')[0] + '>' +
                        '</div>' +
                    '</' + classes.wrapper.split(' ')[0] + '>' +
                '</div>' +
            '</div>';

    // Injects the container below the Import Options present in both import dialog (apgk,csv)
    importOptionsRow.insertAdjacentHTML('afterend', addonRowHTML);
    
    const newCheckbox = document.getElementById("relocate_cards_id");
    if (newCheckbox && window.is_relocate_activated !== undefined) {
        newCheckbox.checked = window.is_relocate_activated;
    }
    setTimeout(function() {
            
            if (newCheckbox) {
                newCheckbox.addEventListener('change', function() {
                    pycmd("relocate_cards_toggle:" + this.checked);
                });
            }
        }, 100);
    return true;
};

function AddonContainer() {
    
    attemptInjection();

    const observer = new MutationObserver((mutations) => {
        
        if (!document.getElementById("addon-options-row")) {
            attemptInjection();
        }
    });

    
    observer.observe(document.body, { childList: true, subtree: true });
}

AddonContainer()
})();

