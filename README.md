# Gramnetwork Multi-Account

An automated for Gramnetwork supporting multiple accounts with parallel mining and auto tasks.

## Features

- Auto complete tasks for all accounts
- Parallel mining (all accounts run simultaneously)
- Live countdown for each account's mining time
- Auto claim & restart mining when time is up

## Register
- You can register using this [Link Register](https://t.me/Gramnetwork_bot?startapp=2113168134)
## Requirements

- Python 3.8 or higher

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/monteksz/gram.git
   cd gram

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt

3. **Prepare your accounts**
- Put one initData per line (each line = one account)
- Example data.txt:
  ```bash
  initdata account 1...
  initdata account 2...

4. **How to Run**
   ```bash
   python main.py

## Usage Guide
- Fill data.txt with your accounts' initData (1 per line)
- Run the script
- Auto task completion will run first
- Parallel mining will start automatically

## Notes
- The bot will run continuously until you press Ctrl + C
- 30 seconds delay between tasks
- Claim mining will retry up to 5 times if it fails
- All accounts mine at the same time (parallel)

## Warning
Use this at your own risk. Avoid excessive usage that may result in account bans.
