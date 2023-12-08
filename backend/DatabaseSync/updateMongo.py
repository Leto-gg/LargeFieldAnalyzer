import os
import shutil
import time
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

print("Loading environment variables...")
mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME')
collection_name = os.getenv('COLLECTION_NAME')
api_token = os.getenv('CUCKOO_API_TOKEN')

print("Environment variables loaded. Connecting to MongoDB...")
client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]
print("Connected to MongoDB.")

headers = {'Authorization': 'Bearer ' + api_token}

def submit_to_cuckoo(file_path):
    print("Submitting file {} to Cuckoo...".format(file_path))
    url = 'http://localhost:8090/tasks/create/file'
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}
        try:
            r = requests.post(url, files=files, headers=headers)
            r.raise_for_status()
            task_id = r.json().get('task_id')
            print("File submitted successfully. Task ID: {}".format(task_id))
            return task_id
        except requests.RequestException as e:
            print("Error submitting file to Cuckoo: {}".format(e))
            return None

def get_cuckoo_report(task_id):
    print("Fetching report for Task ID: {}...".format(task_id))
    if task_id is None:
        print("No task ID provided. Skipping report fetch.")
        return None
    report_url = 'http://localhost:8090/tasks/report/{}'.format(task_id)
    try:
        response = requests.get(report_url, headers=headers)
        response.raise_for_status()
        report = response.json()
        print("Report fetched successfully.")
        print("Full report:", report)  # Debug: print the entire report
        return report
    except requests.RequestException as e:
        print("Error fetching report from Cuckoo: {}".format(e))
        return None

def update_mongo(ipfs_cid, score):
    print("Updating MongoDB for IPFS CID: {} with score: {}".format(ipfs_cid, score))
    if score is not None:
        collection.update_one(
            {'ipfsCID': ipfs_cid},
            {'$set': {'cuckoo_score': score}},
            upsert=True
        )
        print("MongoDB updated successfully.")

def clear_directory(directory):
    if os.path.exists(directory):
        print("Deleting directory and its contents: {}".format(directory))
        try:
            shutil.rmtree(directory)
            print("Deleted directory: {}".format(directory))
        except Exception as e:
            print('Failed to delete {}. Reason: {}'.format(directory, e))
    else:
        print("Directory not found: {}".format(directory))

def process_file(file_path, base_folder):
    print("Processing file: {}".format(file_path))

    # Correctly extracting IPFS CID
    path_parts = file_path.split(os.sep)
    try:
        ipfs_cid_index = path_parts.index('analysisQueue') + 1
        ipfs_cid = path_parts[ipfs_cid_index]
    except (ValueError, IndexError):
        print("Error: Unable to extract IPFS CID from path")
        return

    print("Extracted IPFS CID: {} from path {}".format(ipfs_cid, file_path))

    task_id = submit_to_cuckoo(file_path)
    time.sleep(180)  # Adjust based on expected analysis time

    report = get_cuckoo_report(task_id)
    if report is not None:
        score = report.get('info', {}).get('score', 0)
        update_mongo(ipfs_cid, score)
        clear_directory(os.path.join(base_folder, 'analysisCIDs'))  # Clear analysisCIDs directory
        clear_directory(base_folder)  # Clear analysisQueue directory

def process_folder(folder_path):
    print("Processing folder: {}".format(folder_path))
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path, root)

folder_path = '/home/major-shepard/Documents/LargeFieldDataAnalyzer/backend/DatabaseSync/analysisQueue'
process_folder(folder_path)
