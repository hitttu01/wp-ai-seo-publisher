# 🚀 Automated WordPress Publishing & Dynamic Branding Pipeline

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg) ![WordPress](https://img.shields.io/badge/WordPress-REST_API-0073AA.svg) ![Automation](https://img.shields.io/badge/Status-Fully_Automated-brightgreen.svg)

An end-to-end Python automation pipeline that dynamically processes blog content, generates fully branded text-overlay images, and publishes directly to WordPress with custom meta-field integration.

![Pipeline Demo Screenshot](generated_image_1.jpg)

---

## ✨ Key Features

* **📝 Smart Content Formatting:** Automatically cleans markdown, enforces strict internal linking rules, and injects custom client HTML tags (e.g., `<h2 class="h2dav">`).
* **🎨 Dynamic Image Engine:** Fetches context-relevant background photos, applies a readability overlay, auto-wraps bold title text, and precisely stamps corporate logos.
* **🔌 WordPress REST API Integration:** Uploads media securely, assigns featured images, populates custom Meta Box fields (`boldthemes_theme_images`), and publishes categorized drafts.
* **🤖 100% Hands-Off:** Just provide the titles; the system handles the API requests, image manipulation (via `Pillow`), and publishing automatically.

---

## 📂 Project Structure

```text
├── main.py                 # The central execution loop & Google Sheets queue reader
├── generator.py            # AI content generation via OpenAI GPT-4o
├── processor.py            # Text cleaning, markdown removal & HTML link mapping
├── image_maker.py          # Dynamic image fetching, text wrapping & branding
├── wp_publisher.py         # WordPress REST API media upload & post publishing
├── blog.post--2026.jpeg    # Base template containing the corporate footer
├── Montserrat-Black.ttf    # Auto-downloaded font for image titles
├── .env.example            # Template for required environment variables
└── requirements.txt        # Python dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your machine.

### 2. Create Virtual Environment & Install Dependencies
Open your terminal, navigate to this project folder, and run:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory by copying the example template:

```bash
cp .env.example .env
```

Open `.env` and fill in your actual credentials:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# WordPress REST API Configuration
WP_SITE_URL=https://yourwordpresssite.com
WP_USERNAME=your_wordpress_username
WP_APP_PASSWORD=your_wordpress_application_password
```

---

## 🚀 How to Run the Pipeline

Once your `.env` file is set up and the virtual environment is active, execute the main script:

```bash
python main.py
```

*(Or run directly via the virtual environment binary: `./venv/bin/python main.py`)*

---

## 🔄 What Happens Next?

1. **Queue Ingestion:** `main.py` fetches the topic list directly from Google Sheets.
2. **AI Generation:** `generator.py` drafts the comprehensive article and FAQ section.
3. **Text Formatting:** `processor.py` strips markdown asterisks, enforces 24/7 branding, and maps internal links.
4. **Dynamic Image Branding:** `image_maker.py` fetches 3 relevant photos, overlays 60% readability banners, centers Montserrat bold text, and stamps the client logo banner.
5. **WordPress Publishing:** `wp_publisher.py` uploads media to WordPress, sets the featured image, fills custom fields (`boldthemes_theme_images`), and publishes the draft.

---

## 🛠️ Built By

**Hitesh Yadav**  
*Automation Pipeline Developer*