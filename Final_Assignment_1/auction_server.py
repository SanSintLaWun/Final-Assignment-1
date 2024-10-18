import socket
import json
from datetime import datetime

USERS_FILE = "users.txt"
AUCTIONS_FILE = "auctions.txt"
BIDS_FILE = "bids.txt"

# Function to load data from a file
def load_data(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        data = []
    return data

# Function to save data to a file
def save_data(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

def handle_client(client_socket):
    
    request = client_socket.recv(4096).decode("utf-8").split()
    print("Received request:", request)
    action = request[0]

    if action == "login":
        email, password = request[1], request[2]
        user_data = load_data(USERS_FILE)
        response = {"status": "fail"}
        for user in user_data:
            if user["email"] == email and user["pass1"] == password:
                response = {"status": "success", "user_data": user}
                break
        client_socket.send(json.dumps(response).encode("utf-8"))

    elif action == "emailcheck":
        email = request[1]
        user_data = load_data(USERS_FILE)
        response = "notExist" if not any(user["email"] == email for user in user_data) else "exist"
        client_socket.send(response.encode("utf-8"))

# Function to user register
    elif action == "user_reg":
        name, email, password, phone = request[1], request[2], request[3], request[4]
        user_data = load_data(USERS_FILE)
        new_user = {
            "name": name,
            "email": email,
            "pass1": password,
            "phone": phone,
        }
        user_data.append(new_user)
        save_data(user_data, USERS_FILE)
        client_socket.send("Registration Success!".encode("utf-8"))

# Function to create auction
    elif action == "create_auction":
        auction_id, title, description, end_time_str = request[1], request[2], request[3], request[4]
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        auctions = load_data(AUCTIONS_FILE)
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
        response = {"status": "success", "auction_data": new_auction}
        client_socket.send(json.dumps(response).encode("utf-8"))  # Convert the response to JSON before sending

# Function to place bid      
    elif action == "place_bid":
        bid_id, auction_id, bidder, amount = request[1], request[2], request[3], request[4]
        auctions = load_data(AUCTIONS_FILE)
        for auction in auctions:
            if auction["id"] == auction_id:
                if auction["end_time"] < datetime.now():
                    response = {"status": "fail", "message": "Auction has ended."}
                elif float(amount) > auctions["highest_bid"]:
                    auction["highest_bid"] = float(amount)
                    auction["highest_bidder"] = bidder
                    save_data(auctions, AUCTIONS_FILE)

                    bids = load_data(BIDS_FILE)
                    new_bid = {
                        "id": bid_id,
                        "auction_id": auction_id,
                        "bidder": bidder,
                        "amount": float(amount),
                    }
                    bids.append(new_bid)
                    save_data(bids, BIDS_FILE)

                    response = {"status": "success", "message": "Bid placed successfully!"}
                else:
                    response = {"status": "fail", "message": "Your bid amount must be higher than the current highest bid."}
                break
        else:
            response = {"status": "fail", "message": "Auction not found."}
        client_socket.send(json.dumps(response).encode("utf-8"))

    elif action == "display_auction_status":
        auctions = load_data(AUCTIONS_FILE)
        response = {"status": "success", "auctions": auctions}
        client_socket.send(json.dumps(response).encode("utf-8"))
    

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9191))
    server.listen(5)

    print("Server is listening for connections...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr} has been established!")
        handle_client(client_socket)

if __name__ == "__main__":
    start_server()
