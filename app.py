from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'secret_key'  # Clé secrète pour les messages flash

# Permet seulement les types de fichiers suivants
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Vérification du type de fichier
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Données simulées
series = [
    {'id': 1, 'nom': 'Terminale Science Exacte(T.SE)'},
    {'id': 2, 'nom': 'Terminale Science Expérimentale(T.SEXP)'},
    {'id': 3, 'nom': 'Terminale Science Sociale(T.SS)'},
    {'id': 4, 'nom': 'Terminale Lettre et Littérature(T.LL)'},
    {'id': 5, 'nom': 'Terminale Science Économique(T.SECO)'},
    {'id': 6, 'nom': 'Terminale Art et Littérature(T.AL)'}
]


cours = []
cours_universite = []  # Liste distincte pour les cours de l'université

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html', series=series)

# Détails d'une série
@app.route('/serie/<int:serie_id>')
def serie_detail(serie_id):
    serie = next((s for s in series if s['id'] == serie_id), None)
    cours_filtrés = [c for c in cours if c['serie_id'] == serie_id]
    return render_template('serie_detail.html', serie=serie, cours=cours_filtrés)

# Page dédiée à l'université
@app.route('/universite')
def universite():
    return render_template('universite.html', cours=cours_universite)

# Formulaire pour ajouter un cours
@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter_cours():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        type_page = request.form['type_page']  # Série ou université

        # Vérification des fichiers téléchargés
        photo = request.files['photo']
        pdf = request.files['pdf']
        
        if photo and allowed_file(photo.filename) and pdf and allowed_file(pdf.filename):
            # Sécurisation des noms de fichiers
            photo_filename = secure_filename(photo.filename)
            pdf_filename = secure_filename(pdf.filename)
            
            # Sauvegarde des fichiers
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))

            # Ajout du cours à la série ou à l'université
            if type_page == 'universite':
                cours_universite.append({
                    'id': len(cours_universite) + 1,
                    'titre': titre,
                    'description': description,
                    'photo': photo_filename,
                    'pdf': pdf_filename
                })
            else:
                serie_id = int(request.form['serie'])
                cours.append({
                    'id': len(cours) + 1,
                    'titre': titre,
                    'description': description,
                    'serie_id': serie_id,
                    'photo': photo_filename,
                    'pdf': pdf_filename
                })
            
            flash('Cours ajouté avec succès!')
            return redirect(url_for('accueil'))
        else:
            flash('Format de fichier non supporté!')

    return render_template('ajouter_cours.html', series=series)

# Téléchargement des fichiers PDF
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/supprimer/<int:cours_id>', methods=['POST'])
def supprimer_cours(cours_id):
    # Rechercher l'article dans les cours de la série
    cours_a_supprimer = next((c for c in cours if c['id'] == cours_id), None)
    
    # Si l'article n'est pas dans les séries, le chercher dans les cours de l'université
    if not cours_a_supprimer:
        cours_a_supprimer = next((c for c in cours_universite if c['id'] == cours_id), None)
        cours_liste = cours_universite  # Identifier la bonne liste

    else:
        cours_liste = cours  # Identifier la bonne liste (séries ou université)
    
    if cours_a_supprimer:
        # Supprimer les fichiers associés (image et PDF)
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cours_a_supprimer['pdf']))
            os.remove(os.path.join('static/images', cours_a_supprimer['photo']))
        except Exception as e:
            print(f"Erreur lors de la suppression des fichiers : {e}")

        # Supprimer l'article de la bonne liste (séries ou université)
        cours_liste.remove(cours_a_supprimer)
        
        flash('Cours supprimé avec succès.')
    else:
        flash('Cours introuvable.')

    return redirect(url_for('accueil'))

@app.route('/recherche')
def rechercher():
    query = request.args.get('query')  # Récupérer la requête de recherche
    if query:
        # Filtrer les cours dont le titre ou la description contient le mot-clé recherché
        resultats = [c for c in cours if query.lower() in c['titre'].lower() or query.lower() in c['description'].lower()]

        # Si des résultats sont trouvés, les afficher, sinon afficher un message d'erreur
        if resultats:
            return render_template('recherche.html', query=query, resultats=resultats)
        else:
            flash(f"Aucun résultat trouvé pour '{query}'")
            return redirect(url_for('accueil'))
    else:
        flash("Veuillez entrer un terme de recherche.")
        return redirect(url_for('accueil'))




if __name__ == '__main__':
    app.run(debug=True)


