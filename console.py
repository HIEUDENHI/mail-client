from protocol import send_email
import json
import os
import re
import base64
from store import update_mail_status
from store import load_config
def show_email(folder,config):
    match = re.search(r'<([^>]+)>', config["General"]["Username"])
    summary_file = f"D:/Desktop/client/{match.group(1)}/{folder}/summary.json"
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as summary_file1:
            print(f"Đây là danh sách email trong {folder} folder")
            summary_data = json.load(summary_file1)
    else:
        print("Chưa có mail để show")
        return
    while True: 
        for idx, file_info in enumerate(summary_data, start=1):
            if not file_info["isRead"]:
                print(f"{idx}. (chưa đọc) <{file_info['sender']}>, {file_info['subject']}")
            else:
                print(f"{idx}. <{file_info['sender']}>, {file_info['subject']}")
        choice = input("Bạn muốn đọc Email thứ mấy? (nhấn enter để thoát hoặc nhấn 0 để xem lại danh sách email): ")

        if choice.isdigit():
            choice = int(choice)
            if choice > 0 and choice <= len(summary_data):
            # Xử lý khi người dùng chọn một email cụ thể
                selected_email = summary_data[choice - 1]
                update_mail_status(summary_file,selected_email)
                print(f"Bạn đã chọn đọc Email thứ {choice}.")
                
                dataFile=f"D:/Desktop/client/{match.group(1)}/{folder}/"+selected_email["fileName"]
                with open(dataFile, 'r') as file:
                    mail_data = json.load(file)
                print(f"To: {mail_data['To']}")
                print(f"Cc: {mail_data['Cc']}")
                print(f"Subject: {mail_data['Subject']}")
                print(mail_data['Content'])
                if mail_data["Attachment"]:
                    print("Trong email này có attached file.")
                    save_attachment = input("Bạn có muốn lưu không? (có/không): ")

                    if save_attachment.lower() == "có":
                        save_path = input("Cho biết đường dẫn bạn muốn lưu: ")

                        for attachment in mail_data["Attachment"]:
                            filename = attachment["Filename"]
                            encoded_attachment = attachment["Data"]
                            decoded_attachment = base64.b64decode(encoded_attachment)
                            full_save_path = save_path + "\\" + filename

                            with open(full_save_path, 'wb') as dest_file:
                                dest_file.write(decoded_attachment)

                            print(f"File đính kèm {filename} đã được lưu tại: {full_save_path}")

                    else:
                        print("Không lưu file đính kèm.")
                      # Thoát khỏi vòng lặp while khi đã chọn một email
            elif choice == 0:
            # Người dùng muốn xem lại danh sách email, tiếp tục lặp
                continue
            else:
                print("Lựa chọn không hợp lệ.")
        else:
            print("Đã thoát khỏi chương trình.")
            break  # Thoát khỏi vòng lặp while khi người dùng nhấn Enter để thoát
        
    
    
    
    
def view_emails(config):
    folder_names = {
        '1': 'Inbox',
        '2': 'Project',
        '3': 'Important',
        '4': 'Work',
        '5': 'Spam'
    }

    print("Đây là danh sách các folder trong mailbox của bạn:")
    for key, value in folder_names.items():
        print(f"{key}. {value}")

    folder_choice = input("Bạn muốn xem email trong folder nào: ")

    if folder_choice in folder_names:
        show_email(folder_names[folder_choice],config)
    elif not folder_choice:
        return
    else:
        print("Lựa chọn không hợp lệ.")
        



def checkFileSize(filePath):
    file_size = os.path.getsize(filePath)
    if file_size<3*1024*1024:
        return True
    return False


def send_email_console(config):
    print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)")
    to = input("To: ")
    cc = input("CC: ")
    bcc = input("BCC: ")
    subject = input("Subject: ")
    content = input("Content: ")
    attachments=[]
    attach_choice = input("Có gửi kèm file (1. có, 2. không): ")
    if attach_choice == '1':
        num_files = int(input("Số lượng file muốn gửi: "))
        for i in range(num_files):
            file_path=input(f"Cho biết đường dẫn file thứ {i+1}: ")
            while not os.path.exists(file_path):
                print("Đường dẫn file không tồn tại. Nhập đường dẫn file khác")
                file_path=input(f"Cho biết đường dẫn file thứ {i+1}: ")

            while not checkFileSize(file_path):
                print("Dung lượng file hơn 3MB. Nhập đường dẫn file khác")
                file_path=input(f"Cho biết đường dẫn file thứ {i+1}: ")

            attachments.append(file_path)

    match = re.search(r'<([^>]+)>', config["General"]["Username"])
        # Code xử lý việc gửi email sẽ được thêm vào ở đây
    send_email(config["General"]["Username"], to, cc, bcc, subject, content, config["General"]["MailServer"], config["General"]["SMTP"], match.group(1), attachments)
    print("\nĐã gửi email thành công\n")

