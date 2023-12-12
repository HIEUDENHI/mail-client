from protocol import send_email
import json
import os
import re
import base64
import asyncio
from store import update_mail_status
from store import load_config

def show_summary(folder,summary_data):
    print(f"Đây là danh sách email trong {folder} folder")
    for idx, file_info in enumerate(summary_data, start=1):
        if not file_info["isRead"]:
            print(f"{idx}. (chưa đọc) <{file_info['sender']}>, {file_info['subject']}")
        else:
            print(f"{idx}. <{file_info['sender']}>, {file_info['subject']}")
    

async def show_email(folder,config):
    match = re.search(r'<([^>]+)>', config["General"]["Username"])
    summary_file = f"D:/Desktop/client/database/{match.group(1)}/{folder}/summary.json"
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as summary_file1:
            summary_data = json.load(summary_file1)
            
    else:
        print("Chưa có mail để show")
        return
    show_summary(folder,summary_data)
    while True: 
        with open(summary_file, 'r') as summary_file1:
            summary_data = json.load(summary_file1)
        choice =await asyncio.to_thread(input, "Bạn muốn đọc Email thứ mấy? (nhấn enter để thoát hoặc nhấn 0 để xem lại danh sách email): ")
        if choice.isdigit():
            choice = int(choice)
            if choice > 0 and choice <= len(summary_data):
            # Xử lý khi người dùng chọn một email cụ thể
                selected_email = summary_data[choice - 1]
                update_mail_status(summary_file,selected_email)
                print(f"Bạn đã chọn đọc Email thứ {choice}.")
                
                dataFile=f"D:/Desktop/client/database/{match.group(1)}/{folder}/"+selected_email["fileName"]
                with open(dataFile, 'r') as file:
                    mail_data = json.load(file)
                print(f"To: {mail_data['To']}")
                print(f"Cc: {mail_data['Cc']}")
                print(f"Subject: {mail_data['Subject']}")
                print(mail_data['Content'])
                if mail_data["Attachment"]:
                    print("Trong email này có attached file.")
                    save_attachment = await asyncio.to_thread(input, "Bạn có muốn lưu không? (có/không): ")

                    if save_attachment.lower() == "có":
                        save_path = await asyncio.to_thread(input, "Cho biết đường dẫn bạn muốn lưu: ")
                        while not os.path.exists(save_path):
                            print("Đường dẫn không tồn tại. Nhập đường dẫn khác")
                            save_path = await asyncio.to_thread(input, "Cho biết đường dẫn bạn muốn lưu: ")

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
                os.system('cls')
                show_summary(folder,summary_data)
            else:
                print("Lựa chọn không hợp lệ.")
        elif choice=="":
            os.system('cls')
            break  
        
    
    
    
    
async def view_emails(config):
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

    folder_choice = await asyncio.to_thread(input, "Bạn muốn xem email trong folder nào: ")

    if folder_choice in folder_names:
        await show_email(folder_names[folder_choice],config)
    elif not folder_choice:
        return
    else:
        print("Lựa chọn không hợp lệ.")
        



def checkFileSize(filePath):
    file_size = os.path.getsize(filePath)
    if file_size<3*1024*1024:
        return True
    return False


async def send_email_console(config):
    print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)")
    to =await asyncio.to_thread(input, "To: ")
    cc = await asyncio.to_thread(input, "Cc: ")
    bcc = await asyncio.to_thread(input, "Bcc: ")
    subject = await asyncio.to_thread(input, "Subject: ")
    content = await asyncio.to_thread(input, "Content: ")
    attachments=[]
    attach_choice = await asyncio.to_thread(input, "Có gửi kèm file (1. có, 2. không): ")
    if attach_choice == '1':
        num_files = int(await asyncio.to_thread(input, "Số lượng file muốn gửi: "))
        for i in range(num_files):
            file_path=await asyncio.to_thread(input, f"Cho biết đường dẫn file thứ {i+1}: ")
            
            while not os.path.exists(file_path):
                print("Đường dẫn file không tồn tại. Nhập đường dẫn file khác")
                file_path=await asyncio.to_thread(input, f"Cho biết đường dẫn file thứ {i+1}: ")
            while not checkFileSize(file_path):
                print("Dung lượng file hơn 3MB. Nhập đường dẫn file khác")
                file_path=await asyncio.to_thread(input, f"Cho biết đường dẫn file thứ {i+1}: ")


            attachments.append(file_path)

    match = re.search(r'<([^>]+)>', config["General"]["Username"])
        # Code xử lý việc gửi email sẽ được thêm vào ở đây
    send_email(config["General"]["Username"], to, cc, bcc, subject, content, config["General"]["MailServer"], config["General"]["SMTP"], match.group(1), attachments)
    print("\nĐã gửi email thành công\n")
    os.system('cls')

