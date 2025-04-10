import requests
from datetime import datetime
import resend, schedule, time

resend.api_key = "RESEND_API_KEY"

# API endpoints to check
API_ENDPOINTS = {
    "EVM Blocks API": "https://api.evm.testnet.5ire.network/5ire/blocks?page=1",
    "EVM Transaction API": "https://api.evm.scan.5ire.network/5ire/transactions/hash/0x702fcd6a74e18c346f4f3ecb7bde46cc7c86d4d8c488fbc04df5e0fbf90b4d50",
    "Native Validators API": "https://api.native.testnet.5ire.network/5ire/validator",
}

EMAIL_RECIPIENT = ["piyush.choudhary@5ire.org", "hitesh@5ire.org"]

def build_consolidated_html_message(api_results: list) -> str:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Count active and down APIs
    active_count = sum(1 for _, is_active in api_results if is_active)
    down_count = len(api_results) - active_count
    
    # Determine overall status 
    overall_status = "All Active ✅" if down_count == 0 else f"{active_count} Active ✅, {down_count} Down ❌"
    header_bg_color = "#1b5e20" if down_count == 0 else "#f57c00" if active_count > 0 else "#b71c1c"
    
    message = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: {header_bg_color}; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
            .content {{ background-color: white; padding: 20px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .api-item {{ padding: 15px; margin-bottom: 15px; border-radius: 5px; border-left: 5px solid; }}
            .api-active {{ background-color: #e8f5e9; border-left-color: #4caf50; }}
            .api-down {{ background-color: #ffebee; border-left-color: #f44336; }}
            .status-label {{ display: inline-block; padding: 5px 10px; border-radius: 15px; font-weight: bold; font-size: 14px; }}
            .status-active {{ background-color: #4caf50; color: white; }}
            .status-down {{ background-color: #f44336; color: white; }}
            .footer {{ margin-top: 20px; text-align: center; color: #757575; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>5ire Testnet API Status Report</h1>
                <p>Status: {overall_status}</p>
            </div>
            <div class="content">
                <h2>API Status Details</h2>
    """
    
    # each API status
    for api_name, is_active in api_results:
        status_class = "api-active" if is_active else "api-down"
        status_label_class = "status-active" if is_active else "status-down"
        status_text = "Active" if is_active else "Down"
        
        message += f"""
                <div class="api-item {status_class}">
                    <h3>{api_name}</h3>
                    <p>Status: <span class="status-label {status_label_class}">{status_text}</span></p>
                </div>
        """
    
    # footer
    message += f"""
                <div class="footer">
                    <p>Report generated at: {now}</p>
                    <p>5ire Testnet Monitoring System</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return message

def check_api_status():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== Checking APIs at {current_time} ===")
    
    api_results = []
    
    for api_name, url in API_ENDPOINTS.items():
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                status = f"Active ({response.status_code})"
                api_results.append((api_name, True))
            else:
                status = f"DOWN ({response.status_code})"
                api_results.append((api_name, False))
        except requests.exceptions.RequestException as e:
            status = f"Down (Error: {str(e)})"
            api_results.append((api_name, False))
            
        print(f"{api_name}: {status}")
    
    # Send email only if any API is down
    down_apis = [(name, status) for name, status in api_results if not status]
    if down_apis:
        send_consolidated_email(api_results)
    else:
        print("All APIs are active. No email notification sent.")

def send_consolidated_email(api_results: list):
    try:
        # Count active and down APIs
        active_count = sum(1 for _, is_active in api_results if is_active)
        down_count = len(api_results) - active_count
        
        # subject based on overall status
        if down_count == 0:
            subject = "✅ All 5ire Testnet APIs are Active"
        elif active_count == 0:
            subject = "❌ All 5ire Testnet APIs are Down"
        else:
            subject = f"⚠️ 5ire Testnet API Status: {active_count} Active, {down_count} Down"
        
        html_message = build_consolidated_html_message(api_results)

        email_params: resend.Emails.SendParams = {
            "from": "5ire Testnet API Monitor <no-reply@thedevpiyush.com>",
            "to": EMAIL_RECIPIENT,
            "subject": subject,
            "html": html_message,
        }

        resend.Emails.send(email_params)
        print(f"Consolidated email sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"Failed to send consolidated email: {e}")

def send_daily_reminder():
    try:
        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"🔔 5ire API Monitoring System - Daily Check-in ({current_date})"
        
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3f51b5; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background-color: white; padding: 20px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .footer {{ margin-top: 20px; text-align: center; color: #757575; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>5ire API Monitoring System</h1>
                    <p>Daily Status Report</p>
                </div>
                <div class="content">
                    <h2>Monitoring System Active</h2>
                    <p>This is an automated message to confirm that the 5ire API monitoring system is active and running.</p>
                    <p>The system is checking all API endpoints every 15 minutes and will send alerts if any issues are detected.</p>
                    <p>Current monitoring targets:</p>
                    <ul>
                        {chr(10).join([f'<li><strong>{api_name}</strong>: {url}</li>' for api_name, url in API_ENDPOINTS.items()])}
                    </ul>
                </div>
                <div class="footer">
                    <p>Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>5ire Testnet Monitoring System</p>
                </div>
            </div>
        </body>
        </html>
        """

        email_params: resend.Emails.SendParams = {
            "from": "5ire Testnet API Monitor <no-reply@thedevpiyush.com>",
            "to": EMAIL_RECIPIENT,
            "subject": subject,
            "html": html_message,
        }

        resend.Emails.send(email_params)
        print(f"Daily reminder email sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"Failed to send daily reminder email: {e}")

def schedule_checks():
    schedule.every(15).minutes.do(check_api_status)
    
    # Send daily reminder only 1 time.
    schedule.every().day.at("00:00").do(send_daily_reminder)

    print("5ire Testnet Monitor started. Checking every 15 minutes with daily status report at midnight...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    check_api_status()
    schedule_checks()  
