# This is ob program for servertcp and client actions
class Ob:
    def __init__(self):
        print("Starting OB Program!")




    def get_received(self,data):
        print("Received",data)
        return data


    def send_data(self,data):
        print("Sent:",data)
        return data

