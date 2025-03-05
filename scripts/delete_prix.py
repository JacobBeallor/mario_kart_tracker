import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add parent directory to path so we can import from project root
sys.path.append(str(Path(__file__).parent.parent))

from models import Prix, Race, RaceResult, PrixResult
from database import get_db_context

def delete_prix(prix_id: int) -> bool:
    """
    Delete a prix and all associated data from the database.
    
    Args:
        prix_id (int): The ID of the prix to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        with get_db_context() as db:
            # First check if prix exists
            prix = db.query(Prix).filter(Prix.prix_id == prix_id).first()
            if not prix:
                print(f"No prix found with ID {prix_id}")
                return False
                
            # Get confirmation from user
            date_played = prix.date_played.strftime("%Y-%m-%d")
            confirm = input(
                f"Are you sure you want to delete prix {prix_id} from {date_played}? "
                "This will delete all associated race results and cannot be undone. (y/N): "
            )
            
            if confirm.lower() != 'y':
                print("Deletion cancelled")
                return False

            # Delete all prix results
            db.query(PrixResult).filter(PrixResult.prix_id == prix_id).delete()
            
            # Get all races for this prix
            races = db.query(Race).filter(Race.prix_id == prix_id).all()
            race_ids = [race.race_id for race in races]
            
            # Delete all race results for these races
            if race_ids:
                db.query(RaceResult).filter(RaceResult.race_id.in_(race_ids)).delete()
            
            # Delete all races
            db.query(Race).filter(Race.prix_id == prix_id).delete()
            
            # Finally delete the prix
            db.query(Prix).filter(Prix.prix_id == prix_id).delete()
            
            # Commit the transaction
            db.commit()
            
            print(f"Successfully deleted prix {prix_id} and all associated data")
            return True
            
    except Exception as e:
        print(f"Error deleting prix: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_prix.py <prix_id>")
        sys.exit(1)
        
    try:
        prix_id = int(sys.argv[1])
    except ValueError:
        print("Error: prix_id must be a number")
        sys.exit(1)
        
    success = delete_prix(prix_id)
    sys.exit(0 if success else 1) 