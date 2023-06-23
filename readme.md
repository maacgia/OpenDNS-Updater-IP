# OpenDNS.com Updater IP  

This script is designed to automatically update the IP address on OpenDNS It periodically checks for IP changes and performs the update if necessary.

## Prerequisites

- Python 3.x
- Requests library 
  
  ```python
    pip install dotenv
    pip install python-dotenv
  ```
## Configuration

1. Open the `.env` file and enter your OpenDNS credentials (`USERNAME` and `PASSWORD`).
2. Customize the list of IP check services in the `check_ip_services` variable if needed in app.py.

## Usage

1. Run the script: `python app.py`.
2. The script will start checking for IP changes every 120 second.
3. If the IP has changed, it will update OpenDNS with the new IP.
4. The script will log its actions to the `app.log` file.

## Customization

- To adjust the interval between IP checks, modify the `time.sleep` value (in seconds) in the script.
- You can change the log file name and format by modifying the logging configuration in the script.

## License

This project is licensed under the [MIT License](LICENSE).
