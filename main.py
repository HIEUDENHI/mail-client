from protocol import receive_email
from console import send_email_console, view_emails
from store import load_config
import time
import asyncio
import re
from store import update_config


async def task1(config):
    while True:
        print("Vui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Thoát")

        # Use asyncio.to_thread to run input in a separate thread
        choice = await asyncio.to_thread(input, "Bạn chọn: ")
        if choice == '1':
            await send_email_console(config)
        elif choice == '2':
            await view_emails(config)
        elif choice == '3':
            print("Thoát chương trình")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại")


async def task2(config):
    match = re.search(r'<([^>]+)>', config["General"]["Username"])
    while True:
        receive_email(match.group(1), config["General"]["Password"], config["General"]["MailServer"],
                       config["General"]["POP3"], config)
        await asyncio.sleep(int(config["General"]["Autoload"]))


async def load_config_async():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, load_config)


async def main():
    config = await load_config_async()
    await asyncio.gather(task2(config), task1(config))


if __name__ == "__main__":
    # username=input("Nhap username: ")
    # password=input("Nhap password: ")
    # mailserver=input("Nhap mail server: ")
    # SMTPport=input("Nhap SMTP port: ")
    # POP3port=input("Nhap POP3 port: ")
    # autoload=input("Nhap auto load: ")
    # update_config(username,password,mailserver,SMTPport,POP3port,autoload)
    asyncio.run(main())
