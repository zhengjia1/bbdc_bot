import subprocess
import json
import requests
import time
import random
from datetime import datetime

bot_token = ""
chat_id = ""
lower_bound = 13
upper_bound = 17

class Stage1Exception(Exception):
    pass
class Stage2Exception(Exception):
    pass
class Stage3Exception(Exception):
    pass

global response_times 
response_times = []

def main():
    current_time = str(datetime.now())[:-7]
    current_time_sanitized = current_time.replace(":", "_")
    
    command = open("command.txt", "r").read()
    command = command.replace("--compressed ", "")
    command = command.replace('-H "Accept-Encoding: gzip, deflate, br, zstd"',"--silent")
    output_original = subprocess.check_output(command, shell=True)

    #Sanitize output - convert to JSON
    output = str(output_original)[2:-1].replace('\\', "")
    print(output)
    #Stage 1: JSONify output from server
    try:
        output = json.loads(output)
    except Exception as error:
        message = f"Stage 1: JSONify from server failed\n{output_original}"
        print(message)
        telegram_request = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message})        
        raise Stage1Exception

    #Stage 2: Validate data
    try:
        response_code = output['code']
        success_status = output['success']
        if response_code == 402 and success_status is False:
            message = f"Stage 3A: JSON extraction failed. \n{output_original}"
            telegram_request = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message})
            raise Exception 
        else:
            data = output['data']
            
    except Exception as error:
        message = f"Stage 3B: JSON extraction failed (others) \n{output_original}"
        telegram_request = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message})

        print(message)
        raise Stage3Exception 
    #Stage 3: send Telegram message
    all_dates = data.get('releasedSlotListGroupByDay')
    if len(str(all_dates)) != 0:
        print("Dates detected:")
        for i in all_dates:
            date = i.split(" ")[0]
            
            target_date = datetime.strptime(date, "%Y-%m-%d")
            current_date = datetime.now()
            days_away = (target_date - current_date).days
            print(f"{date}, {days_away} days away")
            if days_away <= 300:
                slots_for_the_day = all_dates[i]
                for j in slots_for_the_day:
                    #Every single slot
                    if days_away < 3:
                        day_of_week = target_date.strftime("%A")
                        line_one = "New 3A Try-sell slot available! \n"
                        line_two = f"Date: {day_of_week}, {date}\n"
                        line_three = f"{j['slotRefName'].capitalize()}: {j['startTime']}-{j['endTime']}\n"
                        line_four = f"No of slots available: {j['computedSlotAvl']}\n"
                        line_five = f"Group: {j['c3PsrFixGrpNo']}\n"

                        message = f"{line_one}{line_two}{line_three}{line_four}{line_five}"
                        print(message)
                        telegram_request = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message})
                    else:
                        day_of_week = target_date.strftime("%A")
                        line_one = "New 3A slot available! \n"
                        line_two = f"Date: {day_of_week}, {date}\n"
                        line_three = f"{j['slotRefName'].capitalize()}: {j['startTime']}-{j['endTime']}\n"
                        line_four = f"No of slots available: {j['computedSlotAvl']}\n"


                        message = f"{line_one}{line_two}{line_three}{line_four}"
                        telegram_request = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": message})
        print(response_times)
    else:
        print("No dates detected.")

while True:
    
    current_time = datetime.now()
    current_minute = current_time.minute
    current_hour = current_time.hour
    if current_hour >= 7:
        current_date = str(datetime.now().date())
        print(str(i),str(datetime.now())[:-7])
        try:
            main()
            print()
            
        except Exception as error:
            print("Error:", error)
            time.sleep(10)
        sleep_time = random.uniform(13, 17)
        print(f"Wait for {sleep_time} seconds.")
        time.sleep(sleep_time)

    else:
        print("Under maintenance.")
        time.sleep(100)