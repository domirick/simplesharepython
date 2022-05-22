
# Simple Share Python
Simple P2P file transfer in python with client-server architecture.
The program uses TCP protocol to communicate, and the receiver **should open a port**,when participants aren't in the same network (default port is 32700).

## Usage
> Compatible with Python 3.x (tested with 3.10)

This CLI program can operate in sender or receiver mode. Or just display information messages, like help, or version.
```
Usage when sending: ssp.py send -d IP -f FILE [-p PORT_NUMBER]
Usage when receiving: ssp.py receive [-p PORT_NUMBER] [--no-api]
Usage when getting information: ssp.py [--help] [--version]

Sending arguments:
  -d, -ip IP_ADDRESS		Required, the receiver's IP address
  -f FILE_LOCATION			Required, the file to be sent
  -p, -port PORT_NUMBER		Optional, default is 32700 (have to match with the receiver's

Receiving arguments:
  -p, -port PORT_NUMBER		Listening port, default is 32700 (you should open it)
  --no-api					Do not use ipify API to get the external IP address

Standalone arguments:
  -h, --help				Show this help message and exit
  -v, --version				Show informations about the program, and the version then exit
```
> Tip: You can shorten `receive` command, because program only checks for `send`, and otherwise it will be in receiving mode, so you can type anything instead of `receive`.
> Example: `ssp.py rec`

## Privacy notices
- **The program do not use any encryption.** If you wanted to send sensitive data, I suggest to use PGP.

- Program uses [ipify API](https://www.ipify.org), and sends a GET request to the site to get your external IP. You can disable this function with `--no-api` switch.

- In receiving mode the program connects to Google (8.8.8.8) on port 80 (just for get the right adapter's address with internet access)

## Known issues
- Progress bar issues (will be fixed in the future)
	- On bigger packet size (65535 bytes) progress bar can't work properly (appears a lot on receiver's side, when download is finished).
	- Error message writes it over, and not visible properly.

 Nothing else yet, so feel free to test.

## Future improvements
- Optimizing packet size
- Multiple file receiving, and sending without restart the program
- Encryption
- GUI
- Unit tests
- Optional DDOS protection (or password protection)