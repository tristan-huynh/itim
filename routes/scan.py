import secrets
import string

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import db, Bin, Asset

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/', methods=['GET', 'POST'])
def index():
    