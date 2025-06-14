from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, PoliceStation, User
from datetime import datetime, timezone

police_station_bp = Blueprint('police_station', __name__)

# Utility
def get_current_utc_time():
    return datetime.now(timezone.utc)

# GET all police stations
@police_station_bp.route('/', methods=['GET'])
@jwt_required()
def get_police_stations():
    db.session.expire_all()
    stations = PoliceStation.query.all()
    return jsonify([{
        'id': ps.id,
        'name': ps.name,
        'country': ps.country,
        'state': ps.state,
        'taluka': ps.taluka,
        'district': ps.district,
        'pincode': ps.pincode,
        'fullAddress': ps.full_address,
        'isActive': ps.is_active,
        'stationHouseOfficerId': ps.station_house_officer_id,
        'stationHouseOfficerName': ps.station_house_officer.fullName if ps.station_house_officer else None,
        'createdBy': ps.created_by,
        'createdAt': ps.created_at.isoformat() if ps.created_at else None,
        'updatedBy': ps.updated_by,
        'updatedAt': ps.updated_at.isoformat() if ps.updated_at else None
    } for ps in stations])

# POST create police station
@police_station_bp.route('/', methods=['POST'])
@jwt_required()
def create_police_station():
    data = request.get_json() or {}
    current_user_id = get_jwt_identity()

    ps = PoliceStation(
        name=data.get('name'),
        country=data.get('country', 'India'),
        state=data.get('state'),
        taluka=data.get('taluka'),
        district= data.get('district'),
        pincode=data.get('pincode'),
        full_address=data.get('fullAddress'),
        is_active=str(data.get('isActive', True)).lower() in ('true', '1', 'yes'),
        station_house_officer_id=data.get('stationHouseOfficerId'),
        created_by=current_user_id,
        created_at=get_current_utc_time(),
        updated_by=current_user_id,
        updated_at=get_current_utc_time()
    )
    db.session.add(ps)
    db.session.commit()
    return jsonify(id=ps.id, name=ps.name), 201

# PUT update police station
@police_station_bp.route('/<int:station_id>', methods=['PUT'])
@jwt_required()
def update_police_station(station_id):
    data = request.get_json() or {}
    current_user_id = get_jwt_identity()

    ps = PoliceStation.query.get_or_404(station_id)

    ps.name = data.get('name', ps.name)
    ps.country = data.get('country', ps.country)
    ps.state = data.get('state', ps.state)
    ps.district= data.get('district', ps.district)
    ps.taluka = data.get('taluka', ps.taluka)
    ps.pincode = data.get('pincode', ps.pincode)
    ps.full_address = data.get('fullAddress', ps.full_address)
    ps.is_active = bool(str(data.get('isActive', ps.is_active)).lower() in ('true', '1', 'yes'))
    ps.station_house_officer_id = data.get('stationHouseOfficerId', ps.station_house_officer_id)
    ps.updated_by = current_user_id
    ps.updated_at = get_current_utc_time()

    db.session.commit()
    return jsonify(msg='Updated')

# DELETE police station
@police_station_bp.route('/<int:station_id>', methods=['DELETE'])
@jwt_required()
def delete_police_station(station_id):
    ps = PoliceStation.query.get_or_404(station_id)
    db.session.delete(ps)
    db.session.commit()
    return jsonify(msg='Deleted')
