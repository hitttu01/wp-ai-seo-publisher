import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from processor import extract_yoast_description
from image_maker import cleanup_local_images

load_dotenv()

WP_URL = os.getenv("WP_SITE_URL", "").rstrip('/')
USERNAME = os.getenv("WP_USERNAME")
PASSWORD = os.getenv("WP_APP_PASSWORD")

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# In-memory category cache to avoid redundant network lookups
_CATEGORY_CACHE = {}


def get_or_create_category(category_name: str = "Guides") -> int:
    """
    Dynamically finds or creates the category ID in WordPress:
    1. Checks in-memory cache.
    2. Searches the WP REST API: /wp-json/wp/v2/categories?search={category_name}
    3. If not found, automatically creates the category via POST /wp-json/wp/v2/categories.
    4. Returns the valid integer category ID (defaults to 'Guides').
    """
    clean_name = category_name.strip()
    cache_key = clean_name.lower()

    if cache_key in _CATEGORY_CACHE:
        return _CATEGORY_CACHE[cache_key]

    categories_url = f"{WP_URL}/wp-json/wp/v2/categories"

    # Step 1: Search for existing category
    try:
        search_res = requests.get(
            categories_url,
            params={"search": clean_name},
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=DEFAULT_HEADERS,
            timeout=15
        )

        if search_res.status_code == 200:
            categories = search_res.json()
            for cat in categories:
                cat_name = cat.get("name", "").strip().lower()
                cat_slug = cat.get("slug", "").strip().lower()
                target_slug = clean_name.lower().replace(" ", "-")

                if cat_name == clean_name.lower() or cat_slug == target_slug:
                    cat_id = cat.get("id")
                    _CATEGORY_CACHE[cache_key] = cat_id
                    print(f"📁 Found existing WordPress category '{clean_name}' (ID: {cat_id})")
                    return cat_id

            # If search returned results and one starts with or matches closely
            if categories:
                cat_id = categories[0].get("id")
                _CATEGORY_CACHE[cache_key] = cat_id
                print(f"📁 Matched category '{clean_name}' -> '{categories[0].get('name')}' (ID: {cat_id})")
                return cat_id

    except Exception as e:
        print(f"Notice: Exception searching category '{clean_name}': {e}")

    # Step 2: If category doesn't exist, create it dynamically
    try:
        create_res = requests.post(
            categories_url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=DEFAULT_HEADERS,
            json={"name": clean_name},
            timeout=15
        )

        if create_res.status_code == 201:
            cat_data = create_res.json()
            cat_id = cat_data.get("id")
            _CATEGORY_CACHE[cache_key] = cat_id
            print(f"✨ Created new WordPress category '{clean_name}' (ID: {cat_id})")
            return cat_id
        elif create_res.status_code == 400:
            # Handle case where category exists under another slug / term_exists error
            err_data = create_res.json()
            term_id = err_data.get("data", {}).get("term_id")
            if term_id:
                _CATEGORY_CACHE[cache_key] = term_id
                print(f"📁 Retrieved existing term ID for '{clean_name}' (ID: {term_id})")
                return term_id

    except Exception as e:
        print(f"Notice: Exception creating category '{clean_name}': {e}")

    # Step 3: Safe fallback ID for "Guides" (ID: 4)
    fallback_id = 4
    _CATEGORY_CACHE[cache_key] = fallback_id
    return fallback_id


def upload_image_to_wordpress(image_path: str, title: str):
    """
    Uploads an image to the WordPress Media Library and sets alt_text and title.
    Returns (media_id, source_url).
    """
    if not os.path.exists(image_path):
        print(f"Warning: Image file not found: {image_path}")
        return None, None

    media_url = f"{WP_URL}/wp-json/wp/v2/media"
    headers = {
        **DEFAULT_HEADERS,
        'Content-Disposition': f'attachment; filename={os.path.basename(image_path)}'
    }

    try:
        with open(image_path, 'rb') as img_file:
            response = requests.post(
                media_url,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                headers=headers,
                files={'file': img_file},
                timeout=35
            )

        if response.status_code == 201:
            media_data = response.json()
            media_id = media_data.get('id')
            source_url = media_data.get('source_url', '')

            # Set alt_text and title matching the post title for image SEO
            requests.post(
                f"{media_url}/{media_id}",
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                headers=DEFAULT_HEADERS,
                json={
                    'alt_text': title,
                    'title': title,
                    'caption': title
                },
                timeout=15
            )
            print(f" -> Uploaded image: {image_path} (Media ID: {media_id})")
            return media_id, source_url
        else:
            print(f"Failed to upload image {image_path}: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Error uploading image {image_path}: {e}")
        return None, None


def generate_faq_accordion_html(faq_items: list) -> str:
    """
    Generates styled HTML <details> and <summary> accordion markup for 10 FAQs.
    Matches Easy Accordion styling:
    - Light gray background (#f5f5f5) for summary question box
    - Bold dark text
    - 15px padding
    - 10px bottom margin
    - White background with 15px padding for answer box
    """
    if not faq_items:
        return ""

    accordion_html = (
        '\n\n<div class="sp-easy-accordion-wrapper" style="margin-top: 35px; margin-bottom: 25px; font-family: inherit;">\n'
        '  <h2 class="h2dav">Frequently Asked Questions?</h2>\n'
    )

    for idx, item in enumerate(faq_items, start=1):
        if isinstance(item, dict):
            q = item.get("question", "")
            a = item.get("answer", "")
        else:
            q = f"Question {idx}"
            a = str(item)

        accordion_html += (
            f'  <details style="background: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px; margin-bottom: 10px; overflow: hidden;">\n'
            f'    <summary style="background: #f5f5f5; color: #222222; font-weight: bold; font-size: 16px; padding: 15px; cursor: pointer; outline: none; list-style: none; user-select: none;">\n'
            f'      {idx}. {q}\n'
            f'    </summary>\n'
            f'    <div style="background: #ffffff; color: #444444; padding: 15px; font-size: 15px; line-height: 1.6; border-top: 1px solid #eeeeee;">\n'
            f'      {a}\n'
            f'    </div>\n'
            f'  </details>\n'
        )

    accordion_html += '</div>\n'
    return accordion_html


def generate_faq_schema_jsonld(faq_items: list) -> str:
    """
    Generates strict Google-compliant JSON-LD FAQ Schema markup for the 10 FAQs.
    """
    if not faq_items:
        return ""

    main_entities = []
    for idx, item in enumerate(faq_items, start=1):
        if isinstance(item, dict):
            q = item.get("question", "")
            a = item.get("answer", "")
        else:
            q = f"Question {idx}"
            a = str(item)

        main_entities.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })

    schema_dict = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entities
    }

    schema_json = json.dumps(schema_dict, indent=2, ensure_ascii=False)
    return f'\n<script type="application/ld+json">\n{schema_json}\n</script>\n'


def publish_wordpress_post(
    title: str,
    content: str,
    image_paths: list,
    faq_items: list = None,
    category_name: str = "Guides",
    category_id: int = None
):
    """
    Publishes the blog post to WordPress strictly as a DRAFT.
    - Dynamically resolves category ID (defaulting to 'Guides') to completely eliminate 'Uncategorized'.
    - Uploads 3 images to WP Media Library.
    - Sets featured_media to Image 1.
    - Passes all 3 media IDs to gallery meta fields (boldthemes_theme_images, _override_images, etc.).
    - Does NOT append <img> tags to HTML body.
    - Sets Yoast SEO title and dynamic meta description.
    - Appends styled HTML FAQ Accordion (<details>/<summary>) and JSON-LD FAQ Schema.
    - Cleans up temporary local images after successful upload.
    """
    posts_url = f"{WP_URL}/wp-json/wp/v2/posts"

    # 1. Dynamically resolve category ID to ensure "Uncategorized" (ID 1) is never used
    if category_id is not None and int(category_id) != 1:
        target_category_id = int(category_id)
    else:
        target_category_id = get_or_create_category(category_name or "Guides")

    # 2. Upload the 3 images to the WordPress Media Library
    media_ids = []
    source_urls = []

    for path in image_paths:
        m_id, s_url = upload_image_to_wordpress(path, title)
        if m_id:
            media_ids.append(m_id)
            source_urls.append(s_url)

    featured_media_id = media_ids[0] if media_ids else 0
    media_ids_csv = ",".join(map(str, media_ids))

    # 3. Build full content: formatted body + FAQ Accordion + FAQ Schema (NO <img> tags in body)
    full_content = content.rstrip()

    if faq_items:
        faq_accordion_html = generate_faq_accordion_html(faq_items)
        faq_schema_script = generate_faq_schema_jsonld(faq_items)
        full_content += faq_accordion_html + faq_schema_script

    # 4. Yoast SEO Metadata
    yoast_title = title
    yoast_metadesc = extract_yoast_description(content)

    # 5. Build WordPress Post Payload with dynamically fetched category ID
    payload = {
        'title': title,
        'content': full_content,
        'status': 'draft',  # CRITICAL: Always published as draft
        'featured_media': featured_media_id,
        'categories': [target_category_id],
        'meta': {
            # Yoast SEO Meta
            '_yoast_wpseo_title': yoast_title,
            '_yoast_wpseo_metadesc': yoast_metadesc,
            # Theme Gallery Meta
            '_post_gallery': media_ids_csv,
            'boldthemes_theme_images': media_ids,
            '_boldthemes_theme_images': media_ids,
            '_override_images': media_ids_csv,
            '_bt_images': media_ids_csv,
            '_images': media_ids_csv,
            'images': media_ids_csv
        }
    }

    try:
        response = requests.post(
            posts_url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=DEFAULT_HEADERS,
            json=payload,
            timeout=35
        )

        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get('id')
            edit_url = f"{WP_URL}/wp-admin/post.php?post={post_id}&action=edit"
            preview_url = post_data.get('link', '')

            print(f"\n✅ Post successfully published as DRAFT! (Post ID: {post_id})")
            print(f"📁 Category Assigned      : ID {target_category_id} ({category_name})")
            print(f"📝 WordPress Edit URL     : {edit_url}")
            print(f"🌐 Post Preview URL      : {preview_url}")

            # Local cleanup after successful upload
            cleanup_local_images(image_paths)

            # Attach URLs to returned dictionary
            post_data['edit_url'] = edit_url
            post_data['preview_url'] = preview_url
            post_data['yoast_metadesc'] = yoast_metadesc
            post_data['media_ids'] = media_ids
            post_data['category_id'] = target_category_id

            return post_data
        else:
            print(f"❌ Failed to publish post: {response.status_code} - {response.text}")
            cleanup_local_images(image_paths)
            return None
    except Exception as e:
        print(f"❌ Exception during WordPress publication: {e}")
        cleanup_local_images(image_paths)
        return None