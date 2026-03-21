import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

LIBRARY_URL = "https://textilestudycenter.com/library/"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,          # keep False to avoid bot detection
            slow_mo=200              # human-like delay
        )

        context = browser.new_context(
            accept_downloads=True
        )

        page = context.new_page()
        page.goto(LIBRARY_URL, timeout=60000)

        print("🔍 Collecting book links...")
        page.wait_for_selector("ol li a")

        book_urls = page.eval_on_selector_all(
            "ol li a",
            "els => els.map(e => e.href)"
        )

        print(f"📚 Found {len(book_urls)} books")

        for index, book_url in enumerate(book_urls, start=1):
            print(f"\n➡️ [{index}/{len(book_urls)}] Processing:")
            print(book_url)

            try:
                book_page = context.new_page()
                book_page.goto(book_url, timeout=60000)

                # click MediaFire link
                book_page.wait_for_selector("a[href*='mediafire.com']", timeout=15000)

                with context.expect_page() as mf_page_info:
                    book_page.click("a[href*='mediafire.com']")

                mf_page = mf_page_info.value
                mf_page.wait_for_load_state()

                # wait for real MediaFire download button
                mf_page.wait_for_selector("#downloadButton", timeout=60000)

                with mf_page.expect_download() as download_info:
                    mf_page.click("#downloadButton")

                download = download_info.value
                filename = download.suggested_filename
                save_path = os.path.join(DOWNLOAD_DIR, filename)

                download.save_as(save_path)
                print(f"✅ Downloaded: {filename}")

                mf_page.close()
                book_page.close()

                time.sleep(4)  # polite delay

            except TimeoutError:
                print("⚠️ Skipped (timeout or missing link)")
            except Exception as e:
                print(f"❌ Error: {e}")

        browser.close()
        print("\n🎉 All done!")

if __name__ == "__main__":
    main()
