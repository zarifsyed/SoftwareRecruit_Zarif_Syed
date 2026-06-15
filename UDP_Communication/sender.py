import socket

TARGET_IP = "127.0.0.1"
PORT = 5555

MIN_16INT = -32768
MAX_16INT = 32767

def number_check(numbers):

    if len(numbers) != 100:
        raise ValueError("The array must contain exactly 100 integers!")

    for n in numbers:
        if not isinstance(n, int):
            raise ValueError("Number must be an integer.")
        
        if n < MIN_16INT or n > MAX_16INT:
            raise ValueError(f"{n} is not within the 16-bit range.")
        
def run_length_encoding(numbers):
    encoded = []

    curr = numbers[0]
    count = 1

    for n in numbers[1:]:
        if n == curr:
            count += 1
        else:
            encoded.append(f"{curr}:{count}")
            curr = n
            count = 1
    
    encoded.append(f"{curr}:{count}")
    return ",".join(encoded)

def sum_check(numbers):
    
    return sum(numbers) % 65536

def build_packet(numbers):


    number_check(numbers)

    encoded_array = run_length_encoding(numbers)
    check_sum = sum_check(numbers)

    return f"UDPARRAY1|{len(numbers)}|{check_sum}|{encoded_array}"

def main():
     numbers = [
        5, 5, 5, 5, 5,
        10, 10, 10, 10, 10,
        15, 15, 15, 15, 15,
        20, 20, 20, 20, 20,
        25, 25, 25, 25, 25,
        30, 30, 30, 30, 30,
        35, 35, 35, 35, 35,
        40, 40, 40, 40, 40,
        45, 45, 45, 45, 45,
        50, 50, 50, 50, 50,
        55, 55, 55, 55, 55,
        60, 60, 60, 60, 60,
        65, 65, 65, 65, 65,
        70, 70, 70, 70, 70,
        75, 75, 75, 75, 75,
        80, 80, 80, 80, 80,
        85, 85, 85, 85, 85,
        90, 90, 90, 90, 90,
        95, 95, 95, 95, 95,
        100, 100, 100, 100, 100
    ]
     
     p = build_packet(numbers)

     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

     s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

     s.sendto(p.encode(), (TARGET_IP, PORT))

     print("Sent following packet:")
     print(p)

     s.close()

if __name__ == "__main__":
    main()


     
