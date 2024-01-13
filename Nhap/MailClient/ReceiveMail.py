import socket
import json
from tempfile import tempdir

import Other
import FilterMail

from SendMail import FORMAT

# CÁC HÀM NHẬN MAIL
def receive_mail(user_info, server_info):
    global FORMAT
    try:
        # Mở kết nối socket
        pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pop3_socket.connect((server_info["MailServer"], server_info["POP3"]))
        # Nhận thông tin lời chào từ server
        welcome_message = pop3_socket.recv(1024).decode()
        
        # SEND CAPA
        pop3_socket.send(b'CAPA\r\n')
        pop3_socket.recv(1024).decode()

        # Tách email từ username
        email_address = Other.extract_email_address(user_info['Username'])
        # SEND USER
        pop3_socket.send(f'USER {email_address}\r\n'.encode())
        pop3_socket.recv(1024).decode()

        # SEND PASS
        pop3_socket.send(f'PASS {user_info["Password"]}\r\n'.encode())
        pop3_socket.recv(1024).decode()
    
        # SEND STAT
        pop3_socket.send(b'STAT\r\n')
        ## TRẢ VỀ: +OK x y (x là số mail, y là tổng kích thước theo byte)
        response = pop3_socket.recv(1024).decode(FORMAT)
    
        # SEND LIST
        pop3_socket.send(b'LIST\r\n')
        ## TRẢ VỀ:
        # +OK
        # Thứ tự mail _ size mail
        # .
        response = pop3_socket.recv(2048).decode(FORMAT)
    
        # Lấy dung lượng các mail
        email_sizes = Other.get_email_size(response)

        # SEND UIDL
        pop3_socket.send(b'UIDL\r\n')
        ## TRẢ VỀ: 
        # +OK
        # Thứ tự mail _ <mã độc nhất>.msg
        # .
        response = pop3_socket.recv(2048).decode(FORMAT)
    
        # Tải mail về máy
        download_mail(pop3_socket, response, email_address, email_sizes)

    except Exception as e:
        # Kiểm tra xem pop3_socket có tồn tại không
        if pop3_socket:
            try:
                # Đóng kết nối socket nếu chưa được đóng
                pop3_socket.send(b'QUIT\r\n')
                pop3_socket.close()
            except Exception as close_error:
                    # Xử lý lỗi khi đóng kết nối socket
                print(f"Error closing socket: {close_error}")

        print(f"Error: {e}")
        print("Disconnected from SERVER!")   
    
def download_mail(pop3_socket, uidl_response, email_address, email_sizes):
    global FORMAT
    # Lấy các dòng phản hồi UIDL từ server
    uidl_lines = uidl_response.split('\r\n')
    
    # Đọc các dòng UIDL trừ dòng đầu (+OK) và dòng cuối (.)
    for i, uidl_line in enumerate(uidl_lines[1:-2], start=0):
        check = False
        with open('uidl.json', 'r') as f:
            data = json.load(f)

            # Chạy vòng lặp kiểm tra xem mail đã được tải về chưa
            tmp1 = uidl_line.split(" ")[1].strip()
            for email_info in data[str(email_address)]:
                if str(email_info["UniqueID"]) == str(tmp1):
                    check = True
                    break
                
        # Nếu mail chưa được tải về thì tải về
        if check == False:
            tmp2 = uidl_line.split(" ")[0].strip()
            pop3_socket.send('RETR {}\r\n'.format(int(tmp2)).encode(FORMAT))  
            retr_response = pop3_socket.recv(int(1e6)).decode()
            
            # Tách các dòng phản hồi RETR từ server
            retr_lines = retr_response.split('\r\n')
            # Phân tích phản hồi RETR
            email_info = Other.parse_email(retr_lines[1:-2], uidl_line, email_sizes[i])
            # Phân loại mail và lưu mail
            FilterMail.save_email_filtered(email_address, email_info, retr_lines[1:-2])
            
            with open('uidl.json', 'r') as f:
                data = json.load(f)
            data[str(email_address)].append(email_info)
            with open('uidl.json', 'w') as f:
                json.dump(data, f, indent=2) 
