import time
import threading
import ReceiveMail

# Tạo cờ exit
exit_event = threading.Event()

def auto_load_mail(user_info, server_info):
    while not exit_event.is_set():
        ReceiveMail.receive_mail(user_info, server_info)
        time.sleep(server_info["AutoLoad"])
    print("Auto load mail thread is exiting...")

# Thêm hàm để đặt cờ exit
def set_exit_flag():
    exit_event.set()

