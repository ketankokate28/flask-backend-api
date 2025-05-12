from Model import Members
from typing import List, Optional
from datetime import datetime

class MembersStore:
    @staticmethod
    def get_all(active_only: bool = True) -> List[Members]:
        query = Members.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()

    @staticmethod
    def get_by_id(member_id: int) -> Optional[Members]:
        return Members.query.get(member_id)

    @staticmethod
    def create(
        first_name: str,
        last_name: str,
        email: Optional[str],
        phone_number: Optional[str],
        is_active: bool = True
    ) -> Members:
        mem = Members(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            is_active=is_active,
            created_at=datetime.utcnow(),
            update_at=datetime.utcnow()
        )
        db.session.add(mem)
        db.session.commit()
        return mem

    @staticmethod
    def update(
        member_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Members]:
        mem = Members.query.get(member_id)
        if not mem:
            return None
        if first_name is not None:
            mem.first_name = first_name
        if last_name is not None:
            mem.last_name = last_name
        if email is not None:
            mem.email = email
        if phone_number is not None:
            mem.phone_number = phone_number
        if is_active is not None:
            mem.is_active = is_active
        mem.update_at = datetime.utcnow()
        db.session.commit()
        return mem

    @staticmethod
    def delete(member_id: int) -> bool:
        mem = Members.query.get(member_id)
        if not mem:
            return False
        db.session.delete(mem)
        db.session.commit()
        return True