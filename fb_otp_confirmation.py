import requests
import random
import string
import time


def generate_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Mobile Safari/537.36"
    ]
    return random.choice(user_agents)


def extract_tokens_from_page(response):
    # This function will extract necessary tokens from the HTML response
    # Assuming there's a JSON response with the required token
    # Modify the extraction logic based on actual page structure
    tokens = response.cookies.get_dict()
    return tokens


def get_confirmation_page(phone_number):
    url = "https://m.facebook.com/v2.9/otp/confirm"
    headers = {
        "User-Agent": generate_user_agent(),
    }
    payload = {
        "phone_number": phone_number,
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.ok:
        return response.text
    else:
        raise Exception(f"Error getting confirmation page: {response.status_code}")


def confirm_facebook_otp(phone_number, otp_code):
    url = "https://m.facebook.com/v2.9/otp/confirm"
    headers = {
        "User-Agent": generate_user_agent(),
    }
    payload = {
        "phone_number": phone_number,
        "otp_code": otp_code,
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.ok:
        print("OTP confirmed successfully!")
        return True
    else:
        print(f"Failed to confirm OTP: {response.status_code}")
        return False


def main():
    phone_number = input("Enter your phone number: ")
    # Obtain the confirmation page to start the process

    try:
        confirmation_page = get_confirmation_page(phone_number)
        print("Confirmation page fetched successfully.")

        otp_code = input("Enter the 5-digit OTP you received: ")

        while len(otp_code) != 5 or not otp_code.isdigit():
            print("Invalid OTP. Please enter a 5-digit OTP.")
            otp_code = input("Enter the 5-digit OTP you received: ")

        confirm_facebook_otp(phone_number, otp_code)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()