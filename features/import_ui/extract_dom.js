(function() {
    
    function captureAndSendDOM() {
        console.log("Iniciando captura del DOM...");
        
        // Clonar el HTML completo
        var clonedDoc = document.documentElement.cloneNode(true);
        
        // Crear un contenedor para los estilos inline
        var styleBlock = document.createElement('style');
        styleBlock.setAttribute('id', 'captured-styles');
        var allStyles = '';
        
        // Capturar todos los estilos de las hojas CSS cargadas
        try {
            for (var i = 0; i < document.styleSheets.length; i++) {
                var sheet = document.styleSheets[i];
                try {
                    if (sheet.cssRules || sheet.rules) {
                        var rules = sheet.cssRules || sheet.rules;
                        for (var j = 0; j < rules.length; j++) {
                            allStyles += rules[j].cssText + '\\n';
                        }
                    }
                } catch (e) {
                    console.log('No se pudo acceder a stylesheet (CORS):', sheet.href,e);
                }
            }
        } catch (e) {
            console.error('Error capturando estilos:', e);
        }
        
        styleBlock.textContent = allStyles;
        
        // Insertar el bloque de estilos en el head del clon
        var clonedHead = clonedDoc.querySelector('head');
        if (clonedHead) {
            var links = clonedHead.querySelectorAll('link[rel="stylesheet"], link[rel="preload"][as="style"]');
            links.forEach(function(link) {
                link.parentNode.removeChild(link);
            });
            clonedHead.insertBefore(styleBlock, clonedHead.firstChild);
        }
        
        // Remover scripts externos
        var scripts = clonedDoc.querySelectorAll('script[src]');
        scripts.forEach(function(script) {
            var comment = document.createComment('Script removed: ' + script.src);
            script.parentNode.replaceChild(comment, script);
        });
        
        // Serializar y enviar
        var htmlContent = clonedDoc.outerHTML;
        pycmd("DUMP_HTML:" + htmlContent);
    }

    // Variable para controlar que no se ejecute mil veces por segundo
    let debounceTimer;

    function triggerCapture() {
        // Si se llama de nuevo antes de que pasen 500ms, cancelamos el anterior
        clearTimeout(debounceTimer);
        
        // Programamos la ejecución para dentro de 500ms
        debounceTimer = setTimeout(function() {
            captureAndSendDOM();
        }, 500); 
    }

    // Configuramos qué queremos vigilar, pero NO lo encendemos todavía
    const observer = new MutationObserver(function(mutations) {
        // Ante cualquier cambio, intentamos capturar (respetando el debounce)
        triggerCapture();
    });

    setTimeout(function() {
        // A. Ejecutamos la lógica por primera vez inmediatamente
        captureAndSendDOM();

        // B. Encendemos el vigilante para futuros cambios
        // 'subtree: true' es importante para detectar cambios profundos en Svelte
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true
        });
        
        console.log("Observer activado: Esperando actualizaciones del DOM...");

    }, 3000); // Espera inicial de 3 segundos
})();