import time
import ReceiveMail

exit_flag = False

# HÀM AUTO LOAD MAIL SAU THỜI GIAN NHẤT ĐINH CHO TRƯỚC
def auto_load_mail(user_info, server_info):
    global exit_flag
    while not exit_flag:
        ReceiveMail.receive_mail(user_info, server_info)
        time.sleep(server_info["AutoLoad"])
