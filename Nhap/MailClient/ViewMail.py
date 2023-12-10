import os
import json
import base64

import Other

# CÁC HÀM XEM MAIL
def menu_view_mail(email_address):
    # Lấy đường dẫn chương trình
    program_path = os.getcwd()
    # Lấy đường dẫn người dùng
    user_path = os.path.join(program_path, email_address)
    
    while True:
        # List ra các folder phân loại mail
        print('------------------------------------------------------------------')
        print("This is folder list in your mailbox: ")
        folders = ["Inbox", "Spam", "Project", "Important", "Work"]
        for i, folder in enumerate(folders, start=1):
            print(f"{i}. {folder}")
        # Chọn xem folder nào   
        folder_choice = input("Enter folder number to view emails (or press Enter to EXIT): ")

        # EXIT
        if folder_choice == '':
            return    
        # List ra các email trong folder đó
        elif folder_choice.isdigit() and 1 <= int(folder_choice) <= len(folders):
            # Lấy tên folder được chọn
            selected_folder = folders[int(folder_choice) - 1]
            # Lấy đường dẫn folder được chọn
            folder_path = os.path.join(user_path, selected_folder)
            while True:
                # Lấy các email trong folder được chọn
                selected_emails = os.listdir(folder_path)

                # List ra các email trong folder được chọn
                print('------------------------------------------------------------------')
                print(f"This is mail list in your {selected_folder} folder: ")
                
                if not selected_emails:
                    print("---No mail in this folder---")
                    break
                else:
                    # List từng email
                    for i, msg_name in enumerate(selected_emails, start=1):
                        # Lấy thông tin để in email
                        email_info = Other.get_email_info(msg_name, email_address)
                        # Gán thông tin vào các biến để xuất ra màn hình
                        email_from = email_info["From"]
                        email_subject = email_info["Subject"]
                        email_status = email_info["Status"]
                        # In email
                        if email_status == "Unread":
                            print(f"{i}. ({email_status}) {email_from}, <{email_subject}>")
                        else:
                            print(f"{i}. {email_from}, <{email_subject}>")
            
                    print('------------------------------------------------------------------')
                    print("Enter 0 to back or press Enter to EXIT.")
                    email_choice = input("Enter email number to view details: ")

                    # EXIT
                    if email_choice == '':
                        return
                    # BACK
                    elif email_choice == '0':
                        break
                    elif email_choice.isdigit() and 1 <= int(email_choice) <= len(selected_emails):
                        msg_name = selected_emails[int(email_choice)-1]
                        email_path = os.path.join(folder_path, msg_name)
                        
                        # Hàm read_mail in mail ra màn hình -> chuyển trạng thái mail sang đã đọc -> trả về số file đính kèm
                        num_attached = read_mail(msg_name, email_address)
                        
                        if num_attached > 0:
                            print('------------------------------------------------------------------')
                            save_choice = input(f"This mail has {num_attached} attached file(s)! Do you want to save? (1. Yes, 2. No): ")
                            if save_choice == '2':
                                break
                            elif save_choice == '1':
                                path_choice = input("Enter path to save attached file (or press Enter to EXIT): ")
                                if path_choice == '':
                                    break
                                save_file(email_path, path_choice)
                            else:
                                print('------------------------------------------------------------------')
                                print("Invalid choice! Please try again!")
                                continue
                    else:
                        print('------------------------------------------------------------------')
                        print("Invalid choice! Please try again!")
                        continue
        else:
            print('------------------------------------------------------------------')
            print("Invalid choice! Please try again!")
            continue
        
def read_mail(msg_name, email_address):
    with open("uidl.json", 'r') as f:
        data = json.load(f)
        email_infos = data[email_address]
    
    for email_info in email_infos:
        if (str(msg_name) == email_info["UniqueID"]):
            # Đổi trạng thái mail sang đã đọc
            if email_info["Status"] == "Unread":
                email_info["Status"] = ""
                with open("uidl.json", 'w') as f:
                    json.dump(data, f, indent=2)
                    
            # In mail ra màn hình
            print("Date: " + email_info["Date"])
            print("From: " + email_info["From"])
            print("TO", end=': ')
            for to in email_info["To"]:
                if (to == email_info["To"][-1]):
                    print(to, end='.')
                else:
                    print (to, end=', ')
            print("\nCc", end=': ')
            for cc in email_info["CC"]:
                if (cc == email_info["CC"][-1]):
                    print(cc, end='.')
                else:
                    print (cc, end=', ')
            print("\nSubject: " + email_info["Subject"])
            print("Body: " + email_info["Body"])
            
            # Trả về số file đính kèm
            return email_info["Num_Attached"]
 
def save_file(input_path, output_path):
    with open(input_path, 'r', encoding='latin1') as f:
        data = f.read()
    
    # Tách file msg thành các dòng
    data_lines = data.split('\r\n')
    # Tìm boundary ở dòng đầu tiên
    boundary = data_lines[0].split('boundary="')[1].split('"\n')[0]
    
    # Tách file msg thành các phần (giữa các boundary)
    parts = data.split(boundary)[1:]
    # Duyệt từng phần để tìm file đính kèm
    for part in parts:
        # Nếu là phần có chứa file đính kèm thì lưu file đính kèm
        if 'Content-Disposition: attachment' in part:
            # Tách tên file đính kèm
            attached_name = part.split('filename="')[1].split('"\n')[0]
            # Tách dữ liệu file đính kèm
            encode_type = part.split('Content-Transfer-Encoding: ')[1].split('\n')[0]
            attached_data = part.split(f'{encode_type}\n\n')[1].split('==\n')[0]
            
            # Lưu file đính kèm
            attached_path = os.path.join(output_path, attached_name)
            with open(attached_path, 'wb') as f:
                f.write(base64.b64decode(attached_data))
            print(f"Attached file saved: {attached_path}")
