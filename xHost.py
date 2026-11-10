import httpx
import time
import os
import asyncio
from colorama import Fore, Style, init
from datetime import timedelta
import json
import re

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
   \t   {Fore.LIGHTCYAN_EX}▂▃▄▅▆▇▓▒░{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}Reverse IP By GitBadak{Style.RESET_ALL}{Fore.LIGHTCYAN_EX}░▒▓▇▆▅▄▃▂ {Style.RESET_ALL}\t {Fore.LIGHTRED_EX} :::    : : :  :        :::{Style.RESET_ALL}
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

os.system("clear")
print(BANNER1)
print(INFO_TEXT)

OUTPUT_FILE = 'restdomen.txt'
SAVE_INTERVAL = 5

# Set global untuk dedupe hasil
found_domains = set()

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

def load_existing_domains():
    """Load domain yang sudah ada di output file agar tidak dobel"""
    try:
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    domain = line.strip()
                    if domain:
                        found_domains.add(domain)
    except:
        pass

# ==================== SUMBER API ====================

async def source_webscan(client, target):
    """Sumber 1: webscan.cc"""
    try:
        url = f'https://api.webscan.cc/query/{target}'
        r = await client.get(url, timeout=15.0)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                domains = [d.get('domain', '') for d in data if d.get('domain')]
                return domains
    except:
        pass
    return []

async def source_hackertarget(client, target):
    """Sumber 2: HackerTarget (gratis, limit)"""
    try:
        url = f'https://api.hackertarget.com/reverseiplookup/?q={target}'
        r = await client.get(url, timeout=15.0)
        if r.status_code == 200:
            text = r.text.strip()
            if text and "error" not in text.lower() and "API count exceeded" not in text:
                domains = [line.strip() for line in text.splitlines() if line.strip() and '.' in line]
                return domains
    except:
        pass
    return []

async def source_rapiddns(client, target):
    """Sumber 3: RapidDNS (scrape)"""
    try:
        url = f'https://rapiddns.io/sameip/{target}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = await client.get(url, headers=headers, timeout=15.0)
        if r.status_code == 200:
            # Ambil domain dari tabel
            domains = re.findall(r'<td>([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})</td>', r.text)
            # Filter yang valid
            domains = [d for d in domains if not d.startswith('http') and len(d) > 4]
            return list(set(domains))
    except:
        pass
    return []

# ====================================================

async def check_target(target, client):
    """Cek satu target ke semua sumber, gabung & dedupe"""
    all_domains = set()

    # Coba sumber 1
    domains = await source_webscan(client, target)
    if domains:
        all_domains.update(domains)
        print(f"{Style.BRIGHT}{Fore.BLUE}{target}{Style.RESET_ALL}  [ {Fore.LIGHTGREEN_EX}webscan: {len(domains)}{Style.RESET_ALL} ]")

    # Coba sumber 2
    domains = await source_hackertarget(client, target)
    if domains:
        all_domains.update(domains)
        print(f"{Style.BRIGHT}{Fore.BLUE}{target}{Style.RESET_ALL}  [ {Fore.CYAN}hackertarget: {len(domains)}{Style.RESET_ALL} ]")

    # Coba sumber 3 (kalau yang lain kosong atau ingin lebih banyak)
    if len(all_domains) < 3:
        domains = await source_rapiddns(client, target)
        if domains:
            all_domains.update(domains)
            print(f"{Style.BRIGHT}{Fore.BLUE}{target}{Style.RESET_ALL}  [ {Fore.MAGENTA}rapiddns: {len(domains)}{Style.RESET_ALL} ]")

    # Dedupe dengan hasil global
    new_domains = [d for d in all_domains if d and d not in found_domains]
    for d in new_domains:
        found_domains.add(d)

    if new_domains:
        print(f"{Style.BRIGHT}{Fore.GREEN}{target}{Style.RESET_ALL}  [ {Fore.LIGHTGREEN_EX}New: {len(new_domains)} domains{Style.RESET_ALL} ]")
        return '\n'.join(new_domains) + '\n'
    else:
        print(f"{Style.BRIGHT}{Fore.YELLOW}{target}{Style.RESET_ALL}  [ {Fore.YELLOW}No new domains{Style.RESET_ALL} ]")
        return ''

def write_output_to_file(output):
    try:
        valid = [line for line in output if line and line.strip()]
        if not valid:
            return
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as file:
            file.writelines(valid)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error writing output: {e}{Style.RESET_ALL}")

def remove_duplicate_targets(existing, new_list):
    existing_set = set(existing)
    return [t for t in new_list if t not in existing_set]

async def check_ips(targets, max_concurrent=5):
    load_existing_domains()
    output = []
    start_time = time.time()
    last_save_time = start_time

    print(f"\n{Fore.LIGHTGREEN_EX}Reading targets from file...{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}Total Targets : {len(targets)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}Existing domains in result: {len(found_domains)}{Style.RESET_ALL}\n")

    unique_targets = list(dict.fromkeys(targets))  # keep order, remove dupes
    groups = [unique_targets[i:i + max_concurrent] for i in range(0, len(unique_targets), max_concurrent)]

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            for group in groups:
                tasks = [check_target(t, client) for t in group]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for r in results:
                    if isinstance(r, str) and r.strip():
                        output.append(r)

                current_time = time.time()
                if current_time - last_save_time >= SAVE_INTERVAL and output:
                    write_output_to_file(output)
                    output.clear()
                    last_save_time = current_time

        except KeyboardInterrupt:
            print(f"\n{Fore.LIGHTRED_EX}Interrupted. Saving...{Style.RESET_ALL}")

        finally:
            if output:
                write_output_to_file(output)

    elapsed = time.time() - start_time
    print(BANNER2)
    print(f"\n{Fore.LIGHTYELLOW_EX}Total time: {str(timedelta(seconds=int(elapsed)))}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTYELLOW_EX}Total unique domains found: {len(found_domains)}{Style.RESET_ALL}")
    print(f"\nOutput written to {Fore.YELLOW}{OUTPUT_FILE}{Style.RESET_ALL}")

# Main
while True:
    file_path = input(f"Enter the path to the file containing IP/Domain (e.g., ips.txt): ")
    targets = read_ips_from_file(file_path)
    if targets:
        break
    else:
        print(f"{Fore.LIGHTRED_EX}File empty or not found.{Style.RESET_ALL}")

asyncio.run(check_ips(targets))
print(f"\n{Fore.LIGHTGREEN_EX}Congrats Your Project Is FINISHED!!!{Style.RESET_ALL}")
