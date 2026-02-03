#!/usr/bin/env python3
"""
Add family members for all users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User
from models.member import Member

def add_all_family_members():
    db = SessionLocal()
    
    try:
        print("👨‍👩‍👧‍👦 Adding family members for all users...\n")
        
        # Define all users and their family members
        families = [
            {
                "email": "josh@josh.com",
                "members": [
                    {"name": "Josh Dicker", "relation": "self", "dietary": "NO shellfish, pork, blue cheese"},
                    {"name": "Dorrie Goodman", "relation": "spouse", "dietary": "NO olives, blue cheese"},
                    {"name": "Demi Dicker", "relation": "daughter", "dietary": "NO spicy"}
                ]
            },
            {
                "email": "sarah@sarah.com",
                "members": [
                    {"name": "Sarah Scott", "relation": "self", "dietary": "NO bananas"}
                ]
            },
            {
                "email": "jaime@jaime.com",
                "members": [
                    {"name": "Jaime Aker", "relation": "self", "dietary": None}
                ]
            },
            {
                "email": "brian@brian.com",
                "members": [
                    {"name": "Brian Kaiser", "relation": "self", "dietary": "NO fish"}
                ]
            }
        ]
        
        total_added = 0
        
        for family in families:
            # Find user
            user = db.query(User).filter_by(email=family["email"]).first()
            
            if not user:
                print(f"⚠️  User {family['email']} not found - skipping")
                continue
            
            print(f"👤 {user.name} ({user.email})")
            
            # Delete existing members
            existing = db.query(Member).filter_by(user_id=user.id).all()
            if existing:
                for member in existing:
                    db.delete(member)
                db.commit()
                print(f"   🗑️  Removed {len(existing)} existing members")
            
            # Add new members
            for member_data in family["members"]:
                member = Member(
                    user_id=user.id,
                    name=member_data["name"],
                    relation=member_data["relation"],
                    dietary_restrictions=member_data["dietary"]
                )
                db.add(member)
                dietary_text = member_data["dietary"] if member_data["dietary"] else "No restrictions"
                print(f"   ✅ {member.name} ({member.relation}) - {dietary_text}")
                total_added += 1
            
            db.commit()
            print()
        
        print(f"🎉 Successfully added {total_added} family members!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_all_family_members()