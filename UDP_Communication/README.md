# UDP Communication Task

Overview

This folder contains the files for my solution regarding the mandatory UDP communication task, as part of the TorontoMetRobotics Software Team package. The goal of this task was to send an array of 100 16-bit integers from a python script (sender.py) to another (reciever.py).

The following contents:

 - sender.py: constructs (encodes) and sends the UDP packet.
 - reciever.py: receives the packet, decodes, validates, and then prints the sent integer array.

# How the Packet Functions

The sender script creates the packet using the following format:

UDPARRAY1|length|sumcheck|encoded_data

Example:
UDPARRAY1|100|5250|5:5,10:5,15:5,...

What each part of the packet represents:

 1. UDPARRAY1: The header of the packet, which identifies the packet uses the custom UDP integer array format.
 2. length: Stores the expected number of integers in the array.
 3. sumcheck: Stores a check using the sum of the integers. This number will be compared with the actual sum of the integers to determine if data is correct.
 4. encoded_data: Stores the compressed (using Run-Length encoding) integer array.

The | symbol in the packet helps seperate each section. Since commas are used inside the compressed array, using | makes it easier to split and parse the packet.


## Compressing Repeated Integers

To handle any long sequences of the same integer, the script uses run-length encoding to compress the repeated integers.

For instance:
[5, 5, 5, 10, 10]

is converted/encoded to:
"5:3,10:2"

The receiver script will interpret this as 5 appearing 3 times and 10 appearing 2 times. This also helps reduce packet size.

## Data Validation
The sender script checks if:
 - The array contains exactly 100 integers
 - Every value in the array is an integer
 - Every integer is within the signed 16-bit range of -32768 to 32767

The receiver script then validates that:
 - The packet has exactly four sections
 - Header is correct
 - The expected array length matches the actual array length
 - The expected sumcheck value matches the actual sumcheck value

The sum check is calculated using the formula:

	sum(numbers) % 65536

with 65536 (2^16 = 65536) keeping the sum within the range.

## Local Testing

For local testing, both scripts use:
Target IP: 127.0.0.1
Port: 5555

To test the scripts, open two terminals.

The first terminal runs: 

	python reciever.py

The second terminal runs:

	python sender.py

The receiver should then print the received packet, the decoded integers, and validation result.

## Broadcasting to the Network

Since the recruitment packages describes the scenario with a **192.168.1.X**  network where all computers listen on port **5555**,  the sender script can use the broadcast address:

	TARGET_IP = "192.168.1.255"

The sender also enables the support for broadcast with:

	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

However, for my submitted version, I left TARGET_IP as 127.0.0.1 so it can be tested locally without the use of multiple computers.

