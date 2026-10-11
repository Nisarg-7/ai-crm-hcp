from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import HCP, Product, User, FollowUp, Interaction

DEMO_PASSWORD = "Demo@1234"

USERS = [
    {"email": "rep1@democrm.com", "full_name": "Aarav Mehta", "territory": "Mumbai West"},
    {"email": "rep2@democrm.com", "full_name": "Priya Nair", "territory": "Mumbai Central"},
]

HCPS = [
    {"full_name": "Dr. Rohan Kapoor", "specialty": "Cardiology", "organization": "Lilavati Hospital", "city": "Mumbai", "email": "rohan.kapoor@example.com", "phone": "+91 98200 10001"},
    {"full_name": "Dr. Sneha Iyer", "specialty": "Endocrinology", "organization": "Kokilaben Hospital", "city": "Mumbai", "email": "sneha.iyer@example.com", "phone": "+91 98200 10002"},
    {"full_name": "Dr. Arjun Deshmukh", "specialty": "Oncology", "organization": "Tata Memorial Hospital", "city": "Mumbai", "email": "arjun.deshmukh@example.com", "phone": "+91 98200 10003"},
    {"full_name": "Dr. Meera Joshi", "specialty": "Pulmonology", "organization": "Hinduja Hospital", "city": "Mumbai", "email": "meera.joshi@example.com", "phone": "+91 98200 10004"},
    {"full_name": "Dr. Vikram Shah", "specialty": "Neurology", "organization": "Nanavati Hospital", "city": "Mumbai", "email": "vikram.shah@example.com", "phone": "+91 98200 10005"},
    {"full_name": "Dr. Anjali Rao", "specialty": "Cardiology", "organization": "Fortis Hospital", "city": "Navi Mumbai", "email": "anjali.rao@example.com", "phone": "+91 98200 10006"},
    {"full_name": "Dr. Sameer Khan", "specialty": "General Medicine", "organization": "Wockhardt Hospital", "city": "Mumbai", "email": "sameer.khan@example.com", "phone": "+91 98200 10007"},
    {"full_name": "Dr. Kavita Pillai", "specialty": "Endocrinology", "organization": "Jaslok Hospital", "city": "Mumbai", "email": "kavita.pillai@example.com", "phone": "+91 98200 10008"},
    {"full_name": "Dr. Nikhil Bhatt", "specialty": "Gastroenterology", "organization": "Apollo Hospital", "city": "Navi Mumbai", "email": "nikhil.bhatt@example.com", "phone": "+91 98200 10009"},
    {"full_name": "Dr. Pooja Menon", "specialty": "Rheumatology", "organization": "Breach Candy Hospital", "city": "Mumbai", "email": "pooja.menon@example.com", "phone": "+91 98200 10010"},
]

PRODUCTS = [
    {"name": "CardioSafe 10mg", "category": "Cardiovascular", "description": "Statin for lowering LDL cholesterol in high-risk patients."},
    {"name": "GlucoBalance XR", "category": "Diabetes", "description": "Extended-release metformin for type 2 diabetes management."},
    {"name": "OncoGuard 50", "category": "Oncology", "description": "Targeted therapy supporting first-line cancer treatment."},
    {"name": "RespiClear Inhaler", "category": "Respiratory", "description": "Long-acting bronchodilator for COPD and asthma."},
    {"name": "NeuroCalm 25", "category": "Neurology", "description": "Anticonvulsant for epilepsy and neuropathic pain."},
]

# (rep_index, hcp_index, type, days_ago, sentiment, summary, notes, source, [product_indexes], follow_up)
INTERACTIONS = [
    (0, 0, "visit", 2, "positive",
     "Discussed CardioSafe 10mg efficacy data with Dr. Kapoor; he is interested in using it for high-risk patients.",
     "Dr. Kapoor asked about long-term safety data and dosing in elderly patients.",
     "form", [0],
     ("Send CardioSafe long-term safety study PDF", 3)),
    (0, 1, "call", 5, "neutral",
     "Phone call with Dr. Iyer about GlucoBalance XR. She wants to compare it with her current prescription.",
     "Needs side-effect comparison before deciding.",
     "ai_chat", [1],
     ("Share GlucoBalance XR comparison sheet", 7)),
    (1, 2, "visit", 7, "positive",
     "Presented OncoGuard 50 trial results to Dr. Deshmukh, who asked for a meeting with the medical team.",
     "Very engaged; open to a hospital-level presentation.",
     "form", [2],
     ("Arrange medical team meeting at Tata Memorial", 10)),
    (1, 3, "visit", 10, "negative",
     "Dr. Joshi raised concerns about RespiClear Inhaler pricing compared with competitors.",
     "Price was the main objection; clinical efficacy was acknowledged.",
     "ai_chat", [3],
     None),
    (0, 4, "email", 1, "neutral",
     "Emailed NeuroCalm 25 prescribing information to Dr. Shah.",
     "No reply yet.",
     "form", [4],
     ("Call Dr. Shah to confirm he received the email", 4)),
    (0, 5, "visit", 14, "positive",
     "Met Dr. Rao to discuss CardioSafe 10mg and GlucoBalance XR for patients with both conditions.",
     "Wants combined-therapy guidance.",
     "ai_chat", [0, 1],
     ("Send combined-therapy guidance document", 5)),
]


def seed_users(db):
    if db.scalar(select(User).limit(1)):
        print("Users already exist, skipping")
        return
    for u in USERS:
        db.add(User(hashed_password=hash_password(DEMO_PASSWORD), **u))
    db.commit()
    print(f"Added {len(USERS)} users")


def seed_hcps(db):
    if db.scalar(select(HCP).limit(1)):
        print("HCPs already exist, skipping")
        return
    db.add_all([HCP(**h) for h in HCPS])
    db.commit()
    print(f"Added {len(HCPS)} HCPs")


def seed_products(db):
    if db.scalar(select(Product).limit(1)):
        print("Products already exist, skipping")
        return
    db.add_all([Product(**p) for p in PRODUCTS])
    db.commit()
    print(f"Added {len(PRODUCTS)} products")


def seed_interactions(db):
    if db.scalar(select(Interaction).limit(1)):
        print("Interactions already exist, skipping")
        return

    users = db.scalars(select(User).order_by(User.id)).all()
    hcps = db.scalars(select(HCP).order_by(HCP.id)).all()
    products = db.scalars(select(Product).order_by(Product.id)).all()
    now = datetime.now(timezone.utc)

    for rep_i, hcp_i, itype, days_ago, sentiment, summary, notes, source, prod_idx, follow_up in INTERACTIONS:
        interaction = Interaction(
            rep_id=users[rep_i].id,
            hcp_id=hcps[hcp_i].id,
            interaction_type=itype,
            interaction_date=now - timedelta(days=days_ago),
            sentiment=sentiment,
            summary=summary,
            notes=notes,
            source=source,
            products=[products[i] for i in prod_idx],
        )
        db.add(interaction)
        if follow_up:
            description, due_in_days = follow_up
            db.add(
                FollowUp(
                    interaction=interaction,
                    description=description,
                    due_date=(now + timedelta(days=due_in_days)).date(),
                )
            )
    db.commit()
    print(f"Added {len(INTERACTIONS)} interactions")


def main():
    db = SessionLocal()
    try:
        seed_users(db)
        seed_hcps(db)
        seed_products(db)
        seed_interactions(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()