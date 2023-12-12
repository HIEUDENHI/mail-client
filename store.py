import os
import time
import random
import string
import json
import re
from json.decoder import JSONDecodeError


def update_config(username, password, mail_server, smtp_port, pop3_port, autoload):
    config_data = {
        "General": {
            "Username": username,
            "Password": password,
            "MailServer": mail_server,
            "SMTP": smtp_port,
            "POP3": pop3_port,
            "Autoload": autoload
        },
        "Filter": {
            "From": [
                "ahihi@testing.com",
                "ahuu@testing.com"
            ],
            "ToFolder_From": "Project",
            "Subject": [
                "urgent",
                "ASAP"
            ],
            "ToFolder_Subject": "Important",
            "Content": [
                "report",
                "meeting"
            ],
            "ToFolder_Content": "Work",
            "Spam": [
                "virus",
                "hack",
                "crack"
            ],
            "ToFolder_Spam": "Spam"
        }
    }

    with open("D:/Desktop/client/config.json", 'w') as file:
        json.dump(config_data, file, indent=4)


def load_config():
    with open("D:/Desktop/client/config.json", 'r') as file:
        config = json.load(file)
    return config

def generate_unique_filename(prefix, extension):
    timestamp = time.strftime("%Y%m%d%H%M%S")
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    unique_filename = f"{prefix}_{timestamp}_{random_string}.{extension}"
    return unique_filename

def createFile(msg, file_path, file_name,config):
    data = {}
    data["From"] = msg["From"]
    data["To"] = msg["To"] if msg["To"] is not None else ""
    data["Cc"] = msg["Cc"] if msg["Cc"] is not None else ""
    data["Subject"] = msg["Subject"]
    data["Content"]=""
    if msg.is_multipart():
        attachments = []

        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                data["Content"] = part.get_payload()

            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            # Download the attachment
            filename = os.path.basename(part.get_filename())
            if filename:
                attachment = {
                "Filename": filename,
                "Data": part.get_payload()
            }
                attachments.append(attachment)
        data["Attachment"] = attachments
    else:
        data["Content"] = msg.get_payload()
        data["Attachment"]=[]    
    match = re.search(r'<([^>]+)>', data["From"])
    if match.group(1) in config["Filter"]["From"]:
        file_path += "/" + config["Filter"]["ToFolder_From"]  
    elif any(keyword in data["Subject"] for keyword in config["Filter"]["Subject"]):
        file_path += "/" + config["Filter"]["ToFolder_Subject"]
    elif any(keyword in data["Content"] for keyword in config["Filter"]["Content"]):
        file_path += "/" + config["Filter"]["ToFolder_Content"]
    elif any(keyword in data["Subject"] or keyword in data["Content"] for keyword in config["Filter"]["Spam"]):
        file_path += "/" + config["Filter"]["ToFolder_Spam"]
    else:
        file_path += "/Inbox"


    # ... (similar code for other rules)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    summary_file_path=file_path+"/summary.json"
    file_path += "/" + file_name   # Use .json extension for JSON files
    with open(file_path, 'w') as file:
        json.dump(data, file)

    update_summary_file(file_name, data["From"], data["Subject"], summary_file_path)


def update_summary_file(msg_file_name, sender_name, subject, summary_file_path):
    summary_data = []

    # Load existing summary data if the file exists
    if os.path.exists(summary_file_path):
        try:
            with open(summary_file_path, 'r') as summary_file:
                summary_data = json.load(summary_file)
        except JSONDecodeError:
            # Handle the case when the file is empty or contains invalid JSON
            summary_data = []
    else:
        # Create a new summary_data list if the file doesn't exist
        summary_data = []
    new_data = {
        "fileName": msg_file_name,
        "sender": sender_name,
        "subject": subject,
        "isRead":False
    }
    summary_data.append(new_data)

    # Save the updated summary data
    with open(summary_file_path, 'w') as summary_file:
        json.dump(summary_data, summary_file)


def update_mail_status(file_path, selectedMail):
    # Đọc dữ liệu từ file JSON
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Tìm kiếm mail cụ thể trong mảng
    for mail in data:
        if mail["fileName"] == selectedMail["fileName"]:
            # Cập nhật trạng thái isRead thành True
            mail['isRead'] = True

    # Ghi lại dữ liệu đã được cập nhật vào file JSON
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)