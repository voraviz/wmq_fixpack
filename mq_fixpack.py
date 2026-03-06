import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os


def process_apars_table(soup, div_id, output_file_name, metadata):
    """
    Locates an element by ID, finds the first 'bx--data-table' after it,
    extracts APARs matching a regex, and writes files with metadata headers.
    """
    # 1. Locate the anchor
    anchor = soup.find(id=div_id)
    if not anchor:
        print(f"Error: Element with id '{div_id}' not found.")
        return

    # 2. Find the first 'bx--data-table' following this anchor
    table = anchor.find_next('table', class_='bx--data-table')
    if not table:
        print(f"Error: No table found following ID '{div_id}'.")
        return

    csv_file = f"{output_file_name}.csv"
    md_file = f"{output_file_name}.md"
    
    # Regex for APAR: Starts with 2 letters followed by digits (e.g., DT12345, IT99999)
    apar_regex = re.compile(r'^[A-Z]{2}\d+')
    count = 1
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv, \
             open(md_file, 'w', encoding='utf-8') as f_md:
            
            writer = csv.writer(f_csv)
            writer.writerow(["APAR", "Is Security", "Is HIPER", "Description"])

            # --- Write Markdown Metadata Header ---
            f_md.write(f"# Fix List for {metadata['Fixpack']}\n\n")
            f_md.write(f"| Property | Details |\n")
            f_md.write(f"| :--- | :--- |\n")
            f_md.write(f"| **Release Type** | {metadata['Type']} |\n")
            f_md.write(f"| **Release Date** | {metadata['Date']} |\n")
            f_md.write(f"| **Total Fixes** | {metadata['Total']} |\n")
            f_md.write(f"| **Security Fixes** | {metadata['Security']} |\n")
            f_md.write(f"| **HIPER Fixes** | {metadata['Hiper']} |\n\n")
            
            f_md.write("## APAR Details\n\n")
            f_md.write("| APAR | Is Security | Is HIPER | Description |\n")
            f_md.write("| --- | --- | --- | --- |\n")

            # 3. Process Table Rows, Skip 1st row because it is header
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue

#                 # --- Field Extraction Logic ---
                
                # 1st Field: 3rd <td> (Check for <a> or raw text)
                # col3 = cols[2]
                apar = cols[2].find('a').text.strip() if cols[2].find('a') else cols[2].get_text(strip=True)

                # 2nd Field: 1st <td> (Is Security? Look for ✓)
                is_security = "Y" if "✓" in cols[0].get_text() else "N"

                # 3rd Field: 4th <td> (Is HIPER? Look for ✓)
                is_hiper = "Y" if "✓" in cols[1].get_text() else "N"

                # 4th Field: 2nd <td> (Description)
                description = cols[3].get_text(strip=True)

                row_data = [apar, is_security, is_hiper, description]
                print("["+str(count)+"/"+metadata["Total"]+"] "+apar+"\n")
                count += 1

                # Write data
                # 4. Write to files immediately
                writer.writerow(row_data)
                f_md.write(f"| {' | '.join(row_data)} |\n")

        print(f"Successfully generated: {csv_file} and {md_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
# def process_apars_table(soup, div_id, metadata, output_file_name):
#     """
#     Locates a div by ID, then finds the first table with class 'bx--data-table' 
#     following that div in the document structure.
#     """
#     # 1. Locate the anchor div/span
#     count = 1
#     anchor = soup.find(id=div_id)
#     if not anchor:
#         print(f"Error: Element with id '{div_id}' not found.")
#         return

#     # 2. Find the first 'bx--data-table' following this anchor
#     table = anchor.find_next('table', class_='bx--data-table')
#     if not table:
#         print(f"Error: No table found following ID '{div_id}'.")
#         return

#     csv_file = f"{output_file_name}.csv"
#     md_file = f"{output_file_name}.md"
#     headers = ["APAR", "Is Security", "Is HIPER", "Description"]

#     try:
#         # Open both files for line-by-line writing
#         with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv, \
#              open(md_file, 'w', encoding='utf-8') as f_md:
            
#             writer = csv.writer(f_csv)
#             writer.writerow(headers)

#             # Markdown Table Setup
#             f_md.write(f"| {' | '.join(headers)} |\n")
#             f_md.write(f"| {' | '.join(['---'] * len(headers))} |\n")

#             # 3. Process rows (skipping the header row if it contains <th>)
#             rows = table.find_all('tr')[1:]
#             for row in rows:
#                 cols = row.find_all('td')
                
#                 # Validation: Skip header rows or empty rows
#                 if len(cols) < 4:
#                     continue

#                 # --- Field Extraction Logic ---
                
#                 # 1st Field: 3rd <td> (Check for <a> or raw text)
#                 # col3 = cols[2]
#                 apar = cols[2].find('a').text.strip() if cols[2].find('a') else cols[2].get_text(strip=True)

#                 # 2nd Field: 1st <td> (Is Security? Look for ✓)
#                 is_security = "Y" if "✓" in cols[0].get_text() else "N"

#                 # 3rd Field: 4th <td> (Is HIPER? Look for ✓)
#                 is_hiper = "Y" if "✓" in cols[1].get_text() else "N"

#                 # 4th Field: 2nd <td> (Description)
#                 description = cols[3].get_text(strip=True)

#                 row_data = [apar, is_security, is_hiper, description]
#                 print("["+str(count)+"/"+metadata["Total"]+"] "+apar+"\n")
#                 count += 1
#                 # 4. Write to files immediately
#                 writer.writerow(row_data)
#                 f_md.write(f"| {' | '.join(row_data)} |\n")
#         print(f"Successfully generated: {csv_file} and {md_file}")

#     except Exception as e:
#         print(f"File writing failed: {e}")

def get_data(url, headers):
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            print("Complete retrieving data.")
            return BeautifulSoup(resp.content, 'html.parser')
        return None
    except Exception as e:
        # print("Error retrieving data. return code: "+resp.status_code)
        print(f"Error processing: {e}")
        return None

def format_date_for_file(date_str):
    """Converts '09 February 2026' to '20260209'."""
    try:
        match = re.search(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', date_str, re.I)
        if match:
            date_obj = datetime.strptime(match.group(), "%d %B %Y")
            return date_obj.strftime("%Y%m%d")
        return "UnknownDate"
    except Exception:
        return "UnknownDate"
def scrape_table_logic(soup, anchor_id, table_class=None, find_meta=False):
    """Extracts Fix Pack metadata and APARs from the table."""
    target = soup.find(id=anchor_id)
    if not target:
        return [], {}

    parent_table = target.find_next('table', class_=table_class) if table_class else target.find_next('table')
    if not parent_table:
        return [], {}

    meta = {"Release Date": "Unknown", "Last Modified": "Unknown", "Status": "Unknown"}
    
    # if find_meta:
    #     table_text = parent_table.get_text(" ", strip=True)
    #     rel_match = re.search(r'Fix release date:\s*(\d{1,2}\s+\w+\s+\d{4})', table_text, re.I)
    #     if rel_match: meta["Release Date"] = rel_match.group(1).strip()
            
    #     mod_match = re.search(r'Last modified:\s*(\d{1,2}\s+\w+\s+\d{4})', table_text, re.I)
    #     if mod_match: meta["Last Modified"] = mod_match.group(1).strip()
            
        # stat_match = re.search(r'Status:\s*(\w+)', table_text, re.I)
        # if stat_match: meta["Status"] = stat_match.group(1).strip()

    queue = []
    seen = set()
    rows = parent_table.find_all('tr')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 2: continue
        is_sec = "Y" if "✓" in tds[0].get_text() else "N"
        is_hiper = "Y" if "✓" in tds[1].get_text() else "N"
        apar_num, description = None, ""
        for i, td in enumerate(tds):
            text = td.get_text(strip=True)
            match = re.search(r'[A-Z]{2}\d{6}', text)
            if match:
                apar_num = match.group(0)
                if i + 1 < len(tds): description = tds[i+1].get_text(strip=True)
                print("APAR:"+apar_num+" Security:" +is_sec+" HIPER: "+is_hiper+" Description: "+description+"\n")
                break
        if apar_num and apar_num not in seen:
            seen.add(apar_num)
            queue.append({"num": apar_num, "isSecurity": is_sec, "table_desc": description})
            
    return queue, meta

def write_markdown_row(md_file, data, fields):
    row = "| " + " | ".join(str(data.get(f, "N/A")) for f in fields) + " |"
    md_file.write(row + "\n")

def scrape_metadata(soup,input_version):
    # vrmf_input = get_vrmf_input()
    # base_url = "https://www.ibm.com/support/pages/fix-list-ibm-mq-version-94-lts"
    
    # response = requests.get(base_url)
    # if response.status_code != 200:
    #     print("Failed to retrieve the page.")
    #     return

    # soup = BeautifulSoup(response.content, 'html.parser')
    main_table = soup.find('table', class_='bx--data-table')
    
    target_row = None
    rows = main_table.find_all('tr')[1:] # Skip header

    # Logic for 0.0 or exact match
    if input_version.endswith(".0.0"):
        target_row = rows[0] # Latest
    else:
        for row in rows:
            if input_version in row.get_text():
                target_row = row
                break

    if not target_row:
        print(f"Version {input_version} not found in the table.")
        return

    cols = target_row.find_all('td')
    link_tag = cols[0].find('a')
    version_clean = link_tag.text.strip().replace("IBM MQ ", "")
    metadata = {
        "Fixpack": version_clean,
        "Type": cols[1].text.strip(),
        "Date": cols[2].text.strip(),
        "Total": cols[3].text.strip(),
        "Security": cols[4].text.strip(),
        "Hiper": cols[5].text.strip()
    }
    # print(metadata["Fixpack"]+" Type: "+metadata["Type"]+" Date: "+metadata["Date"]+" Total: "+metadata["Total"]+" Security: "+metadata["Security"]+" HIPER: "+metadata["Hiper"]+"\n")
    return metadata

def main():
    print("--- IBM Consolidated APARs for WebSphere MQ 9.4 LTS and 9.3 LTS ---")
    user_version = input("Enter Fix Pack Version (e.g., 9.4.0.20 or 9.4.0.0/9.3.0.0 for latest): ").strip()
    headers = {"User-Agent": "Mozilla/5.0"}

    # Base URLs for version detection
    v94_base = "https://www.ibm.com/support/pages/fix-list-ibm-mq-version-94-lts"
    v93_base = "https://www.ibm.com/support/pages/fix-list-ibm-mq-version-93-lts"
    
    if user_version.startswith("9.3."):
        mq_base_url = v93_base
        # mq_url = f"{v93_base}#{version_anchor}"
    elif user_version.startswith("9.4."):
        mq_base_url = v94_base
        # mq_url = f"{v94_base}#{version_anchor}"
    else:
        print("Error: Major version must be 9.3 or 9.4")
        return
    
    print("MQ Base URL: "+mq_base_url+"\n")

    soup = get_data(mq_base_url, headers)
    metadata = scrape_metadata(soup,user_version)
    print(metadata["Fixpack"]+" Type: "+metadata["Type"]+" Date: "+metadata["Date"]+" Total: "+metadata["Total"]+" Security: "+metadata["Security"]+" HIPER: "+metadata["Hiper"]+"\n")
    user_version = metadata["Fixpack"]
    version_anchor = user_version.replace(".", "")
    print("User Version: "+user_version+"\n")
    print("Version Anchor: " + version_anchor + "\n")
    if user_version.startswith("9.3."):
        mq_url = f"{v93_base}#{version_anchor}"
    elif user_version.startswith("9.4."):
        mq_url = f"{v94_base}#{version_anchor}"

    print("MQ URL: "+mq_url+"\n")

    process_apars_table(soup,version_anchor,"test", metadata)
    # base_prefix = f"mq_fixpack_{version_anchor}"
    # fields = ["APAR Number", "isSecurity", "Title", "HIPER"]
    # # counts = {"MQ": 0, "HIPER": 0, "SECURITY": 0}
    # collected_meta = {}
    # sources = [
    #     {"name": "MQ", "url": mq_url, "class": "bx--data-table", "find_meta": True}
    # ]

    final_csv, final_md = None, None
    

    # for src in sources:
    #       print(f"\nProcessing {src['name']}...")
    #       try:
    #         resp = requests.get(src['url'], headers=headers, timeout=15)
    #         if resp.status_code == 200:
    #             soup = BeautifulSoup(resp.text, 'html.parser')
    #             queue, meta = scrape_table_logic(soup, version_anchor, table_class=src['class'], find_meta=src['find_meta'])
                
    #             if src['find_meta']:
    #                 collected_meta = meta
    #                 file_date = format_date_for_file(meta['Release Date'])
    #                 final_csv = f"{base_prefix}_{file_date}.csv"
    #                 final_md = f"{base_prefix}_{file_date}.md"
                
    #             if not final_csv:
    #                 final_csv = f"{base_prefix}_NoDate.csv"
    #                 final_md = f"{base_prefix}_NoDate.md"

    #             if not os.path.exists(final_csv):
    #                 with open(final_csv, mode='w', newline='', encoding='utf-8') as cf, \
    #                      open(final_md, mode='w', encoding='utf-8') as mf:
    #                     csv.DictWriter(cf, fieldnames=fields).writeheader()
    #                     mf.write(f"# IBM Support Fix List Report: {user_version}\n\n")
    #                     if collected_meta:
    #                         mf.write(f"**Release Date:** {collected_meta.get('Release Date')} | **Status:** {collected_meta.get('Status')}\n\n")
    #                     mf.write("| " + " | ".join(fields) + " |\n")
    #                     mf.write("| " + " | ".join(["---"] * len(fields)) + " |\n")

                # for i, item in enumerate(queue, 1):
                #     data = get_detailed_info(item['num'], headers, fields, item, src['name'])
                #     with open(final_csv, mode='a', newline='', encoding='utf-8') as cf:
                #         csv.DictWriter(cf, fieldnames=fields).writerow(data)
                #     with open(final_md, mode='a', encoding='utf-8') as mf:
                #         write_markdown_row(mf, data, fields)
                #     counts[src['name']] += 1
                #     print(f"   [{i}/{len(queue)}] {item['num']} ({src['name']})")
                    
        #   except Exception as e:
        #     print(f"Error processing {src['name']}: {e}")

    # print(f"\n" + "="*45 + f"\nFIX PACK DETAILS ({user_version})\n" + "="*45)
    # if collected_meta:
    #     # print(f"Fix Release Date: {collected_meta.get('Release Date')}\nLast Modified:    {collected_meta.get('Last Modified')}\nStatus:           {collected_meta.get('Status')}")
    #     print(f"Last Modified:    {collected_meta.get('Last Modified')}\n")
    # print("-"*45 + f"\nCSV Report: {final_csv}\nMD Report:  {final_md}\nTotals:     WAS ({counts['WAS']}), IHS ({counts['IHS']})\n" + "="*45)
if __name__ == "__main__":
    main()