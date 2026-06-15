import socket
"""
reciever.py

This script actively listens for a UDP packet on localhost port 5555.
Once it receives a packet, it decodes the packet, reconstructs the original integer array,
checks the length and sum (same as sender.py), then prints the integers.

"""
RECEIVER_IP = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096

def sum_check(numbers):
    return sum(numbers) % 65536

def decode_values(encoded_data):
    """
    Decodes the encoded data (which used run-length encoding) back into the original integer array.

    Example:
    "5:3,10:2" --> [5, 5, 5, 10, 10]
    
    """
    nums = []
    
    pairs = encoded_data.split(",")

    for p in pairs:
        val_str, count_str = p.split(":")
        val = int(val_str)
        count = int(count_str)

        for _ in range(count):
            nums.append(val)

    return nums

def parse_packet(packet):
    """
    Packet Format:

    UDPARRAY1|length|sumcheck|encoded_data
    
    Splits the received packet into four sections:
    header, length, sumcheck, and the encoded data.

    It checks if the packet has the correct header, array length, and matching sumcheck.
    
    """

    parts = packet.split("|")

    if len(parts) != 4:
        raise ValueError("Format of the packet is incorrect.")
    
    header = parts[0]
    length = int(parts[1])
    sumcheck = int(parts[2])
    encoded_data = parts[3]

    if header != "UDPARRAY1":
        raise ValueError("Header is incorrect.")
    
    numbers = decode_values(encoded_data)

    if len(numbers) != length:
        raise ValueError("Array length does not match the length of packet.")
    
    actual_sumcheck = sum_check(numbers)

    if actual_sumcheck != sumcheck:
        raise ValueError("Sum check does not match. Data is incorrect/corrupted.")
    
    return numbers

def main():
    
    #Using IPv4, creates a socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #Binds the receiver to the localhost and port 5555 so it is able to listen for packets.
    s.bind((RECEIVER_IP, PORT))

    print(f"Receiver is currently listening on {RECEIVER_IP}:{PORT}")

    while True:
        #Wait for a UDP Packet to be sent. recvfrom returns the data and sender address.
        data, address = s.recvfrom(BUFFER_SIZE)

        #Convert the initial bytes back into a string.
        packet = data.decode()

        print("\n Packet received from:", address)
        print("Packet:", packet)

        try:
            numbers = parse_packet(packet)

            print("\nIntegers:")
            print(numbers)

            print("\n Integers Validated.")
            print("Number of Integers:", len(numbers))

        except ValueError as error:
            print("\n Validation Failed.")
            print("Error:", error)

if __name__ == "__main__":
    main()