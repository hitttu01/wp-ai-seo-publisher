import os
import time
import io
import requests
import pandas as pd
from dotenv import load_dotenv

from generator import generate_article_content, generate_faqs
from processor import process_and_format_article
from image_maker import create_unique_images
from wp_publisher import publish_wordpress_post

load_dotenv()

# Google Sheet Configuration
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1kieMk1araaWljeKZh4pxwteTtm6KGeqBAwdBRaw_meE")


def run_automation_pipeline(topic_title: str, use_dalle: bool = True):
    """
    Executes the full end-to-end zero-touch automation pipeline for a single topic:
    1. Generates 1,200+ word SEO article content & 10 structured FAQs via OpenAI GPT-4o.
    2. Formats headings (<h2 class="h2dav">Question?</h2>), bolds keywords, and injects shortcodes + internal links.
    3. Generates 3 unique topic images (DALL-E 3 with randomized prompts or branded templates).
    4. Publishes to WordPress strictly as DRAFT with media attachments, Yoast SEO meta, and FAQ accordion + JSON-LD Schema.
    5. Cleans up local image files automatically.
    """
    print(f"\n========================================================")
    print(f"🚀 Starting Automation Pipeline for: '{topic_title}'")
    print(f"========================================================")

    # Step 1: Generate AI Content & 10 Structured FAQs
    print("\n[1/4] Generating article content (1,200+ words) & 10 structured FAQs via OpenAI...")
    raw_content = generate_article_content(topic_title)
    faq_items = generate_faqs(topic_title)
    print(f"      Article drafted ({len(raw_content.split())} words) + {len(faq_items)} FAQ items generated.")

    # Step 2: Clean and Format Text
    print("\n[2/4] Formatting text, applying <h2 class=\"h2dav\">, bolding keywords, and distributing 7 shortcodes...")
    formatted_content = process_and_format_article(raw_content)

    # Step 3: Generate Dynamic Unique Topic Images
    print("\n[3/4] Generating 3 unique topic images...")
    image_paths = create_unique_images(topic_title, use_dalle=use_dalle)

    # Step 4: Publish to WordPress REST API as DRAFT
    print("\n[4/4] Publishing post to WordPress as a clean DRAFT with Yoast SEO, FAQ Accordion & Schema...")
    published_post = publish_wordpress_post(
        title=topic_title,
        content=formatted_content,
        image_paths=image_paths,
        faq_items=faq_items
    )

    if published_post:
        print("\n🎉 Pipeline Step Completed Successfully!")
        print(f"   Post ID     : {published_post.get('id')}")
        print(f"   Status      : {published_post.get('status')} (Draft)")
        print(f"   Edit URL    : {published_post.get('edit_url')}")
        print(f"   Preview URL : {published_post.get('preview_url')}")
        return published_post
    else:
        print(f"\n⚠️ Pipeline failed during WordPress publishing for: '{topic_title}'")
        return None


def process_sheet_queue(sheet_id=GOOGLE_SHEET_ID):
    """
    Reads blog post titles from a public Google Sheet using pandas and runs the pipeline sequentially.
    """
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    print(f"📥 Fetching title queue from Google Sheet (ID: {sheet_id})...")
    try:
        resp = requests.get(csv_url, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"Google Sheet export returned status {resp.status_code}")

        df = pd.read_csv(io.StringIO(resp.text))
        raw_titles = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        titles = [t for t in raw_titles if t and t.lower() not in ["title", "titles", "topic", "topics"]]

        total = len(titles)
        print(f"✅ Found {total} valid title(s) in the queue.")

        for index, title in enumerate(titles, start=1):
            print(f"\n>>> Processing Queue Item [{index}/{total}]: {title}")
            run_automation_pipeline(title)

            # Safety cooldown delay between posts
            if index < total:
                print("\n⏳ Cooldown: Waiting 5 seconds before next post to prevent server firewall blocks...")
                time.sleep(5)

        print("\n🏁 All items in the Google Sheet queue have been processed!")

    except Exception as e:
        print(f"❌ Error reading Google Sheet. Ensure sheet is public ('Anyone with the link can view'). Error: {e}")


if __name__ == "__main__":
    process_sheet_queue()
