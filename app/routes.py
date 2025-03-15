import concurrent.futures
from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_file, session
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from . import login_manager
from .utils import translate_file, extract_text_from_pdf
from .forms import UploadForm
from .models import User, Translation, db
from .languages import supported_languages

bp = Blueprint('main', __name__)
languages = supported_languages

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    translations = Translation.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', translations=translations, in_progress=[t for t in translations if t.status == 'in_progress'])

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)

        translation = Translation(
            user_id=current_user.id,
            file_name=filename,
            file_path=filepath,
            status='in_progress',
            target_language=form.language.data
        )
        db.session.add(translation)
        db.session.commit()

        file_base, file_ext = os.path.splitext(filename)
        translated_filename = f"translated_{file_base}.txt"
        translated_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], translated_filename)

        try:
            if filename.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(filepath)
                text_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{file_base}.txt")

                with open(text_filepath, 'w', encoding='utf-8') as text_file:
                    text_file.write(extracted_text)

                success = translate_file(text_filepath, translated_filepath, translation.target_language)

            else:
                success = translate_file(filepath, translated_filepath, translation.target_language)

            if success:
                translation.translated_file_path = translated_filepath
                translation.status = 'completed'
                flash('Translation completed successfully!', 'success')
            else:
                translation.status = 'error'
                flash('An error occurred during translation.', 'danger')

        except Exception as e:
            translation.status = 'error'
            flash(f'Translation failed: {str(e)}', 'danger')

        db.session.commit()
        return redirect(url_for('main.dashboard'))

    return render_template('upload.html', form=form, languages=languages)

@bp.route('/translation_status/<int:translation_id>')
@login_required
def translation_status(translation_id):
    translation = Translation.query.get_or_404(translation_id)

    if translation.user_id != current_user.id:
        flash('You are not authorized to view this translation.', 'danger')
        return redirect(url_for('main.dashboard'))

    if translation.status == 'in_progress':
        return render_template('translation_status.html', status='in_progress', translation=translation)
    elif translation.status == 'completed':
        return render_template('translation_status.html', status='completed', translation=translation)
    else:
        return render_template('translation_status.html', status='error', translation=translation)

@bp.route('/translations')
@login_required
def translations():
    translations = Translation.query.filter_by(user_id=current_user.id).all()
    return render_template('translations.html', translations=translations)

@bp.route('/process_translation/<int:translation_id>', methods=['POST'])
@login_required
def process_translation(translation_id):
    translation = Translation.query.get_or_404(translation_id)

    if translation.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    input_path = translation.file_path
    output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"translated_{translation.file_name}")

    if translate_file(input_path, output_path, translation.target_language):
        translation.translated_file_path = output_path
        translation.status = 'completed'
        db.session.commit()
        flash('Translation completed successfully!', 'success')
    else:
        translation.status = 'error'
        db.session.commit()
        flash('An error occurred during translation.', 'danger')
    
    return redirect(url_for('main.translation_status', translation_id=translation_id))

@bp.route('/download/<int:translation_id>')
@login_required
def download_translation(translation_id):
    translation = Translation.query.get_or_404(translation_id)

    if translation.user_id != current_user.id:
        flash('You are not authorized to download this file.', 'danger')
        return redirect(url_for('main.dashboard'))

    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    translated_file_path = os.path.abspath(translation.translated_file_path)

    if not translated_file_path.startswith(upload_folder):
        flash('Invalid file path detected.', 'danger')
        return redirect(url_for('main.dashboard'))

    if not os.path.exists(translated_file_path):
        flash('The requested file does not exist.', 'danger')
        return redirect(url_for('main.dashboard'))

    return send_file(translated_file_path, as_attachment=True, download_name=os.path.basename(translated_file_path))

@bp.route('/delete_translation/<int:translation_id>', methods=['POST'])
@login_required
def delete_translation(translation_id):
    translation = Translation.query.get_or_404(translation_id)

    # Check if the translation belongs to the logged-in user
    if translation.user_id != current_user.id:
        flash("You don't have permission to delete this document.", "danger")
        return redirect(url_for('main.dashboard'))

    # Delete the translation from the database
    try:
        db.session.delete(translation)
        db.session.commit()
        flash("Document deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting the document: {e}", "danger")
    
    return redirect(url_for('main.dashboard'))