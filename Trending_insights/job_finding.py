import webbrowser

def get_job_search_url(role, platform):
    """Construct search URL for each platform with 'India' as the location."""
    job_search_urls = {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ', '%20')}&location=India",
        "Naukri": f"https://www.naukri.com/{role.replace(' ', '-').lower()}-jobs-in-india",
        "Foundit": f"https://www.foundit.in/search/jobs?q={role.replace(' ', '%20')}&l=India",
        "Indeed": f"https://www.indeed.co.in/jobs?q={role.replace(' ', '%20')}&l=India"
    }
    return job_search_urls.get(platform, "")

def search_jobs(role):
    """Search job vacancies sequentially on different platforms."""
    platforms = ["LinkedIn", "Naukri", "Indeed"]
    
    for platform in platforms:
        url = get_job_search_url(role, platform)
        
        # Print the search link for the current platform
        print(f"\nHere is the link for '{role}' jobs on {platform}: {url}")
        
        # Ask user if they found the job after clicking the link
        response = input(f"Did you find the job on {platform}? (yes/no): ").strip().lower()

        if response == "yes":
            print(f"Great! Here is the link for the job: {url}")
            return  # Terminate the script once the user finds the job

        print(f"No vacancies found on {platform}. Moving to the next platform...\n")
    
    # If no vacancies found after checking all platforms:
    print("\nNo vacancies found on any platform.")

def main():
    """Main function to get job role input and start the search."""
    role = input("Enter the job role you are looking for (e.g., Data Analyst): ")
    
    # Start the job search and return the first platform link with vacancies
    search_jobs(role)

if __name__ == "__main__":
    main()
