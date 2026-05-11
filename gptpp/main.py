from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://chatgpt.com")

        input("Login manually, then press ENTER...")

        await page.fill("textarea", "Hello!")
        await page.keyboard.press("Enter")

        await page.wait_for_timeout(5000)

        messages = await page.query_selector_all("[data-message-author-role='assistant']")
        for m in messages:
            print(await m.inner_text())

import asyncio
asyncio.run(main())