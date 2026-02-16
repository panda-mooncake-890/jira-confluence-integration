"""
GitHub Actions script to process Jira webhook data and update Confluence table
Triggered by repository_dispatch events from smee.io webhook relay
"""

import requests
from requests.auth import HTTPBasicAuth
import os
import json
from datetime import datetime
import sys

# Configuration from GitHub Secrets
ATLASSIAN_EMAIL = os.getenv('ATLASSIAN_EMAIL')
ATLASSIAN_API_TOKEN = os.getenv('ATLASSIAN_API_TOKEN')
JIRA_BASE_URL = 'https://panda-mooncake.atlassian.net'
CONFLUENCE_BASE_URL = 'https://panda-mooncake.atlassian.net/wiki'
CONFLUENCE_PAGE_ID = '163975'
EPIC_KEY = 'SCRUM-5'

# Authentication
auth = HTTPBasicAuth(ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN)

def get_epic_for_ticket(ticket_key):
    """Check if a ticket belongs to the SCRUM-5 epic"""
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_key}"
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        
        issue = response.json()
        fields = issue.get('fields', {})
        
        # Check for epic link (various possible field names)
        epic_link = (
            fields.get('parent', {}).get('key') or
            fields.get('customfield_10014') or
            fields.get('customfield_10008')
        )
        
        print(f"✓ Ticket {ticket_key} epic link: {epic_link}")
        return epic_link == EPIC_KEY
        
    except Exception as e:
        print(f"✗ Error checking epic for {ticket_key}: {str(e)}")
        return False

def get_confluence_page_content():
    """Fetch the current Confluence page content"""
    try:
        url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{CONFLUENCE_PAGE_ID}"
        params = {'expand': 'body.storage,version'}
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        print("✓ Successfully fetched Confluence page")
        return response.json()
    except Exception as e:
        print(f"✗ Error fetching Confluence page: {str(e)}")
        raise

def update_confluence_table(ticket_key, ticket_title, enablement_date):
    """Update the Confluence table with new ticket information"""
    try:
        # Get current page content
        page_data = get_confluence_page_content()
        current_content = page_data['body']['storage']['value']
        current_version = page_data['version']['number']
        
        # Check if ticket already exists in the table
        if ticket_key in current_content:
            print(f"⚠ Ticket {ticket_key} already exists in Confluence table. Skipping.")
            return True
        
        # Create new table row
        new_row = f"""<tr>
<td><p>{ticket_key}</p></td>
<td><p>{ticket_title}</p></td>
<td><p>{enablement_date}</p></td>
<td><p></p></td>
</tr>"""
        
        # Find the table and add the new row before </tbody>
        if '<tbody>' in current_content and '</tbody>' in current_content:
            updated_content = current_content.replace('</tbody>', f'{new_row}</tbody>', 1)
        else:
            print("✗ Could not find table structure in page")
            return False
        
        # Update the page
        url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{CONFLUENCE_PAGE_ID}"
        update_data = {
            'version': {'number': current_version + 1},
            'title': page_data['title'],
            'type': 'page',
            'body': {
                'storage': {
                    'value': updated_content,
                    'representation': 'storage'
                }
            }
        }
        
        response = requests.put(
            url,
            auth=auth,
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        print(f"✓ Successfully updated Confluence page with {ticket_key}")
        return True
        
    except Exception as e:
        print(f"✗ Error updating Confluence table: {str(e)}")
        return False

def main():
    """Main function to process the webhook event"""
    
    # Read the event payload from GitHub Actions context
    event_path = os.getenv('GITHUB_EVENT_PATH')
    
    if not event_path:
        print("✗ No event data found")
        sys.exit(1)
    
    try:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
        
        # Extract client_payload from repository_dispatch event
        payload = event_data.get('client_payload', {})
        
        print("=" * 60)
        print("PROCESSING JIRA WEBHOOK EVENT")
        print("=" * 60)
        
        # Check if this is a status change event
        webhook_event = payload.get('webhookEvent')
        if webhook_event != 'jira:issue_updated':
            print(f"⊘ Ignored: Not an issue update event (got: {webhook_event})")
            return
        
        # Check if status changed to DONE
        changelog = payload.get('changelog', {})
        items = changelog.get('items', [])
        
        status_changed_to_done = False
        for item in items:
            if item.get('field') == 'status' and item.get('toString', '').upper() == 'DONE':
                status_changed_to_done = True
                break
        
        if not status_changed_to_done:
            print("⊘ Ignored: Status not changed to DONE")
            return
        
        # Get ticket details
        issue = payload.get('issue', {})
        ticket_key = issue.get('key')
        ticket_title = issue.get('fields', {}).get('summary', '')
        transition_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"→ Ticket: {ticket_key}")
        print(f"→ Title: {ticket_title}")
        print(f"→ Date: {transition_date}")
        
        # Check if ticket belongs to SCRUM-5 epic
        if not get_epic_for_ticket(ticket_key):
            print(f"⊘ Ignored: Ticket not under epic {EPIC_KEY}")
            return
        
        print(f"✓ Ticket is under epic {EPIC_KEY}")
        
        # Update Confluence table
        print("\nUpdating Confluence table...")
        success = update_confluence_table(ticket_key, ticket_title, transition_date)
        
        if success:
            print("\n" + "=" * 60)
            print(f"SUCCESS: Updated Confluence with {ticket_key}")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("FAILED: Could not update Confluence table")
            print("=" * 60)
            sys.e
