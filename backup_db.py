import sqlite3
import shutil
from datetime import datetime
import os
import schedule
import time
from tqdm import tqdm

def backup_database():
    print("\n=== Starting Database Backup Process ===")
    
    # Create backups directory if it doesn't exist
    backup_dir = "database_backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print("✓ Created backup directory")
    
    # Show spinning progress indicator for each step
    with tqdm(total=5, desc="Backup Progress") as pbar:
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"crm_backup_{timestamp}.db")
        pbar.set_description("Initializing backup")
        pbar.update(1)
        
        try:
            # Connect to the source database
            source_conn = sqlite3.connect('crm.db')
            cursor = source_conn.cursor()
            pbar.set_description("Connected to source database")
            pbar.update(1)
            
            # Get all table names and create backup file
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            shutil.copy2('crm.db', backup_file)
            pbar.set_description("Created backup file")
            pbar.update(1)
            
            # Verify backup
            backup_conn = sqlite3.connect(backup_file)
            backup_cursor = backup_conn.cursor()
            
            # Verify each table with nested progress bar
            pbar.set_description("Verifying tables")
            for table in tqdm(tables, desc="Table Verification", leave=False):
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                source_count = cursor.fetchone()[0]
                backup_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                backup_count = backup_cursor.fetchone()[0]
                
                if source_count != backup_count:
                    raise ValueError(f"Backup verification failed for table {table_name}")
            pbar.update(1)
            
            # Clean up old backups
            cleanup_old_backups(backup_dir, 7)
            pbar.set_description("Cleaned up old backups")
            pbar.update(1)
            
            source_conn.close()
            backup_conn.close()
            
            backup_size = os.path.getsize(backup_file) / (1024 * 1024)  # Convert to MB
            print(f"\n✓ Backup completed successfully:")
            print(f"  - File: {backup_file}")
            print(f"  - Size: {backup_size:.2f} MB")
            print(f"  - Tables backed up: {len(tables)}")
            return True
            
        except Exception as e:
            print(f"\n❌ Backup failed: {str(e)}")
            if os.path.exists(backup_file):
                os.remove(backup_file)
            return False

def cleanup_old_backups(backup_dir, days_to_keep):
    """Remove backups older than specified days"""
    current_time = datetime.now()
    for filename in os.listdir(backup_dir):
        if filename.startswith("crm_backup_") and filename.endswith(".db"):
            file_path = os.path.join(backup_dir, filename)
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
            
            if file_age.days > days_to_keep:
                os.remove(file_path)
                print(f"Removed old backup: {filename}")

def schedule_backup():
    """Schedule daily backup"""
    schedule.every().day.at("00:00").do(backup_database)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Database Backup Utility')
    parser.add_argument('--schedule', action='store_true', help='Run as scheduled service')
    parser.add_argument('--manual', action='store_true', help='Run single manual backup')
    
    args = parser.parse_args()
    
    if args.schedule:
        print("Database backup service started...")
        schedule_backup()
    else:  # Default to manual backup if no args provided
        print("Starting manual backup...")
        start_time = datetime.now()
        success = backup_database()
        end_time = datetime.now()
        duration = end_time - start_time
        
        if success:
            print(f"Backup completed in {duration.total_seconds():.2f} seconds")
        else:
            print("Backup failed")