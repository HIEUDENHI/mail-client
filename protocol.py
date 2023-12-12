from store import createFile
from store import generate_unique_filename
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import base64
from email import encoders
from email import message_from_bytes
from store import load_config
import os
import re





def send_email(user_name, to_emails, cc_emails, bcc_emails, subject, message, smtp_server, smtp_port, email, attachment_paths):
    # Create a socket object
    smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the SMTP server
    smtp_socket.connect((smtp_server, smtp_port))

    # Receive the initial greeting from the server
    response = smtp_socket.recv(1024).decode()
    if response[:3] != '220':
        print('220 reply not received from server')
        return

    # Send EHLO command
    smtp_socket.send(f"EHLO [{smtp_server}]\r\n".encode())
    response = smtp_socket.recv(1024).decode()
    if response[:3] != '250':
        print('250 reply not received from server')
        return

    # Send MAIL FROM command
    smtp_socket.send(f"MAIL FROM: <{email}>\r\n".encode())
    response = smtp_socket.recv(1024).decode()

    # Split the recipient lists into individual email addresses
    to_email_list = to_emails.split(", ")    
    
    cc_email_list = cc_emails.split(", ")
    bcc_email_list = bcc_emails.split(", ")

    # Combine all recipient lists into a single list
    receiver_list = to_email_list + cc_email_list + bcc_email_list

    # Send RCPT TO commands for each recipient
    for recipient in receiver_list:
        smtp_socket.send(f"RCPT TO:<{recipient}>\r\n".encode())
        response = smtp_socket.recv(1024).decode()

    # Send DATA command to indicate start of message body
    smtp_socket.send('DATA\r\n'.encode())
    response = smtp_socket.recv(1024).decode()
    
    
    
    msg = MIMEMultipart()
    msg['From']=user_name
    msg['To'] =to_emails
    msg['Cc']=cc_emails
    msg['Subject']=subject
    
    msg.attach(MIMEText(message,'plain'))
    
    for attachment_path in attachment_paths:
            
        with open(attachment_path, "rb") as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path)
        msg.attach(p)
    text = msg.as_string().encode()
    smtp_socket.send(text)
    smtp_socket.send('\r\n.\r\n'.encode())
    # Send QUIT command to close the connection
    smtp_socket.send('QUIT\r\n'.encode())
    response = smtp_socket.recv(1024).decode()
    

    # Close the socket connection
    smtp_socket.close()



def receive_email(user_name,password,pop3_server,port,config):
    pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pop3_socket.connect((pop3_server,port))
    response=pop3_socket.recv(1024).decode()
    pop3_socket.send("CAPA\r\n".encode())
    response=pop3_socket.recv(1024).decode()
    pop3_socket.send(f"USER {user_name}\r\n".encode())
    response=pop3_socket.recv(1024).decode()
    pop3_socket.send(f"PASS {password}\r\n".encode())
    response=pop3_socket.recv(1024).decode()
    pop3_socket.send("STAT\r\n".encode())
    response=pop3_socket.recv(1024).decode()
    if(not response.startswith("+OK 0 0")):
        pop3_socket.send("LIST\r\n".encode())
        response=pop3_socket.recv(1024).decode()    
        pop3_socket.send("UIDL\r\n".encode())
        response=pop3_socket.recv(1024).decode()
        uidl_list = response.split('\r\n')[1:-2]
        mail_number, mail_uidl = uidl_list[0].split()
        pop3_socket.send(f"RETR {mail_number}\r\n".encode())
        message_content = b''
        while True:
            response = pop3_socket.recv(4096)
            if not response:
                break
            message_content += response

                # Check for the end of the message
            if b'\r\n.\r\n' in message_content[-5:]:
                break
                # Parse the email content
        response_parts = message_content.split(b'\n', 1)
        msg = message_from_bytes(response_parts[1])
        match = re.search(r'<([^>]+)>', config["General"]["Username"])
        filePath=f"D:/Desktop/client/database/{match.group(1)}"
        fileName=generate_unique_filename("msg","json")
        createFile(msg,filePath,fileName,config)
        pop3_socket.send(f"DELE {mail_number}\r\n".encode())
        response=pop3_socket.recv(1024).decode()
    
        
    
    
    quit_command = "QUIT\r\n"
    pop3_socket.sendall(quit_command.encode())
    response = pop3_socket.recv(1024).decode()

