import aspose.words as aw
from deep_translator import GoogleTranslator
from pdf2image import convert_from_path
import pytesseract
from langdetect import detect
from .languages import LANGUAGE_FONT_MAP
from langdetect.lang_detect_exception import LangDetectException

def translate_file(input_path, output_path, target_language):
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            content = file.read()

        max_chunk_size = 4000
        translated_content = []

        for i in range(0, len(content), max_chunk_size):
            chunk = content[i:i + max_chunk_size]
            try:
                translated_chunk = GoogleTranslator(target=target_language).translate(chunk)
                translated_content.append(translated_chunk)
            except Exception as e:
                print(f"Error translating chunk: {e}")
                translated_content.append(f"[Translation failed for this section]\n{chunk}\n")
        
        output_path = output_path if output_path.endswith('.txt') else f"{output_path}.txt"
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(''.join(translated_content))
        
        return True
    except Exception as e:
        print(f"Translation error: {e}")
        return False
    
def extract_text_from_pdf(pdf_path):
    text = ""
    """try:
        # Try extracting text using Aspose.Words
        doc = aw.Document(pdf_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction with Aspose.Words error: {e}")"""

    try:
        pages = convert_from_path(pdf_path, dpi=300)
        
        for page in pages:
            text += pytesseract.image_to_string(page)
        
        try:
            detected_language = detect(text[:1000])
            print(f"Detected language: {detected_language}")
        except LangDetectException as e:
            detected_language = 'eng'
            print(f"Language detection failed: {e}")
        
        if detected_language and detected_language in pytesseract.get_languages(config=''):
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page, lang=detected_language)
        
        return text
    except Exception as e:
        print(f"OCR error: {e}")
        return ""

