# routes/site_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db
from models import Site

site_bp = Blueprint('sites', __name__)

@site_bp.route('', methods=['GET'])
@jwt_required()
def get_sites():
    sites = Site.query.all()
    return jsonify([site.to_dict() for site in sites])

@site_bp.route('', methods=['POST'])
@jwt_required()
def create_site():
    data = request.json
    site = Site(
        subnode_id=data['subnode_id'],
        name=data['name'],
        description=data.get('description'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        altitude=data.get('altitude'),
        address=data.get('address'),
        dvr_ip=data.get('dvr_ip'),
        dvr_port=data.get('dvr_port', 554),
        dvr_username=data.get('dvr_username'),
        dvr_password=data.get('dvr_password'),
        dvr_rtsp_url=data.get('dvr_rtsp_url'),
        dvr_model=data.get('dvr_model'),
        dvr_vendor=data.get('dvr_vendor'),
        dvr_firmware_version=data.get('dvr_firmware_version'),
        last_maintenance_date=data.get('last_maintenance_date'),
        is_active=data.get('is_active', True)
    )
    db.session.add(site)
    db.session.commit()
    return jsonify(site.to_dict()), 201

@site_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_site(id):
    site = Site.query.get_or_404(id)
    data = request.json
    for field in data:
        setattr(site, field, data[field])
    db.session.commit()
    return jsonify(site.to_dict())

@site_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_site(id):
    site = Site.query.get_or_404(id)
    db.session.delete(site)
    db.session.commit()
    return jsonify({'message': 'Deleted'})
