import requests
import urllib.parse
import time
import sys
import threading
from fake_useragent import UserAgent

ua = UserAgent()
lock = threading.Lock()

def load_all_init_data(file_path="data.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        accounts = []
        for i, line in enumerate(lines, 1):
            content = line.strip()
            if content:
                accounts.append({
                    "id": i,
                    "init_data": content,
                    "username": f"Account-{i}"
                })
        print(f"Loaded {len(accounts)} accounts from data.txt\n")
        return accounts
    except Exception as e:
        print(f"Failed to load data.txt: {e}")
        sys.exit(1)


def get_headers():
    return {
        "Accept": "application/json",
        "User-Agent": ua.random
    }


def api_request(method, endpoint, init_data, payload=None):
    base_url = "https://app.gramnetwork.online/api/"
    url = base_url + endpoint
    headers = get_headers()
    
    try:
        if method == "GET":
            encoded = urllib.parse.quote(init_data)
            full_url = f"{url}?initData={encoded}"
            resp = requests.get(full_url, headers=headers, timeout=30)
        else:
            data = {"initData": init_data}
            if payload:
                data.update(payload)
            resp = requests.post(url, data=data, headers=headers, timeout=30)
        
        return resp.json() if resp.status_code == 200 else {"success": False}
    except:
        return {"success": False}


def claim_mining(init_data, username):
    with lock:
        print(f"\n? Claim Mining for {username} ... ", end="")
    for attempt in range(1, 6):
        result = api_request("POST", "claim_mining.php", init_data)
        if result.get('success'):
            with lock:
                print("SUCCESS")
            return True
        time.sleep(5)
    with lock:
        print("FAILED after retries")
    return False


def start_mining(init_data, username):
    with lock:
        print(f"? Starting Mining for {username} ... ", end="")
    result = api_request("POST", "start_mining.php", init_data)
    with lock:
        print("SUCCESS" if result.get('success') else "FAILED")
    return result.get('success', False)


def mining_worker(account):
    while True:
        try:
            result = api_request("GET", "get_user_data.php", account["init_data"])
            if not result.get("success") or "user" not in result:
                time.sleep(10)
                continue

            user = result["user"]
            account["username"] = user.get("username", account["username"])

            time_left = user.get('time_left', '00:00:00')

            with lock:
                print("\n" + "="*70)
                print(f"Username       : {account['username']}")
                print(f"Total Balance  : {user.get('total_balance', '0')} GRM")
                print(f"Tokens Earned  : {user.get('tokens_earned', '0')} GRM")
                print(f"Energy         : {user.get('energy', '0')}")
                print(f"Time Left      : {time_left}")
                print("="*70)

            if time_left == "00:00:00" or time_left.startswith("00:00"):
                claim_mining(account["init_data"], account["username"])
                time.sleep(3)
                start_mining(account["init_data"], account["username"])
                time.sleep(5)
                continue

            try:
                h, m, s = map(int, time_left.split(':'))
                seconds_left = h * 3600 + m * 60 + s
            except:
                seconds_left = 300

            while seconds_left > 0:
                hours = seconds_left // 3600
                minutes = (seconds_left % 3600) // 60
                seconds = seconds_left % 60
                current = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                with lock:
                    print(f"\rTime Left {account['username']:15} : {current} (Live)", end="", flush=True)
                
                time.sleep(1)
                seconds_left -= 1

            # Waktu habis
            with lock:
                print(f"\n\nTime finished for {account['username']} ? Claiming & Restarting...")
            claim_mining(account["init_data"], account["username"])
            time.sleep(3)
            start_mining(account["init_data"], account["username"])
            time.sleep(5)

        except Exception as e:
            with lock:
                print(f"Error on {account['username']}: {e}")
            time.sleep(10)


def complete_tasks_for_account(account):
    print(f"Processing tasks for {account['username']} ...")
    tasks_data = api_request("GET", "get_tasks.php", account["init_data"])
    tasks = tasks_data.get('tasks', []) if tasks_data.get('success') else []
    
    pending = [t for t in tasks if not t.get('is_completed')]
    print(f"   Found {len(pending)} pending tasks.")
    
    for i, task in enumerate(pending, 1):
        print(f"   [{i}/{len(pending)}] Completing: {task['title']}")
        result = api_request("POST", "complete_task.php", account["init_data"], {"task_id": task['id']})
        status = "Success" if result.get('success') else "Failed"
        print(f"      Status: {status}")
        if i < len(pending):
            time.sleep(30)
    print(f"   Task completion for {account['username']} finished.\n")


def main():
    accounts = load_all_init_data("data.txt")
    
    if not accounts:
        print("No accounts found!")
        return

    print("Starting Auto Task Completion for all accounts...\n")
    for account in accounts:
        complete_tasks_for_account(account)

    print("\nStarting Parallel Mining for all accounts...\n")
    
    threads = []
    for account in accounts:
        t = threading.Thread(target=mining_worker, args=(account,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(2)

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nProgram stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
