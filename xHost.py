import httpx
import time
import asyncio
from colorama import Fore, Style, init
from datetime import timedelta
import json

init()

BANNER1 = f"""
{Fore.LIGHTRED_EX}
                                                          @@@    @@@@@@@@        @@@
            ooooo   ooooo                        .       @@@@   @@@@@@@@@@      @@@@
            `888'   `888'                      .o8      @@!@!   @@!   @@@@     @@!@!
oooo    ooo  888     888   .ooooo.   .oooo.o .o888oo   !@!!@!   !@!  @!@!@    !@!!@!
 `88b..8P'   888ooooo888  d88' `88b d88(  "8   888    @!! @!!   @!@ @! !@!   @!! @!!
   Y888'     888     888  888   888 `"Y88b.    888   !!!  !@!   !@!!!  !!!  !!!  !@!
 .o8"'88b    888     888  888   888 o.  )88b   888 . :!!:!:!!:  !!:!   !!!  :!!:!:!!
o88'   888o o888o   o888o `Y8bod8P' 8""888P'   "888" !:::!!:::  :!:    !:!  !:::!!::
                                                          :::   ::::::: ::       :::
   \t   {Fore.LIGHTCYAN_EX}▂▃▄▅▆▇▓▒░{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}Reverse IP By Mr.Doom{Style.RESET_ALL}{Fore.LIGHTCYAN_EX}░▒▓▇▆▅▄▃▂ {Style.RESET_ALL}\t {Fore.LIGHTRED_EX} :::    : : :  :        :::{Style.RESET_ALL}
"""

BANNER2 = f"""             
{Fore.LIGHTGREEN_EX}
███████╗██╗███╗   ██╗██╗███████╗██╗  ██╗██╗
██╔════╝██║████╗  ██║██║██╔════╝██║  ██║██║
█████╗  ██║██╔██╗ ██║██║███████╗███████║██║
██╔══╝  ██║██║╚██╗██║██║╚════██║██╔══██║╚═╝
██║     ██║██║ ╚████║██║███████║██║  ██║██╗
╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝{Style.RESET_ALL}
"""
INFO_TEXT = f"""
{Fore.LIGHTGREEN_EX}
{Style.BRIGHT}[  FOR YOUR INFORMATION ]{Style.RESET_ALL}{Fore.LIGHTCYAN_EX}

- You Can Check IP & Domains
- Make Your List IPs Like This
    example.com
    123.45.678
    example.com
    123.456.78
    ...
- Your Result Will Be In restdomen.txt
- xHost404 Will Only Retrieve Acquired Domains
- don't assume xHost404 is for Live Or dead the Domains {Style.RESET_ALL}
"""

# Display the banner
os.system("clear")
print(BANNER1)
print(INFO_TEXT)

OUTPUT_FILE = 'restdomen.txt'  # Output file name
SAVE_INTERVAL = 5  # Save results every 5 seconds (adjust as needed)

# Function to read IP addresses from a file
def read_ips_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            ips = [line.strip() for line in file if line.strip()]
        return ips
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}Error: File not found - {file_path}{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error reading IPs from file: {e}{Style.RESET_ALL}")
        return []

async def check_webscan_api(ip_address, existing_ips):
    api_url = f'https://api.webscan.cc/query/{ip_address}'

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)

            if response.status_code == 403:
                print(f"{Style.BRIGHT}{Fore.BLUE}{ip_address}{Style.RESET_ALL}  [ {Fore.RED} Eror {Fore.LIGHTRED_EX}403 {Fore.RED}Forbidden{Style.RESET_ALL} ]")
                return ''

            response.raise_for_status()
            try:
                data = response.json()
            except json.JSONDecodeError as json_error:
                print(f"{Style.BRIGHT}{Fore.BLUE}{ip_address}{Style.RESET_ALL}  [ {Fore.RED}Eror {Fore.LIGHTRED_EX}404{Fore.RED} Not Found {Style.RESET_ALL} ]")
                return ''

        if isinstance(data, list) and data:
            domains = [entry['domain'] for entry in data]
            if domains:
                result = f"[ {Fore.LIGHTGREEN_EX}Get {len(domains)} Domains{Style.RESET_ALL} ]"
                print(f"{Style.BRIGHT}{Fore.BLUE}{ip_address}{Style.RESET_ALL}  {result}")
                return f"{'\n'.join(domains)}\n"
            else:
                return ''
        else:
            return ''

    except (httpx.RequestError, httpx.TimeoutException) as e:
        print(f"{Style.BRIGHT}{Fore.BLUE}{ip_address}{Style.RESET_ALL}  [ {Fore.RED} Eror {Fore.LIGHTRED_EX}403 {Fore.RED}Forbidden{Style.RESET_ALL} ]")
        return ''

def write_output_to_file(output):
    try:
        with open(OUTPUT_FILE, 'a') as file:
            file.writelines(output)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error writing output to file: {e}{Style.RESET_ALL}")

def remove_duplicate_ips(existing_ips, new_ips):
    duplicates = set(existing_ips).intersection(new_ips)
    for ip in duplicates:
        print(f"{ip}  [ {Fore.YELLOW}Duplicate{Style.RESET_ALL} ]")
    return list(set(new_ips) - duplicates)

async def check_ips(ips_to_check, max_concurrent=10):
    existing_ips = read_ips_from_file(OUTPUT_FILE)  # Read existing IPs from the previous result file
    output = []
    start_time = time.time()  # Record start time
    last_save_time = start_time

    print(f"\n{Fore.LIGHTGREEN_EX}Reading IPs from file...{Style.RESET_ALL}\n")
    print(f"{Fore.LIGHTGREEN_EX}Total Domains/IPs : {len(ips_to_check)}{Style.RESET_ALL}")
    # Remove duplicates from the list of IPs to check
    unique_ips_to_check = remove_duplicate_ips(existing_ips, ips_to_check)

    # Divide the list of IPs into groups of max_concurrent size
    ip_groups = [unique_ips_to_check[i:i + max_concurrent] for i in range(0, len(unique_ips_to_check), max_concurrent)]

    try:
        for ip_group in ip_groups:
            # Create a list of asynchronous tasks
            tasks = [check_webscan_api(ip, existing_ips) for ip in ip_group]

            # Run tasks concurrently
            results = await asyncio.gather(*tasks)

            # Collect results
            output.extend(results)

            # Save results to file every SAVE_INTERVAL seconds
            current_time = time.time()
            if current_time - last_save_time >= SAVE_INTERVAL:
                write_output_to_file(output)
                last_save_time = current_time

    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTRED_EX}Script interrupted. Finishing up...{Style.RESET_ALL}")

    finally:
        # Write output to file after finishing the loop
        write_output_to_file(output)

        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time
        elapsed_time_str = str(timedelta(seconds=elapsed_time))  # Convert seconds to the format hours:minutes:seconds
        print(BANNER2)

        print(f"\n{Fore.LIGHTYELLOW_EX}Total execution time: {elapsed_time_str}{Style.RESET_ALL}")
        
        print(f"\nOutput written to {Fore.YELLOW}{OUTPUT_FILE}{Style.RESET_ALL}")

# Ask user for the file containing IP addresses to check
while True:
    file_path = input(f"Enter the path to the file containing IP addresses (e.g., ips_to_check.txt): ")
    ips_to_check = read_ips_from_file(file_path)

    # Check if the list of IPs is empty or file not found
    if ips_to_check:
        break
    else:
        print(f"{Fore.LIGHTRED_EX}List of IPs is empty or file not found. Please check the file path.{Style.RESET_ALL}")

# Run the asynchronous loop
asyncio.run(check_ips(ips_to_check))

# Display a message after completion or forced termination
print(f"\n{Fore.LIGHTGREEN_EX}Congrats Your Project Is FINISHED!!!{Style.RESET_ALL}")
