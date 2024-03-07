import asyncio
import random
import traceback

from playwright.async_api import async_playwright
from random import uniform
from loguru import logger
from config import *

from utils import get_accounts, get_format_proxy, switch_to_page_by_title

NEW_PASSWORD = "Password_12345"

async def run(id, private_key, proxy, semaphore):
    # 3 попытки зайти в кошелек
    for _ in range(3):
        try:
            async with semaphore:
                # await gas_checker(id)
                logger.info(f"{id} | START")

                # Initialize the browser and context
                async with async_playwright() as playwright:
                    if proxy is not None and USE_PROXY is True:
                        address, port, login, password = get_format_proxy(proxy)
                        context = await playwright.chromium.launch_persistent_context(
                            '',
                            headless=False,
                            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                            proxy={
                            "server": f"http://{address}:{port}",
                            "username": login,
                            "password": password
                            },
                            args=[
                                '--disable-blink-features=AutomationControlled',
                                f"--disable-extensions-except={EXTENSION_PATH}",
                                f"--load-extension={EXTENSION_PATH}"
                            ]
                        )
                    else:
                        context = await playwright.chromium.launch_persistent_context(
                            '',
                            headless=False,
                            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',

                            args=[
                                '--disable-blink-features=AutomationControlled',
                                f"--disable-extensions-except={EXTENSION_PATH}",
                                f"--load-extension={EXTENSION_PATH}"
                            ]
                        )
                    
                    page = await context.new_page()
                    await page.goto('chrome-extension://lkimhcmllogkbbkkhkkjfhpemngidiem/options.html?onboarding=true')
                    await page.close()
                    page = await switch_to_page_by_title(context, '')
                    await page.close()
                    
                    page = await switch_to_page_by_title(context, 'Backpack')
                    await page.goto('chrome-extension://lkimhcmllogkbbkkhkkjfhpemngidiem/options.html?onboarding=true')

                    await page.click('span:text("Import Wallet")', timeout=5000)
                    await page.click('span:text("Skip")', timeout=5000)
                    await page.click('span:text("Import private key")', timeout=5000)
                    await page.click('span:text("Solana")', timeout=5000)
                    await page.fill('textarea', private_key)
                    await page.press('textarea', 'Enter')
                    await asyncio.sleep(uniform(0.3, 0.7))

                    # Ввод пароля
                    await page.fill('input[placeholder="Password"]', NEW_PASSWORD, timeout=5000) 
                    await page.fill('input[placeholder="Confirm Password"]', NEW_PASSWORD) 
                    await page.click('input[type="checkbox"]') 
                    await asyncio.sleep(uniform(0.3, 0.7))
                    await page.press('input[placeholder="Confirm Password"]', 'Enter')
                    await asyncio.sleep(uniform(2, 3))
                          
                    if MODE == "SWAP":
                        await swap(id, context, page)
                    else:
                        logger.error("Wrong mode")
                        return
                    
                    await asyncio.sleep(10)
                    break
                
        except Exception as ex:
            logger.error(f"{id} Retry... | {traceback.format_exc()}, {ex} ")
            await asyncio.sleep(10)
        finally:
            try:
                await context.close()
            except:
                pass


async def swap(id, context, page):
    rand_self_count = random.randint(SWAP_COUNT[0], SWAP_COUNT[1])
    logger.info(f"{id} | START {rand_self_count} swaps..")
    count_errors = 0
    for i in range(1, rand_self_count+1):
        if count_errors > MAX_TRY_SEND:
            logger.error(f"{id} | Error rate of more than {MAX_TRY_SEND} | Skip wallet...")
            break
        try:
            await page.goto("chrome-extension://lkimhcmllogkbbkkhkkjfhpemngidiem/popup.html")
            await page.click('svg[data-testid="SwapHorizIcon"]', timeout=5000)
            await asyncio.sleep(random.uniform(1, 2))
            
            
            await page.click('xpath=//div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div/div[1]/div[2]/div/div/button', timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            from_asset = random.choice(FROM_ASSET_LIST)
            await page.fill('input[placeholder="Search"]', from_asset, timeout=20000) 
            await asyncio.sleep(random.uniform(0.5, 1))
            await page.click(f'p:text("{from_asset}")', timeout=20000)

            await page.click('xpath=//div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div/div[3]/div/div[1]/div[2]/div/div/button', timeout=5000)
            await asyncio.sleep(random.uniform(0.5, 1))
            to_asset = random.choice(TO_ASSET_LIST)
            await page.fill('input[placeholder="Search"]', to_asset, timeout=20000) 
            await asyncio.sleep(random.uniform(1, 2))
            await page.wait_for_selector(f'p:text("{to_asset}")', timeout=20000)
            elements = await page.query_selector_all('xpath=//p')
            for el in elements:
                text_el = await el.text_content()
                if text_el.strip() == to_asset:
                    # print("Элемент найден:", el)
                    await el.click()
                    break

            await asyncio.sleep(random.uniform(1, 1.5))
            rand_sum_tx = random.uniform(float(SWAP_SELF_AMOUNT[0]), float(SWAP_SELF_AMOUNT[1]))
            await page.fill('input[placeholder="0"]', f"{rand_sum_tx:.10f}", timeout=10000)
            await asyncio.sleep(random.uniform(6, 10))
            await page.click('span:text("Review")', timeout=5000)
            await asyncio.sleep(random.uniform(6, 10))
            await page.click('span:text("Approve")', timeout=5000)
            await asyncio.sleep(random.uniform(10, 20))
            logger.success(f"{id} | Swap {i} | {rand_sum_tx} {from_asset} -> {to_asset}")
            count_errors=0
            await asyncio.sleep(random.randrange(NEXT_TX_MIN_WAIT_TIME, NEXT_TX_MAX_WAIT_TIME))
        except Exception as ex:
            logger.error(traceback.format_exc(), ex)
            count_errors+=1

async def main(accounts):
    semaphore = asyncio.Semaphore(THREADS_NUM)
    tasks = [run(id, private_key, proxy, semaphore) for id, private_key, proxy in accounts]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    accounts = get_accounts()
    logger.info(f"Loaded {len(accounts)} accounts")
    asyncio.run(main(accounts))
    