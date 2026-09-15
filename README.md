# 🚀 AI-Powered WordPress SEO Publisher & Media Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![WordPress](https://img.shields.io/badge/WordPress-REST%20API-0073AA.svg)](https://developer.wordpress.org/rest-api/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A modern, production-grade automated publishing system built with **Streamlit**, **Python**, and the **WordPress REST API**. Designed for automotive collision centers and high-authority niche publishers, this tool automates long-form SEO blog drafting (1,200+ words), dynamic branded image generation, category resolution, Yoast SEO metadata binding, and media asset deployment directly into WordPress as clean drafts.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Important Architectural Decision (Design Boundary)](#-important-architectural-decision-design-boundary)
- [Project Structure](#-project-structure)
- [Installation & Setup Guide](#-installation--setup-guide)
- [Usage Guide](#-usage-guide)
- [Configuration Reference](#-configuration-reference)
- [Security & Best Practices](#-security--best-practices)

---

## 🌟 Overview

Drafting high-ranking SEO content with custom branded images, proper schema injection, and clean HTML structure is typically a time-consuming manual workflow. 

This automation platform streamlines the entire pipeline into a zero-touch or one-click Streamlit dashboard:
1. **Topic Ingestion**: Accepts individual keywords or reads batch queues directly from Google Sheets.
2. **Comprehensive Content Generation**: Generates 1,200+ word structured articles utilizing GPT-4o with question-based `<h2>` headings, contextual shortcode placement, and exact FAQ schemas.
3. **Dynamic Asset Generation**: Fetches relevant background photos, applies contrast readability masks, renders Montserrat bold typography overlays, and stamps official branding badges.
4. **Direct WordPress REST Deployment**: Uploads assets to the Media Library, maps featured images, assigns categories, populates Yoast SEO titles/meta descriptions, and safely creates **Draft** posts.

---

## ✨ Key Features

- **🤖 Automated Long-Form SEO Content Generation**
  - Generates comprehensive, search-optimized articles (1,200+ words) with rich paragraph depth.
  - Enforces client-specific formatting standards (`<h2 class="h2dav">Question?</h2>`).
  - Generates 12 curated Genesis-certified collision center FAQs with styled HTML accordion details and matching Google-compliant JSON-LD schema markup.

- **🎨 Automated Media & Branded Image Pipeline**
  - Generates 3 branded high-resolution images per post with dynamic readability gradients and centered typography.
  - Automatically cleans up local temporary image files after successful WordPress uploads.

- **🔌 Direct Media Library & Post Draft Integration**
  - Uploads generated images directly to `/wp-json/wp/v2/media` and sets SEO alt text, title, and captions.
  - Binds the primary image ID to `featured_media` and `_thumbnail_id`.
  - Automatically resolves and creates target WordPress categories (e.g., *Guides*).
  - Configures Yoast SEO metadata (`_yoast_wpseo_title` and dynamic `_yoast_wpseo_metadesc` with direct phone CTA).
  - Posts are strictly published with `status: 'draft'` to ensure editorial safety before going live.

- **🛡️ Cloudflare & Security Bypass Mechanics**
  - Uses realistic browser `User-Agent` headers to prevent 403 Forbidden rejections from Cloudflare WAF or security plugins.
  - Authenticates securely via native WordPress Application Passwords (HTTP Basic Auth) without exposing raw user account passwords.

- **🖥️ Interactive Streamlit Dashboard**
  - **Single Post Studio**: Live input, full parameter customization, real-time generation progress, and instant WordPress Edit/Preview links.
  - **Batch Queue Automation**: Automated sequential processing from public or private Google Sheets.
  - **Post Meta Inspector**: Diagnostic utility to query existing WordPress posts via the REST API and inspect raw post meta, ACF fields, and media links in real time.

---

## 🏛️ Important Architectural Decision (Design Boundary)

### Why Theme-Specific Custom Fields Require a Decoupled Boundary

In custom WordPress themes (such as those powered by BoldThemes or custom agency frameworks), certain UI elements rely on proprietary custom post meta fields:
- **Custom Image Gallery Grid**: `boldthemes_theme_images`
- **Header Script Injection Box**: `_inpost_head_script[synth_header_script]` / `synth_header_script`

#### WordPress REST API Security Constraint
By default, the WordPress Core REST API controller (`WP_REST_Posts_Controller`) strictly sanitizes and filters out any custom meta keys sent in `payload['meta']` **unless** those keys have been explicitly registered in PHP via `register_post_meta()` with `'show_in_rest' => true`. 

When custom theme developers define meta boxes using standard PHP hooks without REST API registration, WordPress silently drops those keys during `POST /wp-json/wp/v2/posts` requests to protect database integrity.

#### The Architectural Solution
To preserve long-term site stability and avoid modifying proprietary theme core files:
1. **Zero-Touch Core**: Our API payload safely passes custom attributes (`custom_grid_images` and `custom_faq_schema`) as top-level parameters or through a lightweight server-side PHP interceptor snippet in `functions.php`.
2. **Clean Fallback Boundary**: The application provides the generated Media IDs (e.g., `7294, 7295, 7296`) and the clean JSON-LD FAQ schema directly in the Streamlit UI and terminal logs. If the theme is updated or restored to stock settings, editors can perform a 5-second copy-paste into the theme boxes without risking database corruption or site breakage during theme updates.

This design boundary ensures our automation remains **robust, non-destructive, and resilient against future WordPress theme updates**.

---

## 📂 Project Structure

```text
wp-ai-seo-publisher/
├── app.py                  # Streamlit Web UI (Single generation, Batch queue, Post inspector)
├── generator.py            # OpenAI GPT-4o content & FAQ schema generator engine
├── processor.py            # HTML sanitation, shortcode distribution & internal link injection
├── image_maker.py          # Dynamic branded image generator with PIL & typography overlay
├── wp_publisher.py         # WordPress REST API publishing client & media uploader
├── diagnose_post.py        # Diagnostic script to inspect WordPress REST API post meta
├── debug.py                # Quick connection and authentication verification script
├── blog.post--2026.jpeg    # Template image background asset
├── Montserrat-Black.ttf    # Typography font for dynamic image generation
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules (protects credentials & local virtualenv)
└── README.md               # Project documentation
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- An active **OpenAI API Key** with access to GPT-4o.
- A **WordPress Site (v5.6+)** with REST API enabled and an **Application Password** generated for your user account.

### 2. Clone the Repository
```bash
git clone https://github.com/hitttu01/wp-ai-seo-publisher.git
cd wp-ai-seo-publisher
```

### 3. Create and Activate a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / PowerShell)
# python -m venv venv
# venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create your local `.env` configuration file by copying `.env.example`:

```bash
cp .env.example .env
```

Open `.env` in your text editor and provide your credentials:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# WordPress REST API Configuration
WP_SITE_URL=https://yourwordpresssite.com
WP_USERNAME=YourWordPressUsername
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

> **How to create a WordPress Application Password:**  
> 1. Log in to your WordPress Admin Dashboard.  
> 2. Go to **Users** -> **Profile** (or **All Users** -> Edit your user).  
> 3. Scroll down to the **Application Passwords** section.  
> 4. Enter a name (e.g., `Streamlit Automation`) and click **Add New Application Password**.  
> 5. Copy the generated 24-character password and paste it into `WP_APP_PASSWORD` in `.env`.

---

## 🚀 Usage Guide

### Running the Streamlit Web Application

Launch the interactive dashboard:

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

### Dashboard Tabs

1. **⚡ Single Post Generator**:
   - Enter your target article topic or keyword.
   - Select the target category (default: *Guides*).
   - Click **Generate & Publish Draft**.
   - Monitor the step-by-step progress bar (Content Generation ➔ Image Branding ➔ Media Upload ➔ WordPress Draft Publishing).
   - Access direct links to **Edit in WordPress** or **Preview Draft**.

2. **📊 Batch Queue Runner**:
   - Connect a Google Sheet containing pending topics.
   - Run sequential batch publishing with automatic retry mechanisms and error tracking.

3. **🔎 Post Meta Inspector**:
   - Enter any WordPress Post ID (e.g., `7291`).
   - Query the live REST API to inspect registered post meta, categories, media bindings, and custom fields for diagnostic purposes.

---

## 🔧 Diagnostics & Command-Line Tools

You can also run quick diagnostic checks directly from the command line:

```bash
# Test REST API connection and inspect a specific post
python diagnose_post.py

# Verify authentication against WordPress
python debug.py
```

---

## 🔒 Security & Best Practices

- **Never commit `.env`**: Credentials, application passwords, and OpenAI API keys are excluded via `.gitignore`.
- **Restricted Privileges**: Use an Application Password scoped to an Editor or Administrator account specifically for publishing tasks.
- **Draft Status Enforcement**: All automated posts are created with `'status': 'draft'` by default to ensure review before publishing.
- **Sanitized HTML Body**: JSON-LD scripts and raw `<img>` tags are completely stripped from the main body content to prevent rendering glitches in the Gutenberg/Classic editor.

---

## 👥 Authors & Maintainers

- **Hitesh Yadav** - *Lead Automation Engineer & Pipeline Developer*
- Project Repository: [wp-ai-seo-publisher](https://github.com/hitttu01/wp-ai-seo-publisher)