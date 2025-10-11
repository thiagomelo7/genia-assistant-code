window.onload = function() {
    const fala = document.getElementById('fala-narrador');
    const texto = fala.textContent;
    fala.textContent = '';
    let i = 0;
    function escrever() {
        if (i < texto.length) {
            fala.textContent += texto.charAt(i);
            i++;
            setTimeout(escrever, 25); // velocidade da escrita
        }
    }
    escrever();
};