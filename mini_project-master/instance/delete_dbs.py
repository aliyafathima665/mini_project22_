import os
import glob

def delete_all_databases():
    # Patterns to search for database files
    patterns = [
        'database.db',
        'instance/database.db',
        'instance/*.db',
        '*.db'
    ]
    
    deleted_files = []
    
    for pattern in patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                print(f"✅ Deleted: {file_path}")
            except Exception as e:
                print(f"❌ Could not delete {file_path}: {e}")
    
    if not deleted_files:
        print("ℹ️ No database files found to delete")
    else:
        print(f"\n🗑️ Total deleted: {len(deleted_files)} database files")

if __name__ == "__main__":
    print("Searching for database files to delete...")
    delete_all_databases()
    print("\n🎯 Now run: python app.py")