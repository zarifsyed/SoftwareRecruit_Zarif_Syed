import socket

"""
sender.py

The following script takes an array of 100 16-bit integers (signed) over UDP.
The script uses Run-Length encoding techniques to reduce any repeated values in the array,
then it proceeds to send the data as one UDP packet to the intented (target) IP and port.

"""

TARGET_IP = "127.0.0.1"
PORT = 5555

MIN_16INT = -32768
MAX_16INT = 32767

def number_check(numbers):
    """
    Does a series of checks to determine whether the array meets the task requirements:
    - exactly 100 integers in the array
    - each value in the array is an integer
    - each value fits within the set signed 16-bit range
    
    """

    if len(numbers) != 100:
        raise ValueError("The array must contain exactly 100 integers!")

    for n in numbers:
        if not isinstance(n, int):
            raise ValueError("Number must be an integer.")
        
        if n < MIN_16INT or n > MAX_16INT:
            raise ValueError(f"{n} is not within the 16-bit range.")
        
def run_length_encoding(numbers):
    """
    Compresses repeated integers in the array using run-length encoding.

    Example:
    [5,5,5,10,10] --> "5:3,10:2"
    
    """
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
    """
    Creates a check using the sum of the integers between initial sum and sum after data is sent. 
    Result is kept within the 16-bit range using modulo 65536

    """
    return sum(numbers) % 65536

def build_packet(numbers):
    
    """
    Builds the packet, which is to be sent, using the format:

    UDPARRAY1|length|sumcheck|encoded_data

    """

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
     
     # Constructs the final UDP packet using the custom protocol.
     p = build_packet(numbers)

     # Using IPv4, it creates a UDP Socket, which is an endpoint that lets programs send or receive data 
     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

     #In case TARGET_IP is changed to 192.168.1.255 (broadcast), broadcast support is enabled.
     s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

     #Convert the packet (string) into bytes and send it to the target IP and port.
     s.sendto(p.encode(), (TARGET_IP, PORT))

     print("Sent following packet:")
     print(p)

     s.close()

if __name__ == "__main__":
    main()


     
