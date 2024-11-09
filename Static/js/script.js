// static/js/script.js
document.querySelectorAll('a[download]').forEach(link => {
    link.addEventListener('click', function() {
        alert("Le téléchargement du PDF commencera sous peu !");
    });
});