import socket
from requests import get
import sys
import select
import struct
import os
import math

# Constants
PACKET_SIZE = 32768 # Affects speed & must be consistent in both partner's program (If you modify it, you have to do it in your partner's program too)
PACKER = struct.Struct('256s Q') # String for filename, and unsigned long long for file size in bytes
PROGRAM_NAME = "Simple Share Python"
VERSION = "1.0.0.1"
GITHUB_LINK = "https://github.com/domirick/simplesharepython"
AUTHOR = "Domirick"
PROGRESS_BAR_WIDTH = 40

# Global variables
mode = 0 # 0 for receiving, and 1 for sending
server_ip = ""
server_port = 32700
fname = "" # The file that sender is sending, or the filename as that receiver is receiving
ssp_name = "ssp.py" # Will change for actual name if renamed
use_ipify_api = True
internal_ip = ""

def get_help():
    print("Usage when sending: ssp.py send -d IP -f FILE [-p PORT_NUMBER]")
    print("Usage when receiving: ssp.py receive [-p PORT_NUMBER] [--no-api]")
    print("Usage when getting information: ssp.py [--help] [--version]")
    print("")
    print("Sending arguments:")
    print("  -d, -ip IP_ADDRESS \t\tRequired, the receiver's IP address")
    print("  -f FILE_LOCATION \t\tRequired, the file to be sent")
    print("  -p, -port PORT_NUMBER \tOptional, default is 32700 (have to match with the receiver's")
    print("")
    print("Receiving arguments:")
    print("  -p, -port PORT_NUMBER \tListening port, default is 32700 (you should open it)")
    print("  --no-api \t\t\tDo not use ipify API to get the external IP address")
    print("")
    print("Standalone arguments:")
    print("  -h, --help \t\t\tShow this help message and exit")
    print("  -v, --version \t\tShow informations about the program, and the version then exit")

def get_version():
    print(PROGRAM_NAME)
    print("Version: "+VERSION)
    print("Github: "+GITHUB_LINK)
    print("Author: "+AUTHOR)

# This function check intersect of two arrays of switches, and returs the element of the intersection
def check_opted(opts,triggers):
    for trigger in triggers:
        if trigger in opts:
            return trigger
    return False

def parse_arguments():
    # Get filename for instruction messages
    global server_ip, server_port, fname, ssp_name, mode, use_ipify_api
    ssp_name = sys.argv[0].split('\\')[-1].split('/')[-1] # Both \ and / if it's running in Windows or in Linux

    # Check info args
    if check_opted(sys.argv[1:],["-h","-help","--help"]):
        get_help()
        sys.exit()
    if check_opted(sys.argv[1:],["-v","-version","--version"]):
        get_version()
        sys.exit()

    # Check mode (sender or receiver)
    if len(sys.argv) < 2:
        print(f"Usage: {ssp_name} (send | receive) <args>...")
        raise SystemExit(f"For instructions use: {ssp_name} --help")
    if sys.argv[1] == "send":
        mode = 1

    dopts = [opt for opt in sys.argv[2:] if opt.startswith("--")]
    opts = [opt for opt in sys.argv[2:] if opt.startswith("-") and not opt in dopts]
    args = [arg for arg in sys.argv[2:] if not arg.startswith("-")]

    # Sender mode arguments
    if mode:
        if check_opted(opts,["-d","-ip"]) and "-f" in opts:
            server_ip = args[opts.index(check_opted(opts,["-d","-ip"]))] # Future upgrade for anti code repetition
            fname = args[opts.index("-f")]
            # Make sure, that file to be sent is exists
            if not os.path.exists(fname):
                raise SystemExit(f"{fname} does not exists")
        else:
            raise SystemExit(f"Usage: {sys.argv[0]} sender (-d | -ip) <receiver's address> -f <file to be sent>...")

    # Universal arguments
    if check_opted(opts,["-p","-port"]):
        server_port = int(args[opts.index(check_opted(opts,["-p","-port"]))])

    # Receiving arguments
    if not mode:
        if "--no-api" in dopts:
            use_ipify_api = False

# Receives size in bytes and format it to an easily readable unit, and returns a string
# Followed https://wiki.ubuntu.com/UnitsPolicy
def size_formatter(byte):
    units = ["B","KiB","MiB","GiB"]
    power = 1
    for power in range(1,5):
        if byte / 1024**power < 1:
            break
    return f"{round(byte/1024**(power-1),1)} {units[power-1]}"

# Progress bar drawer
def progress(full,received): # received can be sent too, inside the function it doesn't matter
    ending = "\r"
    if received >= full: # Finished
        received = full # This is because packet size
        ending = "\n"
    percentage = math.floor(received/full*100)
    c_val = math.floor(received/full*PROGRESS_BAR_WIDTH)
    p_val = PROGRESS_BAR_WIDTH-c_val
    completed = "=" * c_val
    pending = "." * p_val
    print(f"{percentage}% [{completed}{pending}] {size_formatter(received)}/{size_formatter(full)}         ",end=ending) # Spaces for solving character deleting from previous line (temporary solution)

def receive_file():
    # Get the internal IP of the correct adapter, with internet access
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8",80))
        global internal_ip
        internal_ip = sock.getsockname()[0]
    
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
        #internal_ip = socket.gethostbyname(socket.gethostname())
        server_address = (internal_ip,server_port)
        server.bind(server_address)
        server.listen(1)

        sockets = [server]

        if use_ipify_api:
            external_ip = get('https://api.ipify.org').content.decode('utf8')
            print(f"Your external IP is {external_ip}")
        print(f"Your internal IP is {internal_ip}")
        
        print("Waiting for sender on port "+str(server_address[1])+"... (Press CTRL+C to abort)")
        while True:
            r,w,e = select.select(sockets,sockets,sockets,1)

            if not (w or r or e):
                continue

            for s in r:
                if s is server: # Client connected
                    client, client_addr = s.accept()
                    sockets.append(client)
                    print("Connected to: ",client_addr)
                else:
                    # Get metadata (filename and size)
                    print("Receiving from "+str(client_addr))
                    metadata = s.recv(PACKER.size)
                    if not metadata:
                        sockets.remove(s)
                        s.close()
                        print("Connection lost")
                    else:
                        # Parse metadata
                        unpacked_metadata = PACKER.unpack(metadata)
                        fname = unpacked_metadata[0].decode().split("\0",1)[0] # split null values after real filename
                        fsize = unpacked_metadata[1]
                        if os.path.exists(fname):
                            raise SystemExit(f"{fname} already exists") # maybe later a better handling
                        print(f"File: {fname}, size:{size_formatter(fsize)}")

                        # Receive file
                        end = False
                        received_data = 0 # have to be unsigned long long
                        with open(fname,"wb") as f:
                            while not end:
                                data = client.recv(PACKET_SIZE)
                                if data:
                                    f.write(data)
                                    received_data += PACKET_SIZE
                                    progress(fsize,received_data)
                                else:
                                    client.close()
                                    end = True
                        # Check for everything is arrived
                        if received_data >= fsize: # because of packet size
                            sys.exit(f"File received as {fname}")
                        else:
                            sys.exit("Connection lost :/")

def send_file():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
        print(f"Connecting to {server_ip} on port {server_port}")
        server_address = (server_ip,server_port)
        sname = fname.split('\\')[-1].split('/')[-1] # Sendable filename without the path
        fsize = os.path.getsize(fname)
        values = (sname.encode(),fsize)
        client.connect(server_address)
        print(f"Sending {sname}...")
        # Send metadata (filename and size)
        packed_data = PACKER.pack(*values)
        client.sendall(packed_data)
        sent_data = 0
        # Send the file
        with open(fname,"rb") as file:
            l = file.read(PACKET_SIZE)
            while l:
                client.sendall(l)
                sent_data += PACKET_SIZE
                progress(fsize,sent_data)
                l = file.read(PACKET_SIZE)
    # Check for everything is sent
    if sent_data >= fsize: # because of packet size
        print(f"File {fname} sent!")
    else:
        print("Connection lost :/")

parse_arguments() # Init
if mode:
    send_file()
else:
    receive_file()
