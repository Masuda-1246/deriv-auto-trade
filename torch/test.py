import asyncio
import time
import requests



async def main():
    while True:
        try:
            await get_rate()
            time.sleep(2*60)
        except Exception as e:
            print(e)
            continue

async def get_rate():
    url = "http://127.0.0.1:8080/api/get/rate"
    r = requests.get(url)
    print(r.json())


asyncio.run(main())