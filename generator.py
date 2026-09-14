import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Strict verbatim client rules for system prompt
SYSTEM_PROMPT = (
    "Write SEO blog posts for My Car Collision Center. "
    "Tone: Natural, human, active voice, short simple sentences. "
    "Do NOT use em dashes, AI-style labels, or generic intros. "
    "Length: ~1,200 words. Structure: Question-based H2 headings. "
    "Business info: My Car Collision Center (NOT Auto Group), locations in Glendale/Studio City, "
    "phone (747) 444-0040, website https://www.mycarautogroup.com. "
    "Focus strictly on local SEO, accurate manufacturer repair facts, and never invent certifications. "
    "CRITICAL LENGTH RULE: You MUST write 3 to 4 detailed paragraphs under EVERY SINGLE H2 to ensure "
    "the article reaches 1,200+ words. No brief summaries."
)

# Standard curated 12 FAQs strictly meeting David's exact specifications
FALLBACK_12_FAQS = [
    {
        "question": "What does being a Genesis Certified Collision Center mean for My Car Collision Center in Glendale?",
        "answer": "My Car Collision Center in Glendale has earned official Genesis Certification by investing in factory-mandated repair equipment, diagnostic tooling, and specialized technician training. This prestigious certification verifies that our facility strictly adheres to Genesis factory repair guidelines for all collision repairs. Vehicle owners in Glendale can trust that their luxury Genesis is restored with precision craftsmanship that preserves its structural safety and manufacturer warranty."
    },
    {
        "question": "Does My Car Collision Center use genuine OEM parts for Genesis repairs?",
        "answer": "Yes, our Glendale collision center exclusively utilizes 100% genuine Genesis OEM parts engineered specifically for your vehicle model. Using authentic manufacturer components ensures precise fitment, structural integrity, and uncompromised factory crash-test performance. We never cut corners with inferior aftermarket or salvage parts when repairing your Genesis luxury vehicle."
    },
    {
        "question": "What collision and body repair services do you provide for Genesis vehicles in Glendale?",
        "answer": "My Car Collision Center offers complete structural collision repair, bumper reconstruction, aluminum body panel replacement, and mechanical suspension rebuilding. Our Glendale facility is equipped with advanced laser-guided measuring benches and computerized alignment systems to handle any severity of accident damage. Every repair is performed in strict compliance with Genesis factory engineering specifications to guarantee showroom condition."
    },
    {
        "question": "How does My Car Collision Center assist with Genesis auto insurance claims?",
        "answer": "Our dedicated claims specialists in Glendale work directly with all major insurance providers to streamline the entire claim and estimate approval process. We prepare comprehensive itemized estimates using Genesis OEM repair procedures and submit all necessary digital supplement documentation on your behalf. Our team actively advocates for your safety so you never have to deal with insurance adjusters alone."
    },
    {
        "question": "Why is ADAS sensor calibration essential after a Genesis collision repair?",
        "answer": "Genesis luxury vehicles rely on sensitive cameras, radar sensors, and ultrasonic units to operate advanced driver assistance safety features. Following any bumper repair, unibody adjustment, or windshield replacement, our Glendale technicians perform computerized static and dynamic ADAS recalibrations using factory targets. This rigorous calibration ensures your Genesis collision avoidance and lane departure systems respond with absolute accuracy on California roads."
    },
    {
        "question": "Does My Car Collision Center offer a warranty on Genesis repairs?",
        "answer": "Yes, all collision repairs, structural work, and paint refinishing performed at My Car Collision Center come with a comprehensive written lifetime warranty. This warranty protects our Glendale clients for as long as they own their Genesis vehicle. We stand behind our certified repair quality, expert craftsmanship, and factory-approved refinishing materials."
    },
    {
        "question": "What is the typical repair timeline for a damaged Genesis at your Glendale shop?",
        "answer": "Repair turnaround times vary depending on the extent of damage and OEM parts delivery, with minor cosmetic repairs taking 2 to 4 business days. Complex unibody and structural rebuilds typically require 1 to 2 weeks to complete thorough diagnostic scans, repairs, and quality inspections. Our Glendale team provides frequent automated status updates so you always know the exact progress of your Genesis vehicle."
    },
    {
        "question": "Can My Car Collision Center repair complex aluminum Genesis body panels?",
        "answer": "Yes, our Glendale collision center features a dedicated aluminum repair station equipped with specialized clean-room tooling to prevent cross-contamination. Genesis models incorporate advanced high-strength aluminum alloys that require specialized dent-pulling equipment, pulsed MIG welders, and certified structural bonding techniques. Our factory-trained technicians possess the advanced certifications required to safely repair lightweight Genesis aluminum architectures."
    },
    {
        "question": "How do you achieve a flawless factory paint match on Genesis vehicles?",
        "answer": "Our Glendale facility utilizes digital spectrophotometer computerized paint-matching technology to accurately analyze your exact Genesis factory color formulation. We mix premium OEM-approved waterborne paint formulas and apply them inside climate-controlled downdraft spray booths for a pristine finish. Multiple layers of durable clear coat are baked in curing ovens to ensure a mirror-like shine that matches factory standards."
    },
    {
        "question": "Do you provide emergency towing and after-hours vehicle drop-off in Glendale?",
        "answer": "Yes, My Car Collision Center provides 24/7 towing coordination and secure after-hours key drop-off services for drivers throughout Glendale and surrounding areas. When an unexpected accident occurs, simply call our emergency assistance line at (747) 444-0040 to arrange immediate vehicle transport. Your Genesis will be stored in our secure, monitored facility until our estimators begin your comprehensive inspection."
    },
    {
        "question": "What specialized diagnostic tooling and technician training do you maintain?",
        "answer": "Our technicians undergo continuous I-CAR and Genesis factory training to stay up to date with the latest luxury vehicle engineering advances. We utilize factory diagnostic scanners, OEM unibody alignment jigs, and computerized spot-welding systems calibrated specifically for Genesis platforms. This state-of-the-art diagnostic infrastructure guarantees that all electronic, mechanical, and safety modules operate according to manufacturer standards."
    },
    {
        "question": "How can I schedule a Genesis collision repair estimate in Glendale?",
        "answer": "You can easily schedule an in-person estimate by calling our Glendale facility directly at (747) 444-0040 or submitting a request online at https://www.mycarautogroup.com. Our friendly staff will walk you through the intake process, inspect your vehicle, and arrange a convenient rental car reservation. We are proud to serve Glendale drivers with premier certified Genesis collision repair and unmatched customer care."
    }
]


def generate_article_content(topic_title: str) -> str:
    """
    Generates a high-quality, comprehensive SEO blog post adhering to strict client rules.
    - max_tokens >= 4000 to prevent cut-offs.
    - Question-based H2 headings.
    - 3-4 detailed paragraphs per H2 heading.
    - 1,200+ words total.
    """
    user_prompt = f"""
Write an in-depth, authoritative SEO blog post for My Car Collision Center about: "{topic_title}".

Strict Article Requirements:
1. Every major section must start with a question-based H2 heading ending in a question mark (e.g., '## Why Is Certified Collision Repair Essential for Modern Vehicles?').
2. Include at least 5 to 7 question-based H2 sections.
3. Under EVERY SINGLE H2 heading, write 3 to 4 comprehensive, well-developed paragraphs explaining repair techniques, safety considerations, insurance procedures, or OEM standards.
4. Keep individual sentences short, punchy, and natural. Avoid filler phrases, em dashes (—), and artificial AI introductions.
5. Emphasize Glendale and Studio City local automotive repair expertise, manufacturer specifications, and the contact number (747) 444-0040.
6. Do not include an FAQ section in this body content (the FAQ is generated separately).
7. Total word count must be 1,200+ words.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=4200,
        temperature=0.7
    )

    return response.choices[0].message.content


def generate_faqs(topic_title: str) -> list:
    """
    Generates 12 questions and answers following David's exact specifications:
    - 12 questions and answers about Genesis Certified Collision Center services for Glendale, CA.
    - Focus exclusively on My Car Collision Center (do not mention other centers).
    - Requirements for every answer: Exactly 3 sentences, professional/helpful tone,
      emphasizing Genesis Certification, OEM parts, factory procedures, and Glendale service.
    - Must cover the 12 specified topics (Genesis certification, OEM parts, services, insurance,
      ADAS calibration, warranty, timelines, aluminum structural repair, paint matching,
      emergency towing/drop-off, diagnostic tooling/training, scheduling/contact).
    - Strictly follows this output format:
      Q1: [Question]
      [Answer – exactly 3 sentences]
    """
    prompt = f"""
Generate 12 questions and answers about Genesis Certified Collision Center services for Glendale, CA related to: "{topic_title}".

Strict Client Specifications:
1. Focus exclusively on My Car Collision Center in Glendale, CA (do not mention other centers).
2. Requirements for every answer: EXACTLY 3 sentences. Professional and helpful tone. Emphasize Genesis Certification, genuine OEM parts, factory procedures, and Glendale local service.
3. Must cover these 12 specified topics:
   - Q1: Genesis Certified Collision Center status & what it means
   - Q2: Genuine OEM Genesis parts usage
   - Q3: Full range of collision and body repair services in Glendale
   - Q4: Working with auto insurance companies & claim handling
   - Q5: ADAS (Advanced Driver Assistance Systems) calibration & safety sensors
   - Q6: Lifetime warranty on body and paint repairs
   - Q7: Repair timelines & turnaround estimates
   - Q8: Aluminum structural repair & unibody straightening
   - Q9: Factory paint matching & computerized spray booths
   - Q10: Emergency towing coordination & 24/7 vehicle drop-off in Glendale
   - Q11: Specialized Genesis diagnostic tooling, equipment & certified technicians
   - Q12: How to schedule an estimate or contact the Glendale center (747) 444-0040 / https://www.mycarautogroup.com

Strict Output Format:
You MUST follow this exact format for all 12 items:
Q1: [Question text]
[Answer text – exactly 3 sentences]

Q2: [Question text]
[Answer text – exactly 3 sentences]

...

Q12: [Question text]
[Answer text – exactly 3 sentences]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized automotive collision repair expert who writes exactly 12 structured Q&As adhering strictly to 3-sentence answers and the specified Q1-Q12 format."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.6
        )

        raw_text = response.choices[0].message.content.strip()

        # Parse Q1..Q12 format
        pattern = re.compile(r'Q\d+:\s*(.*?)\n\s*(.*?)(?=(?:\n\s*Q\d+:|$))', re.DOTALL)
        matches = pattern.findall(raw_text)

        parsed_faqs = []
        for q, a in matches:
            clean_q = q.strip()
            clean_a = re.sub(r'\s*\n\s*', ' ', a.strip())
            if clean_q and clean_a:
                parsed_faqs.append({"question": clean_q, "answer": clean_a})

        if len(parsed_faqs) >= 12:
            return parsed_faqs[:12]
        elif len(parsed_faqs) > 0:
            # Fill remaining with standard curated FAQs
            for fallback in FALLBACK_12_FAQS:
                if len(parsed_faqs) >= 12:
                    break
                if not any(f["question"] == fallback["question"] for f in parsed_faqs):
                    parsed_faqs.append(fallback)
            return parsed_faqs[:12]

    except Exception as e:
        print(f"Notice: Dynamic FAQ generation fallback ({e}). Using David's exact curated 12 FAQs.")

    return list(FALLBACK_12_FAQS)


# Backward compatibility alias
generate_faq_items = generate_faqs