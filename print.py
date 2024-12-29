from playwright.async_api import async_playwright
import asyncio
import time


DISK_CACHE_SIZE = 2 * 1024 * 1024 * 1024

def handle_response_received(params):
    # The "params" dict includes 'response' which may have 'fromDiskCache' or 'fromServiceWorker'
    resp = params["response"]
    url = resp["url"]
    from_disk = resp.get("fromDiskCache", False)
    from_service_worker = resp.get("fromServiceWorker", False)
    print(f"Response for {url} - fromDiskCache={from_disk}, fromServiceWorker={from_service_worker}")


async def capture_screenshot(dim=1000, sleep_time=0):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="user_data",
            headless=False,
            args=[
                # "--disable-gpu",
                f"--disk-cache-size={DISK_CACHE_SIZE}",
                "--enable-aggressive-domstorage-flushing",
            ],
        )

        page = await browser.new_page()

        await page.set_viewport_size({"width": dim, "height": dim})

        # Attach a CDP session
        cdp_session = await browser.new_cdp_session(page)
        await cdp_session.send("Network.enable")

        # Listen for responseReceived events
        cdp_session.on("Network.responseReceived", lambda params: handle_response_received(params))

        await page.goto('http://127.0.0.1:3000/docs/index.html?district=2', wait_until='domcontentloaded')

        # Wait for Leaflet to finish loading tiles
        await page.evaluate("""
            new Promise((resolve) => {
                const map = document.querySelector('.leaflet-container'); // Replace with the correct map container if needed
                if (!map) throw new Error("Leaflet container not found");

                let tilesLoaded = 0;
                const tiles = document.querySelectorAll('.leaflet-tile');
                const totalTiles = tiles.length;

                tiles.forEach((tile) => {
                    if (tile.complete) {
                        tilesLoaded++;
                    } else {
                        tile.addEventListener('load', () => {
                            tilesLoaded++;
                            if (tilesLoaded === totalTiles) resolve();
                        });
                    }
                });

                // If all tiles are already loaded
                if (tilesLoaded === totalTiles) resolve();
            });
        """)

        time.sleep(sleep_time)
        await page.screenshot(path='output.png', full_page=True)

        await browser.close()

asyncio.run(capture_screenshot(8000, 5))
