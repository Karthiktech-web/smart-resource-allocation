"""
SEED DATA SCRIPT
================
Populates Firestore with realistic demo data for the Smart Resource Allocation platform.

Usage:
    python seed_data.py

Collections seeded:
    1. programs
    2. areas
    3. needs
    4. volunteers
    5. impact_logs
    6. surveys
"""

import os
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account-key.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def clear_collection(collection_name: str):
    docs = db.collection(collection_name).stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    print(f"  Cleared {collection_name} ({count} docs)")


def clear_all():
    print("Clearing existing data...")
    for col in ["programs", "areas", "needs", "volunteers", "assignments", "impact_logs", "surveys"]:
        clear_collection(col)
    print("  Done!\n")


def seed_programs() -> list[str]:
    print("Seeding programs...")
    programs = [
        {
            "name": "Water Access Survey 2026",
            "organization": "WaterAid Andhra Pradesh",
            "category": "water",
            "description": "Comprehensive survey of water access, quality, and distribution infrastructure across rural AP.",
            "regions": ["Anantapur", "Kurnool", "Kadapa"],
            "survey_count": 12,
            "needs_discovered": 8,
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Child Health Initiative",
            "organization": "UNICEF AP Chapter",
            "category": "health",
            "description": "Assessment of child malnutrition, vaccination coverage, and access to primary healthcare.",
            "regions": ["Kurnool", "Prakasam", "Anantapur"],
            "survey_count": 8,
            "needs_discovered": 6,
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=12),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Rural Education Assessment",
            "organization": "Teach For India - AP",
            "category": "education",
            "description": "Evaluating school infrastructure, teacher availability, digital access, and learning outcomes.",
            "regions": ["Kadapa", "Prakasam"],
            "survey_count": 6,
            "needs_discovered": 5,
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Food Security Drive",
            "organization": "Akshaya Patra Foundation",
            "category": "food",
            "description": "Mapping food insecurity across drought-affected regions and tracking nutrition gaps.",
            "regions": ["Anantapur", "Kurnool"],
            "survey_count": 10,
            "needs_discovered": 7,
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow(),
        },
    ]

    ids = []
    for prog in programs:
        ref = db.collection("programs").document()
        ref.set(prog)
        ids.append(ref.id)
        print(f"  Created program: {prog['name']} [{ref.id}]")
    return ids


def seed_areas(program_ids: list[str]) -> list[str]:
    print("\nSeeding areas...")
    areas = [
        {
            "name": "Anantapur Rural",
            "district": "Anantapur",
            "state": "Andhra Pradesh",
            "lat": 14.6819,
            "lng": 77.6006,
            "total_needs": 6,
            "open_needs": 4,
            "critical_needs_count": 2,
            "needs_by_category": {"water": 3, "food": 2, "health": 1},
            "compound_score": 8.7,
            "area_priority": "critical",
            "programs_active": [program_ids[0], program_ids[3]],
            "volunteers_assigned": 3,
            "volunteers_recommended": 8,
            "volunteer_gap": 5,
            "ai_insights": [
                "Water scarcity and food insecurity are compounding problems.",
                "Cross-program pattern: households reporting water issues also report food insecurity.",
                "Malnutrition reports correlate with water contamination incidents.",
            ],
            "last_analyzed_at": datetime.utcnow(),
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Kurnool East",
            "district": "Kurnool",
            "state": "Andhra Pradesh",
            "lat": 15.8281,
            "lng": 78.0373,
            "total_needs": 5,
            "open_needs": 3,
            "critical_needs_count": 1,
            "needs_by_category": {"health": 2, "water": 1, "education": 1, "food": 1},
            "compound_score": 7.2,
            "area_priority": "high",
            "programs_active": [program_ids[0], program_ids[1], program_ids[3]],
            "volunteers_assigned": 2,
            "volunteers_recommended": 6,
            "volunteer_gap": 4,
            "ai_insights": [
                "Healthcare access is the primary concern.",
                "Water quality issues are driving health emergencies.",
                "Children are affected by both malnutrition and poor school health coverage.",
            ],
            "last_analyzed_at": datetime.utcnow(),
            "created_at": datetime.utcnow() - timedelta(days=12),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Kadapa South",
            "district": "Kadapa",
            "state": "Andhra Pradesh",
            "lat": 14.4674,
            "lng": 78.8241,
            "total_needs": 4,
            "open_needs": 3,
            "critical_needs_count": 0,
            "needs_by_category": {"education": 2, "water": 1, "infrastructure": 1},
            "compound_score": 5.5,
            "area_priority": "medium",
            "programs_active": [program_ids[0], program_ids[2]],
            "volunteers_assigned": 2,
            "volunteers_recommended": 4,
            "volunteer_gap": 2,
            "ai_insights": [
                "Education infrastructure needs are significant.",
                "Water supply issues affect school attendance.",
            ],
            "last_analyzed_at": datetime.utcnow(),
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Prakasam Coastal",
            "district": "Prakasam",
            "state": "Andhra Pradesh",
            "lat": 15.3647,
            "lng": 80.0444,
            "total_needs": 3,
            "open_needs": 2,
            "critical_needs_count": 1,
            "needs_by_category": {"health": 1, "food": 1, "shelter": 1},
            "compound_score": 6.8,
            "area_priority": "high",
            "programs_active": [program_ids[1], program_ids[3]],
            "volunteers_assigned": 1,
            "volunteers_recommended": 5,
            "volunteer_gap": 4,
            "ai_insights": [
                "Coastal flooding has displaced families.",
                "Post-flood health risks are high.",
                "Food supply chains are disrupted.",
            ],
            "last_analyzed_at": datetime.utcnow(),
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow(),
        },
    ]

    ids = []
    for area in areas:
        ref = db.collection("areas").document()
        ref.set(area)
        ids.append(ref.id)
        print(f"  Created area: {area['name']} [score: {area['compound_score']}]")
    return ids


def seed_needs(program_ids: list[str], area_ids: list[str]) -> list[str]:
    print("\nSeeding needs...")
    needs = [
        {
            "title": "Contaminated water supply affecting 200+ families",
            "description": "Bore well water shows high fluoride and E.coli levels. Over 200 families depend on this source.",
            "category": "water",
            "urgency": "critical",
            "location_name": "Anantapur Rural",
            "lat": 14.6819,
            "lng": 77.6006,
            "area_id": area_ids[0],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[0],
            "ai_confidence": 0.94,
            "ai_priority_score": 9.2,
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "Severe food shortage in drought-affected villages",
            "description": "Three consecutive failed monsoons have devastated crops. PDS ration distribution is irregular.",
            "category": "food",
            "urgency": "critical",
            "location_name": "Anantapur Rural",
            "lat": 14.6819,
            "lng": 77.6006,
            "area_id": area_ids[0],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[3],
            "ai_confidence": 0.91,
            "ai_priority_score": 9.0,
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=8),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "No primary healthcare center within 18km",
            "description": "Nearest PHC is far away and there is no reliable emergency transport.",
            "category": "health",
            "urgency": "critical",
            "location_name": "Kurnool East",
            "lat": 15.8281,
            "lng": 78.0373,
            "area_id": area_ids[1],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[1],
            "ai_confidence": 0.96,
            "ai_priority_score": 9.5,
            "status": "assigned",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=9),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "School lacks basic infrastructure",
            "description": "Government primary school serving 180 students has no functional toilets and a leaking roof.",
            "category": "education",
            "urgency": "high",
            "location_name": "Kadapa South",
            "lat": 14.4674,
            "lng": 78.8241,
            "area_id": area_ids[2],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[2],
            "ai_confidence": 0.89,
            "ai_priority_score": 7.5,
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=7),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "Post-flood temporary shelters lack sanitation",
            "description": "Families displaced by coastal flooding are living in temporary shelters without proper sanitation.",
            "category": "shelter",
            "urgency": "critical",
            "location_name": "Prakasam Coastal",
            "lat": 15.3647,
            "lng": 80.0444,
            "area_id": area_ids[3],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[1],
            "ai_confidence": 0.93,
            "ai_priority_score": 8.8,
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "Water pipeline damaged in 3 villages",
            "description": "Main water pipeline was damaged and tanker supply is insufficient.",
            "category": "water",
            "urgency": "high",
            "location_name": "Anantapur Rural",
            "lat": 14.6819,
            "lng": 77.6006,
            "area_id": area_ids[0],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[0],
            "ai_confidence": 0.87,
            "ai_priority_score": 7.8,
            "status": "assigned",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=6),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "Child malnutrition rate at 35%",
            "description": "Survey reveals 35% of children under 5 are underweight and nutrition coverage is incomplete.",
            "category": "health",
            "urgency": "high",
            "location_name": "Kurnool East",
            "lat": 15.8281,
            "lng": 78.0373,
            "area_id": area_ids[1],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[1],
            "ai_confidence": 0.92,
            "ai_priority_score": 8.0,
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=4),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "Road access cut off during monsoon",
            "description": "Unpaved roads to 2 villages become impassable during monsoon and emergency services cannot reach.",
            "category": "infrastructure",
            "urgency": "medium",
            "location_name": "Kadapa South",
            "lat": 14.4674,
            "lng": 78.8241,
            "area_id": area_ids[2],
            "source_type": "ai_discovered",
            "source_program_id": program_ids[2],
            "ai_confidence": 0.85,
            "ai_priority_score": 6.0,
            "status": "open",
            "assigned_volunteers": [],
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow(),
        },
    ]

    ids = []
    for need in needs:
        ref = db.collection("needs").document()
        ref.set(need)
        ids.append(ref.id)
        print(f"  Created need: [{need['urgency'].upper()}] {need['title'][:60]}...")
    return ids


def seed_volunteers() -> list[str]:
    print("\nSeeding volunteers...")
    volunteers = [
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@example.com",
            "phone": "+91 9876543210",
            "location_name": "Anantapur Town",
            "lat": 14.6819,
            "lng": 77.6006,
            "skills": ["Water purification", "Community health", "First Aid"],
            "availability": "weekends",
            "total_hours": 120,
            "tasks_completed": 8,
            "reliability_score": 0.95,
            "active_assignments": 1,
            "categories_experienced": ["water", "health"],
            "max_concurrent_assignments": 3,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Ravi Kumar",
            "email": "ravi.kumar@example.com",
            "phone": "+91 9876543211",
            "location_name": "Kurnool City",
            "lat": 15.8281,
            "lng": 78.0373,
            "skills": ["Teaching", "Tutoring", "Computer training"],
            "availability": "full_time",
            "total_hours": 200,
            "tasks_completed": 15,
            "reliability_score": 0.98,
            "active_assignments": 2,
            "categories_experienced": ["education", "health"],
            "max_concurrent_assignments": 3,
            "created_at": datetime.utcnow() - timedelta(days=45),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Lakshmi Devi",
            "email": "lakshmi.devi@example.com",
            "phone": "+91 9876543212",
            "location_name": "Kadapa Town",
            "lat": 14.4674,
            "lng": 78.8241,
            "skills": ["Nursing", "Vaccination", "Maternal health"],
            "availability": "weekdays",
            "total_hours": 80,
            "tasks_completed": 5,
            "reliability_score": 0.90,
            "active_assignments": 1,
            "categories_experienced": ["health"],
            "max_concurrent_assignments": 2,
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Suresh Reddy",
            "email": "suresh.reddy@example.com",
            "phone": "+91 9876543213",
            "location_name": "Prakasam Town",
            "lat": 15.3647,
            "lng": 80.0444,
            "skills": ["Construction", "Plumbing", "Electrical"],
            "availability": "weekends",
            "total_hours": 60,
            "tasks_completed": 4,
            "reliability_score": 0.85,
            "active_assignments": 0,
            "categories_experienced": ["infrastructure", "shelter"],
            "max_concurrent_assignments": 2,
            "created_at": datetime.utcnow() - timedelta(days=25),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Anitha Rao",
            "email": "anitha.rao@example.com",
            "phone": "+91 9876543214",
            "location_name": "Anantapur Rural",
            "lat": 14.7000,
            "lng": 77.6200,
            "skills": ["Agriculture", "Food distribution", "Community organizing"],
            "availability": "full_time",
            "total_hours": 150,
            "tasks_completed": 10,
            "reliability_score": 0.92,
            "active_assignments": 1,
            "categories_experienced": ["food", "water"],
            "max_concurrent_assignments": 3,
            "created_at": datetime.utcnow() - timedelta(days=35),
            "updated_at": datetime.utcnow(),
        },
        {
            "name": "Venkat Naidu",
            "email": "venkat.naidu@example.com",
            "phone": "+91 9876543215",
            "location_name": "Kurnool East",
            "lat": 15.8500,
            "lng": 78.0500,
            "skills": ["Data collection", "Survey", "Translation"],
            "availability": "weekdays",
            "total_hours": 40,
            "tasks_completed": 3,
            "reliability_score": 0.88,
            "active_assignments": 0,
            "categories_experienced": ["education"],
            "max_concurrent_assignments": 2,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow(),
        },
    ]

    ids = []
    for vol in volunteers:
        ref = db.collection("volunteers").document()
        ref.set(vol)
        ids.append(ref.id)
        print(f"  Created volunteer: {vol['name']} [{', '.join(vol['skills'][:2])}]")
    return ids


def seed_impact_logs(area_ids: list[str]):
    print("\nSeeding impact logs...")
    impacts = [
        {
            "category": "water",
            "description": "Installed water purification filters in 50 households.",
            "people_helped": 250,
            "volunteer_hours": 40,
            "area_id": area_ids[0],
            "created_at": datetime.utcnow() - timedelta(days=5),
        },
        {
            "category": "health",
            "description": "Vaccination drive for 120 children under 5.",
            "people_helped": 120,
            "volunteer_hours": 24,
            "area_id": area_ids[1],
            "created_at": datetime.utcnow() - timedelta(days=3),
        },
        {
            "category": "food",
            "description": "Distributed emergency food packets to 80 families.",
            "people_helped": 400,
            "volunteer_hours": 16,
            "area_id": area_ids[0],
            "created_at": datetime.utcnow() - timedelta(days=2),
        },
        {
            "category": "education",
            "description": "Set up temporary learning center with donated books.",
            "people_helped": 45,
            "volunteer_hours": 60,
            "area_id": area_ids[2],
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
        {
            "category": "shelter",
            "description": "Built 5 temporary shelters with sanitation for displaced families.",
            "people_helped": 25,
            "volunteer_hours": 32,
            "area_id": area_ids[3],
            "created_at": datetime.utcnow(),
        },
    ]

    for imp in impacts:
        ref = db.collection("impact_logs").document()
        ref.set(imp)
        print(f"  Created impact: {imp['category']} - {imp['people_helped']} people helped")


def seed_surveys(program_ids: list[str]):
    print("\nSeeding surveys...")
    surveys = [
        {
            "program_id": program_ids[0],
            "location_name": "Anantapur Rural",
            "lat": 14.6819,
            "lng": 77.6006,
            "source_type": "photo",
            "image_urls": [],
            "raw_text": "Ma gramamlo neeti samasya chala teevranga undi. Boru bavi neeru kalushitamai undi.",
            "translated_text": "The water problem in our village is very severe. Bore well water is contaminated.",
            "language_detected": "te",
            "ai_analysis": {
                "needs_extracted": [
                    {
                        "category": "water",
                        "urgency": "critical",
                        "description": "Contaminated bore well water affecting 200 families",
                        "confidence": 0.94,
                    }
                ],
                "summary": "Village facing severe water contamination crisis.",
            },
            "sentiment": "negative",
            "created_at": datetime.utcnow() - timedelta(days=10),
        },
        {
            "program_id": program_ids[1],
            "location_name": "Kurnool East",
            "lat": 15.8281,
            "lng": 78.0373,
            "source_type": "photo",
            "image_urls": [],
            "raw_text": "Bachchon mein kuposhan bahut badh raha hai. 35 pratishat bachche kam vajan ke hain.",
            "translated_text": "Malnutrition in children is increasing rapidly. 35% of children are underweight.",
            "language_detected": "hi",
            "ai_analysis": {
                "needs_extracted": [
                    {
                        "category": "health",
                        "urgency": "high",
                        "description": "35% child malnutrition rate",
                        "confidence": 0.92,
                    }
                ],
                "summary": "Alarming child malnutrition rates.",
            },
            "sentiment": "negative",
            "created_at": datetime.utcnow() - timedelta(days=4),
        },
        {
            "program_id": program_ids[2],
            "location_name": "Kadapa South",
            "lat": 14.4674,
            "lng": 78.8241,
            "source_type": "photo",
            "image_urls": [],
            "raw_text": "School has no toilets. Roof is leaking badly. Only 2 teachers for 180 students.",
            "translated_text": "School has no toilets. Roof is leaking badly. Only 2 teachers for 180 students.",
            "language_detected": "en",
            "ai_analysis": {
                "needs_extracted": [
                    {
                        "category": "education",
                        "urgency": "high",
                        "description": "School lacking basic infrastructure",
                        "confidence": 0.89,
                    }
                ],
                "summary": "Government school severely lacking infrastructure.",
            },
            "sentiment": "negative",
            "created_at": datetime.utcnow() - timedelta(days=7),
        },
    ]

    for survey in surveys:
        ref = db.collection("surveys").document()
        ref.set(survey)
        print(f"  Created survey: {survey['location_name']} ({survey['language_detected']})")


if __name__ == "__main__":
    print("=" * 60)
    print("  SMART RESOURCE ALLOCATION - SEED DATA SCRIPT")
    print("=" * 60)
    print()

    # Uncomment this if you want a fresh reset before seeding:
    clear_all()

    program_ids = seed_programs()
    area_ids = seed_areas(program_ids)
    need_ids = seed_needs(program_ids, area_ids)
    vol_ids = seed_volunteers()
    seed_impact_logs(area_ids)
    seed_surveys(program_ids)

    print()
    print("=" * 60)
    print("  SEED DATA COMPLETE!")
    print(f"  Programs:    {len(program_ids)}")
    print(f"  Areas:       {len(area_ids)}")
    print(f"  Needs:       {len(need_ids)}")
    print(f"  Volunteers:  {len(vol_ids)}")
    print("  Impacts:     5")
    print("  Surveys:     3")
    print("=" * 60)
