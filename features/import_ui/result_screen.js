(function() {

    
    window.relocateCount = window.relocateCount || 0; 
    const RELOCATE_ID = "addon-relocate-counter";

    function injectCounter() {

        if (document.getElementById(RELOCATE_ID)) return;


        const headers = Array.from(document.querySelectorAll('h1'));
        const overviewHeader = headers.find(h => h.textContent.trim() === 'Overview');

        if (!overviewHeader) return; 

        const container = overviewHeader.closest('[class*="container"]');
        if (!container) return;

        const list = container.querySelector('ul');
        if (!list) return;

        const li = document.createElement('li');
        li.id = RELOCATE_ID;
        
        if (list.firstElementChild) {
            li.className = list.firstElementChild.className;
        }

        li.innerHTML = `
            <span class="svelte-qivuyu" style="--width-multiplier: 1; --icon-size: 100%;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                   <path d="M16 17.01V10h-2v7.01h-3L15 22l4-4.99h-3zM9 3L5 8h3v7.01h2V8h3L9 3z"></path>
                </svg>
            </span>
            <strong>${window.relocateCount}</strong> cards relocated to destination deck.
        `;

        list.appendChild(li);
    }

    injectCounter();

    const observer = new MutationObserver((mutations) => {
        if (!document.getElementById(RELOCATE_ID)) {
            injectCounter();
        }
    });

    
    observer.observe(document.body, {
        childList: true,  
        subtree: true     
    });

})();