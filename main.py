from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import time

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
RESUME_FOLDER = os.getenv("RESUME_FOLDER")

# =====================================================
# VALIDATION
# =====================================================

if not EMAIL:
    raise Exception("EMAIL not found in .env")

if not PASSWORD:
    raise Exception("PASSWORD not found in .env")

if not RESUME_FOLDER:
    raise Exception("RESUME_FOLDER not found in .env")

# =====================================================
# NEW SKILLS LIST
# =====================================================

# Skills List
# Skills List
NEW_SKILLS = [
    "Data Engineering",
    "Pyspark",
    "Spark SQL",
    "Bigquery",
    "Python",
    "ETL Pipelines",
    "Data Ingestion",
    "Data Transformation",
    "Data Validation",
    "Apache Airflow",
    "AWS",
    "Google Cloud Platform (GCP)",
    "Big Data Processing",
    "Parquet Storage",
    "Window Functions",
    "Rest APIs",
    "Pandas",
    "Partitioning",
    "SQL"
]

# =====================================================
# GET PDF RESUME
# =====================================================

pdf_files = [
    f for f in os.listdir(RESUME_FOLDER)
    if f.endswith(".pdf")
]

if len(pdf_files) == 0:
    raise Exception("No PDF Resume Found")

resume_file = pdf_files[0]

resume_path = os.path.join(
    RESUME_FOLDER,
    resume_file
)

print(f"\nResume Found : {resume_path}")

# =====================================================
# START PLAYWRIGHT
# =====================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False, # False
        slow_mo=300
    )

    page = browser.new_page()

    # =================================================
    # OPEN NAUKRI
    # =================================================

    print("\nOpening Naukri...")

    page.goto(
        "https://www.naukri.com",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)

    print("Naukri Opened")

    # =================================================
    # LOGIN
    # =================================================

    print("\nLogging In...")

    page.locator("#login_Layer").click()

    page.wait_for_selector(
        'input[placeholder="Enter your active Email ID / Username"]'
    )

    # Email
    page.locator(
        'input[placeholder="Enter your active Email ID / Username"]'
    ).fill(EMAIL)

    # Password
    page.locator(
        'input[placeholder="Enter your password"]'
    ).fill(PASSWORD)

    # Login
    page.locator(
        'button[type="submit"]'
    ).click()

    print("Login Successful")

    page.wait_for_timeout(5000)

    # =================================================
    # OPEN PROFILE PAGE
    # =================================================

    print("\nOpening Profile...")

    page.goto(
        "https://www.naukri.com/mnjuser/profile",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(5000)

    print("Profile Opened")

    # =================================================
    # REPLACE RESUME
    # =================================================

    try:

        print("\nReplacing Resume...")

        page.wait_for_selector("#attachCV")

        upload_input = page.locator("#attachCV")

        # Existing Resume Automatically Replaced
        upload_input.set_input_files(resume_path)

        print("Resume Replaced Successfully")

        page.wait_for_timeout(5000)

        # Close Popup
        page.keyboard.press("Escape")

        page.wait_for_timeout(2000)

    except Exception as e:

        print("\nResume Replace Failed")

        print(e)

    # =================================================
    # OPEN SKILLS POPUP
    # =================================================

    try:

        print("\nOpening Skills Popup...")

        page.locator(
            '#lazyKeySkills .edit.icon'
        ).click(force=True)

        page.wait_for_timeout(5000)

        print("Skills Popup Opened")

    except Exception as e:

        print("\nSkills Popup Open Failed")

        print(e)

    # =================================================
    # REMOVE ALL SKILLS EXCEPT SQL
    # =================================================

    try:

        print("\nRemoving Existing Skills Except SQL...")

        while True:

            # ONLY VISIBLE SKILL TEXTS
            skill_texts = page.locator(
                '.chip .tagTxt'
            )

            count = skill_texts.count()

            print(f"Visible Skills Count : {count}")

            removed_any_skill = False

            for i in range(count):

                # Current Skill Text
                skill_text = skill_texts.nth(i).inner_text().strip()

                print(f"Found Skill : {skill_text}")

                # KEEP SQL
                if skill_text.lower() == "sql":

                    print("Keeping SQL Skill")

                    continue

                # Exact Current Chip
                current_chip = page.locator(
                    '.chip'
                ).filter(
                    has=page.locator(
                        '.tagTxt',
                        has_text=skill_text
                    )
                ).first

                # Remove Button
                remove_button = current_chip.locator(
                    'a.close'
                )

                # Remove Skill
                remove_button.click(force=True)

                print(f"Removed Skill : {skill_text}")

                page.wait_for_timeout(1500)

                removed_any_skill = True

                # DOM refresh after delete
                break

            # STOP WHEN ONLY SQL LEFT
            if not removed_any_skill:

                print("Only SQL Skill Remaining")

                break

    except Exception as e:

        print("\nExisting Skill Remove Failed")

        print(e)

    # =================================================
    # ADD NEW SKILLS
    # =================================================

    try:

        for skill in NEW_SKILLS:

            print(f"Adding Skill: {skill}")

            # Skill Input
            skill_input = page.locator(
                'input[placeholder="Add skills"]'
            )

            # Focus input
            skill_input.click()

            time.sleep(1)

            # Clear old text
            skill_input.fill("")

            time.sleep(1)

            # Type skill slowly
            skill_input.type(
                skill,
                delay=10 #20
            )

            print(f"Typed Skill: {skill}")

            # =================================================
            # WAIT FOR DROPDOWN
            # =================================================

            time.sleep(2)

            # =================================================
            # GET FIRST VISIBLE DROPDOWN ITEM
            # =================================================

            dropdown_items = page.locator("ul li")

            dropdown_count = dropdown_items.count()

            print("Dropdown Count:", dropdown_count)

            if dropdown_count > 0:

                first_dropdown = dropdown_items.nth(0)

                first_dropdown.scroll_into_view_if_needed()

                time.sleep(1)

                first_dropdown.click(force=True)

                print(f"Dropdown Clicked: {skill}")

            else:

                print(f"No Dropdown Found For: {skill}")

            # =================================================
            # WAIT UNTIL CHIP CREATED
            # =================================================

            skill_added = False

            for _ in range(15):

                chips = page.locator(".chip").all_text_contents()

                print("Current Chips:", chips)

                if any(skill.lower() in chip.lower() for chip in chips):

                    print(f"Skill Added In UI: {skill}")

                    skill_added = True

                    break

                time.sleep(1)

            if not skill_added:

                print(f"Skill Not Added Properly: {skill}")

            # WAIT BEFORE NEXT SKILL
            time.sleep(2)

        print("All Skills Added Successfully")

    except Exception as e:

        print("Skill Add Failed")

        print(e)

    # =================================================
    # SAVE SKILLS
    # =================================================

    try:

        time.sleep(2)

        save_button = page.locator(
            'button:has-text("Save")'
        ).last

        save_button.scroll_into_view_if_needed()

        time.sleep(2)

        save_button.click(force=True)

        print("Skills Saved Successfully")

    except Exception as e:

        print("Save Failed")

        print(e)

    # =================================================
    # WAIT AFTER SAVE
    # =================================================

    time.sleep(5)

    # =================================================
    # CLOSE BROWSER
    # =================================================

    browser.close()

    print("Automation Completed Successfully")