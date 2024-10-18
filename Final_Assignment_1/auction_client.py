import socket
import json
from datetime import datetime
import encry_decrypt

USERS_FILE = "users.txt"
AUCTIONS_FILE = "auctions.txt"
BIDS_FILE = "bids.txt"

# Global variables
current_user = None


class AuctionClient:
    def __init__(self):
        self.target_ip = "localhost"
        self.target_port = 9191
        self.client_menu()

    def client_runner(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.target_ip, self.target_port))
        return client

    def client_menu(self):
        print("This is the client menu:")
        print("\nAuction Management System Menu")
        user_data = input(
            "1. Register\n 2. Log in\n 3. Create Auction\n 4. Place Bid\n 5. Display Auction Status\n 6. Exit\n"
        )

        if user_data == "1":
            self.register()

        elif user_data == "2":
            self.login()

        elif user_data == "3":
            self.create_auction()

        elif user_data == "4":
            self.place_bid()

        elif user_data == "5":
            self.display_auction_status()

        elif user_data == "6":
            exit()

    def sending_encrypted(self, client, raw_data: str):
        encry = encry_decrypt.A3Encryption()
        decry = encry_decrypt.A3Decryption()
        encrypted_data = encry.start_encryption(raw_data, self.userKey)
        client.send(bytes(encrypted_data, "utf-8"))
        recv_info = client.recv(4096)
        recv_encrypted = recv_info.decode("utf-8")
        print("Received Encrypted Data:", recv_encrypted)

        recv_decrypted = decry.startDecryption(recv_encrypted)
        print("Decrypted Data:", recv_decrypted)

# Function to log in    
    def login(self):
        global current_user
        try:
            print("This is the login Form")
            email = input("Enter your email to login:")
            password = input("Enter your password to login:")
            user_data = load_data(USERS_FILE)
            for user in user_data:
                if user["email"] == email and user["pass1"] == password:
                    current_user = user
                    print("Welcome", user["name"])
                    return
            print("Invalid username or password.")
            
        except Exception as err:
            print(err)
        return

# Function to user register       
    def register(self):
        print("\nThis is the registration option ")
        email = ""
        while True:
            email = input("Enter email for registration:")
            flag = self.email_checking(email)  # 1 or -1

            if flag == 1:
                break
            else:
                print("Email Form Invalid\nTry Again! ")

        print("Email Form Valid ")
        self.reg_for_user(email)

    def email_checking(self, email):
        name_counter = 0
        for i in range(len(email)):
            if email[i] == "@":
                break
            name_counter += 1

        email_name = email[0:name_counter]
        email_form = email[name_counter:]

        name_flag = 0
        email_flag = 0
        for i in range(len(email_name)):
            aChar = email_name[i]
            if (
                (ord(aChar) > 31 and ord(aChar) < 48)
                or (ord(aChar) > 57 and ord(aChar) < 65)
                or (ord(aChar) > 90 and ord(aChar) < 97)
                or (ord(aChar) > 122 and ord(aChar) < 128)
            ):
                name_flag = -1
                break

        domain_form = [
            "@facebook.com",
            "@ncc.com",
            "@mail.ru",
            "@yahoo.com",
            "@outlook.com",
            "@apple.com",
            "@zoho.com",
            "@gmail.com",
        ]

        for i in range(len(domain_form)):
            if domain_form[i] == email_form:
                email_flag = 1
                break

        if name_flag == -1 or email_flag == 0:
            return -1
        else:
            return 1

    def reg_for_user(self, email):
        if self.email_check_inDB_user(email):

            try:
                pass1 = input("Enter candidate password to register:")
                pass2 = input("Enter candidate password Again to register:")

                if pass1 == pass2:
                    print("Password was match!")
                    name = input("Enter candidate name: ")
                    phone = int(input("Enter candidate phone number:"))

                    user_data = {
                        "name": name,
                        "email": email,
                        "pass1": pass1,
                        "phone": phone,
                    }
                    self.final_reg_user(user_data)

                else:
                    print("Password not match:")
                    self.reg_for_user(email)

            except Exception as err:
                print(err)

        else:
            print("Your email was already registered!")
            self.register()

    def email_check_inDB_user(self, email):
        client = self.client_runner()
        data = f"emailcheck {email}"

        client.send(bytes(data, "utf-8"))

        received = client.recv(4096).decode("utf-8")

        print(received)

        if received == "notExist":
            client.close()
            return True
        else:
            client.close()
            return False

    def final_reg_user(self, user_data):
        user_data = (
            f"user_reg {user_data['name']} {user_data['email']} {user_data['pass1']} {user_data['phone']} "
        )

        client = self.client_runner()

        client.send(bytes(user_data, "utf-8"))

        recv = client.recv(4096).decode("utf-8")

        print(recv)

        if recv:
            print("Registration Success!", recv)

        client.close()

# Function to create auction
    def create_auction(self):
        if not current_user:
            print("You need to log in first.")
            return

        title = input("Enter the title of the auction: ")
        description = input("Enter the description of the auction: ")
        end_time_str = input("Enter the end time of the auction (format: YYYY-MM-DD HH:MM): ")

        try:
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format. Please use the format: YYYY-MM-DD HH:MM")
            return

        auctions = load_data(AUCTIONS_FILE)
        auction_id = len(auctions) + 1
        new_auction = {
            "id": auction_id,
            "title": title,
            "description": description,
            "end_time": end_time.strftime("%Y-%m-%d %H:%M"),  # Save as string
            "highest_bidder": None,
            "highest_bid": 0,
        }
        auctions.append(new_auction)
        save_data(auctions, AUCTIONS_FILE)

        print("Auction created successfully!")
    
# Function to place bid    
    def place_bid(self):
        if not current_user:
           print("You need to log in first.")
           return

        auction_id = int(input("Enter the ID of the auction you want to bid on: "))
        bid_amount = float(input("Enter your bid amount: "))

        auctions = load_data(AUCTIONS_FILE)
        for auction in auctions:
            if auction["id"] == auction_id:
               auction_end_time = datetime.strptime(auction["end_time"], "%Y-%m-%d %H:%M")
               if auction_end_time < datetime.now():
                  print("Auction has ended. You cannot bid on this auction.")
                  return

               if bid_amount > auction["highest_bid"]:
                  auction["highest_bid"] = bid_amount
                  auction["highest_bidder"] = current_user["name"]
                  save_data(auctions, AUCTIONS_FILE)

                  bids = load_data(BIDS_FILE)
                  bid_id = len(bids) + 1
                  new_bid = {
                    "id": bid_id,
                    "auction_id": auction_id,
                    "bidder": current_user["name"],
                    "amount": bid_amount,
                    }
                  bids.append(new_bid)
                  save_data(bids, BIDS_FILE)

                  print("Bid placed successfully!")
               else:
                  print("Your bid amount must be higher than the current highest bid.")
                  return

# Function to display auction status
    def display_auction_status(self):
        client = self.client_runner()
        client.send("display_auction_status".encode("utf-8"))
        received_from_server = client.recv(4096)
        if not received_from_server:
            print("Error: Empty response from the server.")
            return

        auction_data: dict = json.loads(received_from_server.decode("utf-8"))

        print("\nAuction Status:")
        for auction in auction_data["auctions"]:
            # Convert the string end_time to a datetime object
            end_time = datetime.strptime(auction["end_time"], "%Y-%m-%d %H:%M")

            # Calculate the time remaining
            time_remaining = end_time - datetime.now()

            print(f"\nAuction ID: {auction['id']}")
            print(f"Title: {auction['title']}")
            print(f"Description: {auction['description']}")
            print(f"Current Highest Bid: {auction['highest_bid']} by {auction['highest_bidder']}")
            print(f"Time Remaining: {time_remaining}")


# Function to load data to a file
def load_data(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return []


# Function to save data to a file
def save_data(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


if __name__ == "__main__":
    auction_client = AuctionClient()

    while True:
        auction_client.client_menu()
