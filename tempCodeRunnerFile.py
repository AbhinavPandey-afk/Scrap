pdf_links = []
        # generated_url = get_pdf_link(bank_name,quarter,year)
        # if generated_url:
        #     pdf_links.append(generated_url)
        #     print("Direct PDF found from hardcoded company_sources.")
        #     print(f"[PDF SELECTED]: {generated_url}")
        # else:
        #     investor_urls = find_investor_url(bank_name)
        #     if len(investor_urls) == 0:
        #         return "Investor site not found. Please try again."

        #     keywords = ("revenue", "results", "quarterly", "fact sheet", "Analyst Datasheet")
        #     for investor_url in investor_urls:
        #         pdf_links += find_presentation_pdf(investor_url, keywords)

        #     print("PDFs found:", pdf_links)

        # # 🔧 FILTERING STRICTLY FOR QUARTER + YEAR
        # filtered_links = []
        # for link in pdf_links:
        #     link_lower = link.lower()
        #     if str(year) in link_lower and (f"q{quarter}" in link_lower or f"{quarter}" in link_lower):
        #         filtered_links.append(link)

        # # fallback if strict filter returns nothing
        # if not filtered_links:
        #     print("⚠ No strictly matching PDFs found for year & quarter, falling back to year-only filtering.")
        #     for link in pdf_links:
        #         if str(year) in link.lower():
        #             filtered_links.append(link)

        # if not filtered_links:
        #     print("⚠ No PDFs found after filtering, using first 5 found as backup.")
        #     filtered_links = pdf_links[:5]

        # pdf_links = filtered_links

        # print("✅ Final PDFs selected for extraction:")
        # for idx, link in enumerate(pdf_links):
        #     print(f"[PDF #{idx+1}]: {link}")