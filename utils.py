import asyncio

import pandas

from loguru import logger
from playwright.async_api._generated import Page


async def switch_to_page_by_title(context, title) -> Page:
    for _ in range(50):
        for page in context.pages:
            # print([await page.title()])
            if title == await page.title():
                await page.bring_to_front()  # Переключаемся на страницу
                # print(await page.title())
                return page
        await asyncio.sleep(0.5)
    return None  
        

def get_format_proxy(proxy):
    login_password, address_port = proxy.split('@')
    address, port = address_port.split(':')
    login, password = login_password.split(':')
    return address, port, login, password


def get_accounts():
    with open('Accounts.xlsx', 'rb') as file:
        try:
            wb = pandas.read_excel(file, sheet_name="Accounts")
        except Exception as ex:
            logger.error(ex)
            raise ex
        
        accounts_data = {}
        for index, row in wb.iterrows():
            private_key = row["Private Key"]
            proxy = row["Proxy"]
            accounts_data[int(index) + 1] = {
                "private_key": private_key,
                "proxy": proxy,
            }
                    
        accounts = []
        for k, v in accounts_data.items():
            accounts.append((
                k,
                v['private_key'], 
                v['proxy'] if isinstance(v['proxy'], str) else None,
            ))
        return accounts

