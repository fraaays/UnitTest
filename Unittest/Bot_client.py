import socket

def connect_to_server(host, port):
    s = socket.socket()
    s.connect((host, port))
    return s

def get_user_difficulty():
    print("Choose difficulty level:")
    print("1 - Easy (1 to 40)")
    print("2 - Medium (1 to 75)")
    print("3 - Hard (1 to 100)")
    return input("Enter Level of Difficulty (1/2/3): ").strip()

def difficulty_range(difficulty):
    if difficulty == "1":
        return 1, 40
    elif difficulty == "2":
        return 1, 75
    return 1, 100

def choose_difficulty(s, difficulty):
    prompt = s.recv(1024).decode()
    print(prompt)
    s.sendall((difficulty + "\n").encode())
    reply = s.recv(1024).decode()
    print(reply)
    return difficulty_range(difficulty)

def guessing_loop(s, low, high):
    guess = (low + high) // 2
    while True:
        print(f"Trying Guess: {guess}")
        s.sendall(f"{guess}\n".encode())
        reply = s.recv(1024).decode().strip()
        print(reply)

        if "CORRECT!" in reply:
            return guess
        elif "Lower" in reply:
            high = guess - 1
        elif "Higher" in reply:
            low = guess + 1

        guess = (low + high) // 2

def play_game(host="192.168.1.7", port=7777):
    s = connect_to_server(host, port)
    difficulty = get_user_difficulty()
    low, high = choose_difficulty(s, difficulty)
    result = guessing_loop(s, low, high)
    s.close()
    print(f"Guessed correctly: {result}")
    return result

if __name__ == "__main__":
    play_game()
