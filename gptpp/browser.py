from playwright.async_api import async_playwright


async def launch_browser():
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch_persistent_context(
        "./profile",
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )

    page = await browser.new_page()

    await page.goto("https://chatgpt.com")

    return playwright, browser, page
