import asyncio
import sys
import json
from pyppeteer import launch
import os

async def capture_screenshot(url, width, height, wait_time, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    await page.setViewport({'width': width, 'height': height})
    await page.goto(url)
    await asyncio.sleep(wait_time / 1000)
    await page.screenshot({'path': output_path, 'fullPage': True})
    await browser.close()
    return output_path

def main(params):
    url = params.get('url')
    width = params.get('width', 1280)
    height = params.get('height', 720)
    wait_time = params.get('wait_time', 3000)
    output_path = params.get('output_path', 'results/screenshot.png')

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        capture_screenshot(url, width, height, wait_time, output_path)
    )
    return result

if __name__ == "__main__":
    # Recibir parámetros JSON desde la línea de comandos
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {}
    main(params)
