from flask import request, Blueprint
import json
from . import main
import os
from app.main import utils
from app.main.email_invoice_extraction import extract_from_email_bodytext

@main.route('/', methods=['GET', 'POST'])
def index():
    return "EMAIL INVOICE API"

@main.route('/upload_bodytext', methods=['POST'])
def upload_pdf_file():
    uploaded_files = request.files
    pdf = uploaded_files['email_bodytext']
    file_extension = ".txt"
    filename = utils.getFileName(utils.getDateTime()) + file_extension
    filepath = os.path.join('static', filename)
    
    pdf.save(filepath)
    res = extract_from_email_bodytext(filepath)
    return json.dumps(res, ensure_ascii=False)