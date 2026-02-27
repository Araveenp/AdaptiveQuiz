from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from .models import User
from .database import db
from .utils import hash_password, verify_password

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    preferred_difficulty = data.get("preferred_difficulty", "medium")
    subjects = data.get("subjects", [])

    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "user already exists"}), 400

    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        preferred_difficulty=preferred_difficulty,
    )
    user.set_subjects(subjects)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "user created", "user": user.to_dict()}), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"msg": "invalid credentials"}), 401

    # Use string identity for JWT 'sub' to avoid PyJWT subject type validation issues
    access = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access, "user": user.to_dict()})


@bp.route("/profile", methods=["GET", "PUT"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "user not found"}), 404

    if request.method == "GET":
        return jsonify({"user": user.to_dict()})

    # PUT - update
    data = request.get_json() or {}
    name = data.get("name")
    preferred_difficulty = data.get("preferred_difficulty")
    subjects = data.get("subjects")

    if name is not None:
        user.name = name
    if preferred_difficulty is not None:
        user.preferred_difficulty = preferred_difficulty
    if subjects is not None:
        user.set_subjects(subjects)

    db.session.commit()
    return jsonify({"msg": "profile updated", "user": user.to_dict()})
