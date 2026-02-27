"""Content ingestion blueprint – upload text, URL, or PDF and chunk into knowledge segments."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .database import db
from .models import Content, ContentChunk
import re, os

bp = Blueprint("content", __name__, url_prefix="/content")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _chunk_text(text: str, max_sentences: int = 5) -> list[str]:
    """Split text into chunks of roughly `max_sentences` sentences each."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i + max_sentences]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def _extract_text_from_url(url: str) -> str:
    """Fetch a URL and extract visible text using BeautifulSoup."""
    import requests as _req
    from bs4 import BeautifulSoup
    resp = _req.get(url, timeout=15, headers={"User-Agent": "AdaptiveQuiz/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def _extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    from PyPDF2 import PdfReader
    reader = PdfReader(filepath)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


# ---------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------

@bp.route("/upload/text", methods=["POST"])
@jwt_required()
def upload_text():
    """Accept raw text and chunk it."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    title = data.get("title", "Untitled")
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"msg": "text is required"}), 400

    content = Content(user_id=int(user_id), title=title, source_type="text", raw_text=raw_text)
    db.session.add(content)
    db.session.flush()

    for idx, chunk in enumerate(_chunk_text(raw_text)):
        db.session.add(ContentChunk(content_id=content.id, chunk_text=chunk, chunk_index=idx))
    db.session.commit()
    return jsonify({"msg": "content saved", "content": content.to_dict()}), 201


@bp.route("/upload/url", methods=["POST"])
@jwt_required()
def upload_url():
    """Fetch a URL, extract text, and chunk it."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    title = data.get("title", url[:80])
    if not url:
        return jsonify({"msg": "url is required"}), 400
    try:
        raw_text = _extract_text_from_url(url)
    except Exception as e:
        return jsonify({"msg": f"failed to fetch URL: {e}"}), 400

    content = Content(user_id=int(user_id), title=title, source_type="url", raw_text=raw_text)
    db.session.add(content)
    db.session.flush()
    for idx, chunk in enumerate(_chunk_text(raw_text)):
        db.session.add(ContentChunk(content_id=content.id, chunk_text=chunk, chunk_index=idx))
    db.session.commit()
    return jsonify({"msg": "content saved", "content": content.to_dict()}), 201


@bp.route("/upload/pdf", methods=["POST"])
@jwt_required()
def upload_pdf():
    """Accept a PDF file upload, extract text, and chunk it."""
    from flask import current_app
    user_id = get_jwt_identity()
    if "file" not in request.files:
        return jsonify({"msg": "PDF file is required"}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"msg": "only PDF files are supported"}), 400
    title = request.form.get("title", f.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], f.filename)
    f.save(filepath)
    try:
        raw_text = _extract_text_from_pdf(filepath)
    except Exception as e:
        return jsonify({"msg": f"failed to parse PDF: {e}"}), 400

    content = Content(user_id=int(user_id), title=title, source_type="pdf", raw_text=raw_text)
    db.session.add(content)
    db.session.flush()
    for idx, chunk in enumerate(_chunk_text(raw_text)):
        db.session.add(ContentChunk(content_id=content.id, chunk_text=chunk, chunk_index=idx))
    db.session.commit()
    return jsonify({"msg": "content saved", "content": content.to_dict()}), 201


@bp.route("/list", methods=["GET"])
@jwt_required()
def list_content():
    """List all content uploaded by the current user."""
    user_id = get_jwt_identity()
    items = Content.query.filter_by(user_id=int(user_id)).order_by(Content.created_at.desc()).all()
    return jsonify({"contents": [c.to_dict() for c in items]})


@bp.route("/<int:content_id>", methods=["GET"])
@jwt_required()
def get_content(content_id):
    """Get a specific content item with its chunks."""
    content = Content.query.get_or_404(content_id)
    chunks = [c.to_dict() for c in content.chunks]
    d = content.to_dict()
    d["chunks"] = chunks
    return jsonify({"content": d})


@bp.route("/<int:content_id>", methods=["DELETE"])
@jwt_required()
def delete_content(content_id):
    """Delete a content item."""
    user_id = get_jwt_identity()
    content = Content.query.get_or_404(content_id)
    if content.user_id != int(user_id):
        return jsonify({"msg": "forbidden"}), 403
    db.session.delete(content)
    db.session.commit()
    return jsonify({"msg": "content deleted"})
