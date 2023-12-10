import socket
import json

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
        email_sizes = get_email_size(response)

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
        
def get_email_size(list_response):
    # Lấy các dòng phản hồi LIST từ server
    list_lines = list_response.split('\r\n')
    email_sizes = {}
    
    # Đọc các dòng LIST trừ dòng đầu (+OK) và dòng cuối (.)
    for i, list_line in enumerate(list_lines[1:-2], start=0):
        email_sizes[i] = int(list_line[2:])
    
    return email_sizes    
    
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
            for email_info in data[str(email_address)]:
                if str(email_info["UniqueID"]) == str(uidl_line[2:]):
                    check = True
                    break
                
        # Nếu mail chưa được tải về thì tải về
        if check == False:
            pop3_socket.send('RETR {}\r\n'.format(uidl_line[0]).encode(FORMAT))  
            retr_response = pop3_socket.recv(email_sizes[i]).decode()
            
            # Tách các dòng phản hồi RETR từ server
            retr_lines = retr_response.split('\r\n')
            # Phân tích phản hồi RETR
            email_info = parse_email(retr_lines[1:-2], uidl_line, email_sizes[i])
            # Phân loại mail và lưu mail
            FilterMail.save_email_filtered(email_address, email_info, retr_lines[1:-2])
            
            with open('uidl.json', 'r') as f:
                data = json.load(f)
            data[str(email_address)].append(email_info)
            with open('uidl.json', 'w') as f:
                json.dump(data, f, indent=2)

def parse_email(retr_lines, uidl_line, email_size):
    email_info = {
        "STT": int(uidl_line[0]),
        "UniqueID": str(uidl_line[2:]),
        "Status": "Unread",
        "Size": email_size,
        "From": "",
        "Subject": "",
        "Date": "",
        "To": [],
        "CC": [],
        "Body": "",
        "has_attachment": False,
        "Num_Attached": 0
    }
    
    # Lấy các dữ liệu cơ bản
    for retr_line in retr_lines:
        if retr_line.startswith("From"):
            email_info["From"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("Subject"):
            email_info["Subject"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("Date"):
            email_info["Date"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("To"):
            to_addresses = retr_line.split(":")[1].strip()
            for to_address in to_addresses.split(','):
                email_info["To"].append(to_address.strip())
        elif retr_line.startswith("Cc"):
            cc_addresses = retr_line.split(":")[1].strip()
            for cc_address in cc_addresses.split(','):
                email_info["CC"].append(cc_address.strip())
   
    # Lấy nội dung mail            
    if "multipart" in retr_lines[0]:
        count_empty_line = 0
        count_file = 0
        for retr_line in retr_lines:
            # Kiểm tra mail có file đính kèm hay không
            if retr_line.startswith("Content-Disposition"):
                disposition = retr_line.split(":")[1].strip()
                if "attachment" in disposition:
                    count_file += 1
                    email_info["has_attachment"] = True
                
            # Kiểm tra mail có nội dung hay không
            elif retr_line == '':
                count_empty_line += 1
            if count_empty_line == 2 and retr_line != '':
                email_info["Body"] += (retr_line + '\n')  
        
        email_info["Num_Attached"] = count_file
        return email_info

    else:
        count_empty_line = 0
        for retr_line in retr_lines:
            if retr_line == '':
                count_empty_line += 1
            if count_empty_line == 1 and retr_line != '':
                email_info["Body"] += retr_line
        return email_info 
