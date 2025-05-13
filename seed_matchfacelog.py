from app import create_app
from models import db, Matchfacelog

app = create_app()

def seed_matchfacelog():
    logs = [
        Matchfacelog(
            capture_time='2025-05-01 10:15:00',
            frame='frame1.jpg',
            cctv_id=1,
            suspect_id=1,
            suspect='Prakash Bhalerao',
            distance=0.25,
            created_date='2025-05-01 10:16:00'
        ),
        Matchfacelog(
            capture_time='2025-05-02 08:45:00',
            frame='frame2.jpg',
            cctv_id=2,
            suspect_id=1,
            suspect='John Doe',
            distance=0.29,
            created_date='2025-05-02 08:46:00'
        ),
        Matchfacelog(
            capture_time='2025-05-03 14:30:00',
            frame='frame3.jpg',
            cctv_id=2,
            suspect_id=2,
            suspect='Ketan Kokate',
            distance=0.18,
            created_date='2025-05-03 14:31:00'
        ),
        Matchfacelog(
            capture_time='2025-05-04 12:00:00',
            frame='frame4.jpg',
            cctv_id=2,
            suspect_id=2,
            suspect='Ketan Kokate',
            distance=0.33,
            created_date='2025-05-04 12:01:00'
        ),
        Matchfacelog(
            capture_time='2025-05-05 09:20:00',
            frame='frame5.jpg',
            cctv_id=2,
            suspect_id=3,  # Example of no match found
            suspect='Poonam Bhalerao',
            distance=0.70,
            created_date='2025-05-05 09:21:00'
        )
    ]

    with app.app_context():
        db.session.bulk_save_objects(logs)
        db.session.commit()
        print("✅ Matchfacelog seeded successfully.")

if __name__ == '__main__':
    seed_matchfacelog()
