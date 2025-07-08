from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Subnode, User, Node
from datetime import datetime, timezone

subnode_police_station_bp = Blueprint('subnode', __name__)

def get_current_utc_time():
    return datetime.now(timezone.utc)

# GET all subnodes (police stations at subnode level)
@subnode_police_station_bp.route('/', methods=['GET'])
@jwt_required()
def get_subnodes():
    db.session.expire_all()
    subnodes = Subnode.query.all()
    return jsonify([{
        'id': sn.id,
        'name': sn.name,
        'country': sn.country,
        'state': sn.state,
        'taluka': sn.taluka,
        'district': sn.district,
        'pincode': sn.pincode,
        'fullAddress': sn.full_address,
        'isActive': sn.is_active,
        'stationHouseOfficerId': sn.station_house_officer_id,
        'stationHouseOfficerName': sn.station_house_officer.fullName if sn.station_house_officer else None,
        'createdBy': sn.created_by,
        'createdAt': sn.created_at.isoformat() if sn.created_at else None,
        'updatedBy': sn.updated_by,
        'updatedAt': sn.updated_at.isoformat() if sn.updated_at else None,
        'nodeId': sn.node_id
    } for sn in subnodes])

# POST create subnode police station
@subnode_police_station_bp.route('/', methods=['POST'])
@jwt_required()
def create_subnode():
    data = request.get_json() or {}
    current_user_id = get_jwt_identity()

    district = data.get('district')
    if not district:
        return jsonify(msg="District is required to determine Node"), 400

    # Find Node by district name
    node = Node.query.filter_by(name=district).first()
    if not node:
        return jsonify(msg=f"Node with district '{district}' not found in Node table"), 400

    sn = Subnode(
        name=data.get('name'),
        country=data.get('country', 'India'),
        state=data.get('state'),
        district=district,
        taluka=data.get('taluka'),
        pincode=data.get('pincode'),
        full_address=data.get('fullAddress'),
        is_active=str(data.get('isActive', True)).lower() in ('true', '1', 'yes'),
        station_house_officer_id=data.get('stationHouseOfficerId'),
        node_id=node.id,
        created_by=current_user_id,
        created_at=get_current_utc_time(),
        updated_by=current_user_id,
        updated_at=get_current_utc_time()
    )
    db.session.add(sn)
    db.session.commit()
    return jsonify(id=sn.id, name=sn.name, nodeId=node.id), 201

# PUT update subnode
@subnode_police_station_bp.route('/<int:subnode_id>', methods=['PUT'])
@jwt_required()
def update_subnode(subnode_id):
    data = request.get_json() or {}
    current_user_id = get_jwt_identity()

    sn = Subnode.query.get_or_404(subnode_id)

    if 'district' in data:
        district = data['district']
        node = Node.query.filter_by(name=district).first()
        if not node:
            return jsonify(msg=f"Node with district '{district}' not found in Node table"), 400
        sn.node_id = node.id
        sn.district = district

    sn.name = data.get('name', sn.name)
    sn.country = data.get('country', sn.country)
    sn.state = data.get('state', sn.state)
    sn.taluka = data.get('taluka', sn.taluka)
    sn.pincode = data.get('pincode', sn.pincode)
    sn.full_address = data.get('fullAddress', sn.full_address)
    sn.is_active = bool(str(data.get('isActive', sn.is_active)).lower() in ('true', '1', 'yes'))
    sn.station_house_officer_id = data.get('stationHouseOfficerId', sn.station_house_officer_id)
    sn.updated_by = current_user_id
    sn.updated_at = get_current_utc_time()

    db.session.commit()
    return jsonify(msg='Updated', nodeId=sn.node_id)

# DELETE subnode
@subnode_police_station_bp.route('/<int:subnode_id>', methods=['DELETE'])
@jwt_required()
def delete_subnode(subnode_id):
    sn = Subnode.query.get_or_404(subnode_id)
    db.session.delete(sn)
    db.session.commit()
    return jsonify(msg='Deleted')
