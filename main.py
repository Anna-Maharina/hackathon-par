import requests
import json
import time
import os
import argparse



def trigger_file_uploading(file_name: str):
    KEY = os.environ["KEY"]
    headers = {'X-API-Key': KEY}

    knowledge_base_id = "48632512-c03c-4293-ae24-835345efb0ad"
    link = requests.get(
        "https://staging.docs.bynesoft.com/api/connectors/local/s3-upload-links",
        headers=headers,
        params={"kb": knowledge_base_id, "fileName": [file_name]},
    )
    link_uri = link.json()[file_name]

    mime_headers = {"Content-Type": "text/plain"}
    upload = requests.put(link_uri, data=open(file_name, "rb"), headers=mime_headers)

    job_id = requests.post(f"https://staging.docs.bynesoft.com/api/knowledge-base/{knowledge_base_id}/jobs", headers=headers).json()
    requests.put(f"https://staging.docs.bynesoft.com/api/knowledge-base/{knowledge_base_id}/jobs/{job_id}",
                headers=headers,
                data=json.dumps(
                        [
                            {
                                "fileName": file_name,
                                "lastModified": "Wed Jul 3 2024",
                                "connector": "local",
                            }
                        ]
                        ),
    )
    trigger_status = requests.post(f"https://staging.docs.bynesoft.com/api/knowledge-base/{knowledge_base_id}/jobs/{job_id}/trigger", headers=headers).json()
    print(trigger_status)

    while True:
        response = requests.get(
        f"https://staging.docs.bynesoft.com/api/knowledge-base/{knowledge_base_id}/jobs/{job_id}",
        headers=headers).json()
        print(response['status'])
        if response['status'] == 'FINISHED':
            break
        time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description='File processing script')
    parser.add_argument('file_name', type=str, 
                            help='Path to the input file to be processed')
    parser.add_argument('-v', '--verbose', action='store_true', 
                            help='Enable verbose output')
    args = parser.parse_args()
        
    if args.verbose:
        print(f"Attempting to process file: {args.file_name}")
        
    trigger_file_uploading(args.file_name)

if __name__ == "__main__":
    main()
