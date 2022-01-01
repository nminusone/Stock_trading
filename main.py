import requests
from twilio.rest import Client

# __________TWILLO INFO_____________________________
account_sid = "ACee43704de3eae4ddff7845c0424090c5"
auth_token = "de8bd6a2d17c89cf69f054b7aa64dbf5"
twi_num = "+16672260210"
# ____________STOCK to QUERY________________________
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
# ____________STOCK WEBSITE_________________________
ALPHA_API_KEY = "XYVUN8MEPIAIXMH5"
# ____________NEWS WEBSITE__________________________
NEWS_API_KEY = "ec3e8a1a1cd841ed9f46fb0a8ddd5dd6"
# ____________URL SHORTENER INFO____________________
BITLY_USER = "o_5cklabk4d6"
BITLY_PW = "Brutus@27"

auth_res = requests.post("https://api-ssl.bitly.com/oauth/access_token", auth=(BITLY_USER, BITLY_PW))
auth_res.raise_for_status()
access_token = auth_res.content.decode()
# print(access_token)
headers = {"Authorization": f"Bearer {access_token}"}
groups_res = requests.get("https://api-ssl.bitly.com/v4/groups", headers=headers)
groups_res.raise_for_status()
groups_data = groups_res.json()["groups"][0]
guid = groups_data["guid"]
# print(guid)
# _____________API PARAMS________________________________
PARAMS = {"function": "TIME_SERIES_DAILY",
          "symbol": STOCK,
          "apikey": ALPHA_API_KEY,
          }
NEWS_PARAMS = {"q": COMPANY_NAME,
               "apikey": NEWS_API_KEY,
               "excludeDomains": "blogspot.com,reuters.com"
               }

# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
response = requests.get(url="https://www.alphavantage.co/query", params=PARAMS)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]

day_0_data = list(data.items())[0]
day_0_close = float(day_0_data[1]["4. close"])
day_1_data = list(data.items())[1]
day_1_close = float(day_1_data[1]["4. close"])
percent_diff = round(((day_1_close - day_0_close) / day_0_close) * 100, 2)

if percent_diff > 5.00:
    print("Get News")
elif percent_diff < -5.00:
    print("Get News")

# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
news = requests.get(url="https://newsapi.org/v2/everything", params=NEWS_PARAMS)
news.raise_for_status()
news_data = news.json()


def shorten_url(item):
    bitly_link = requests.post("https://api-ssl.bitly.com/v4/shorten", json={"group_guid": guid, "long_url": item},
                               headers=headers)
    return bitly_link.json().get("link")


# for items in news_data["articles"][0:3]:
to_shorten = [shorten_url(items["url"]) for items in news_data["articles"][0:3]]
news_description = [items["description"] for items in news_data["articles"][0:3]]

print(to_shorten, news_description)


# for items in news_data["articles"][0:1]: to_shorten=items["url"] print(type(to_shorten)) shorten_res =
# requests.post("https://api-ssl.bitly.com/v4/shorten", json={"group_guid": guid, "long_url": to_shorten},
# headers=headers) print(shorten_res.json().get("link")) print(news_data["articles"])

# STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.
def send_sms(news_list, url_list):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"TSLA: 🔺️{percent_diff}%\n "
             f"Headline: {news_list[0]}\n"
             f"Link: {url_list[0]}",
        from_=twi_num,
        to="+18148269677"
    )


send_sms(news_description, to_shorten)
# Optional: Format the SMS message like this:
"""TSLA: 🔺2% Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. Brief: We at Insider Monkey have 
gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings 
show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash. 
or "TSLA: 🔻5% Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. Brief: We at Insider Monkey 
have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F 
filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus 
market crash. """
