import argparse
import os
import json
import time
from src.resume_utils import load_resume_text # Replaces src.parser
from src.ollama_client import check_connection
from src.agent import process_job_application
from src.browser import BrowserEngine
from src.platforms.linkedin import LinkedIn

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def interactive_wizard():
    print("\n--- Jobaru Interactive Agent Setup ---")
    config = load_config()
    
    # RESUME SETUP
    if 'resume_path' not in config or not os.path.exists(config['resume_path']):
        while True:
            # Check for existing resume.txt from previous recovery
            if os.path.exists("resume.txt") and 'resume_path' not in config:
                print("Found 'resume.txt' in current directory.")
                if input("Use 'resume.txt'? (y/n): ").lower() == 'y':
                     config['resume_path'] = os.path.abspath("resume.txt")
                     config['resume_text'] = load_resume_text("resume.txt")
                     break

            path = input("Where is your resume? (path to PDF/TXT, or type 'paste' to enter text): ").strip()
            
            if path.lower() == 'paste':
                print("Paste your resume below. Type 'DONE' on a new line when finished:")
                lines = []
                while True:
                    line = input()
                    if line.strip() == 'DONE':
                        break
                    lines.append(line)
                
                content = "\n".join(lines)
                with open("resume.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                
                config['resume_path'] = os.path.abspath("resume.txt")
                config['resume_text'] = content
                print("Saved pasted text to resume.txt and loaded successfully.")
                break

            elif os.path.exists(path):
                config['resume_path'] = os.path.abspath(path)
                try:
                    config['resume_text'] = load_resume_text(path)
                    print("Resume loaded successfully.")
                    break
                except Exception as e:
                    print(f"Error reading file: {e}")
            else:
                print("File not found. Please try again.")
    else:
        print(f"Using resume: {config['resume_path']}")
        if 'resume_text' not in config:
             config['resume_text'] = load_resume_text(config['resume_path'])

    # JOB PREFERENCES
    if 'job_role' not in config:
        print("\n--- Role Selection ---")
        use_ai = input("Do you want me to analyze your resume and suggest job roles? (y/n): ").lower()
        
        selected_role = None
        if use_ai == 'y':
            from src.agent import suggest_roles_from_resume
            print("Analyzing resume... (this may take a few seconds)")
            print(f"Resume text length: {len(config.get('resume_text', ''))} chars")
            
            suggestions = suggest_roles_from_resume(config['resume_text'], config.get('model', 'mistral'))
            if suggestions:
                print("\nSuggested Roles:")
                for i, role in enumerate(suggestions):
                    print(f"{i+1}. {role}")
                print(f"{len(suggestions)+1}. Type my own")
                
                choice = input("Select a role (number): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                    selected_role = suggestions[int(choice)-1]
        
        if selected_role:
            config['job_role'] = selected_role
        else:
            config['job_role'] = input("What job role should I search for? (e.g. Python Developer): ").strip()
            
    else:
        print(f"Target Role: {config['job_role']}")
        if input("Change role (or analyze resume)? (y/n): ").lower() == 'y':
             # Offer AI here too?
             if input("Suggest from resume? (y/n): ").lower() == 'y':
                 from src.agent import suggest_roles_from_resume
                 suggestions = suggest_roles_from_resume(config['resume_text'], config.get('model', 'mistral'))
                 print("\nSuggested Roles:")
                 for i, role in enumerate(suggestions):
                    print(f"{i+1}. {role}")
                 print(f"{len(suggestions)+1}. Type my own")
                 c = input("Select: ").strip()
                 if c.isdigit() and 1 <= int(c) <= len(suggestions):
                     config['job_role'] = suggestions[int(c)-1]
                 else:
                     config['job_role'] = input("New role: ").strip()
             else:
                config['job_role'] = input("New role: ").strip()

    if 'location' not in config:
        config['location'] = input("Target Location? (e.g. Remote, San Francisco): ").strip()
    else:

        print(f"Target Location: {config['location']}")
        user_input = input("Change location? (enter new location or press Enter to keep): ").strip()
        if user_input:
            config['location'] = user_input

    # ACTION MODE: DRAFT or APPLY,
    if 'auto_apply' not in config:
        print("\n--- Action Mode ---")
        print("1. Draft Only (Generate cover letters/emails locally)")
        print("2. Auto Apply (Draft AND click Apply buttons - Experimental)")
        choice = input("Select mode (1/2): ").strip()
        config['auto_apply'] = (choice == '2')

    # OLLAMA SETUP
    if 'model' not in config:
        config['model'] = "mistral"
        
    save_config(config)
    return config

def run_agent_loop(config):
    """
    Main autonomous loop:
    1. Launch Browser
    2. Manual Login (to avoid bot detection)
    3. Search & Scrape
    4. AI Processing
    """
    print("\n--- Starting Autonomous Agent Loop ---")
    print("1. Launching Browser...")
    browser = BrowserEngine(headless=False)
    
    try:
        # LOGIN
        print("2. Please log in to LinkedIn in the opened browser window.")
        browser.navigate("https://www.linkedin.com/login")
        
        # Simple wait for manual login
        input("Please log in to LinkedIn in the browser window manually.\nPress Enter after you have logged in...")
        
        # SEARCH
        print(f"3. Searching for '{config['job_role']}' in '{config['location']}'...")
        linkedin = LinkedIn(browser, config)
        jobs = linkedin.search_jobs(config['job_role'], config['location'])
        
        if not jobs:
            print("No jobs found. Exiting loop.")
            return

        print(f"\nFound {len(jobs)} potential jobs. Starting processing...\n")
        
        # PROCESS JOBS
        applications_dir = os.path.join(os.getcwd(), "applications")
        os.makedirs(applications_dir, exist_ok=True)

        for i, job in enumerate(jobs):
            print(f"[{i+1}/{len(jobs)}] Processing: {job['title']}")
            print(f"   {job['title']} at {job['company']}")
            print(f"   URL: {job['url']}")

            browser.navigate(job['url'])
            time.sleep(2)
            
            # Robust description extraction
            job_desc = ""
            
            # 1. Try to expand the description first
            try:
                # Look for "Show more" button
                expand_btns = [
                    browser.find_element("[data-testid='expandable-text-button']"),
                    browser.find_element(".jobs-description__footer-button"),
                    browser.find_element(".show-more-less-html__button")
                ]
                for btn in expand_btns:
                    if btn:
                        browser.driver.execute_script("arguments[0].click();", btn)
                        print("   [DEBUG] Clicked 'Show more' button.")
                        time.sleep(1)
                        break
            except:
                pass # It might be already expanded or not present

            # 2. Extract text from various containers
            selectors = [
                "[data-testid='expandable-text-box']",
                ".jobs-description__content",
                ".jobs-box__html-content",
                "#job-details",
                ".description__text",
                ".show-more-less-html__markup",
                "article.jobs-description__container",
                ".job-view-layout .jobs-description"
            ]
            
            for sel in selectors:
                try:
                    el = browser.find_element(sel)
                    if el and len(el.text) > 50:
                        job_desc = el.text
                        print(f"   [DEBUG] Extracted description using: {sel}")
                        break
                except:
                    continue
            
            if not job_desc:
                job_desc = "Description not found."

            print(f"   Description Length: {len(job_desc)} chars")
            
            if len(job_desc) < 100:
                print("   Skipping: Insufficient description.")
                # Save debug HTML to understand why
                debug_dir = os.path.join("applications", "debug_html")
                os.makedirs(debug_dir, exist_ok=True)
                with open(os.path.join(debug_dir, f"fail_{i}.html"), "w", encoding="utf-8") as f:
                    f.write(browser.get_source())
                print(f"   [DEBUG] Saved page source to {debug_dir}/fail_{i}.html for inspection.")
                continue

            # AI Processing
            print("   Using Ollama to analyze and draft...")
            result = process_job_application(config['resume_text'], job_desc, model=config['model'])
            
            if "error" in result:
                print(f"   Error in analysis: {result['error']}")
                continue
                
            # Saving
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_title = "".join([c for c in job.get('title', 'job') if c.isalnum() or c==' ']).strip().replace(' ', '_')
            output_dir = os.path.join("applications", f"{timestamp}_{safe_title}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save Cover Letter
            with open(os.path.join(output_dir, "cover_letter.md"), "w", encoding="utf-8") as f:
                f.write(str(result["materials"].get("cover_letter", "")))
            
            # Save Metadata
            with open(os.path.join(output_dir, "job_data.json"), "w", encoding="utf-8") as f:
                json.dump({**job, "analysis": result}, f, indent=2)
                
            print(f"   Success! Saved to {output_dir}")
            
            # AUTO APPLY
            if config.get('auto_apply'):
                print("   [Auto-Apply] Attempting to apply...")
                try:
                    # Get the cover letter text we just generated
                    cl_text = result["materials"].get("cover_letter", "")
                    linkedin.apply_to_job(job['url'], cover_letter=cl_text)
                except Exception as e:
                    print(f"   [Auto-Apply] Failed: {e}")
            
            print("   Waiting 5s before next job...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nUser stopped the agent.")
    except Exception as e:
        print(f"\nCritical Error: {e}")
    finally:
        browser.quit()
        print("Browser closed. Session ended.")

def main():
    parser = argparse.ArgumentParser(description="Jobaru - Autonomous Agent")
    parser.add_argument("--reset", action="store_true", help="Reset configuration")
    args = parser.parse_args()
    
    print("Initializing Jobaru...")
    if not check_connection():
        print("ERROR: Ollama is not running. Please start Ollama first.")
        return

    if args.reset and os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("Configuration reset.")

    config = interactive_wizard()
    run_agent_loop(config)

if __name__ == "__main__":
    main()
