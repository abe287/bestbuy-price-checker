import requests
from bs4 import BeautifulSoup
import datetime as dt
import calendar, time
import argparse
from discord_webhook import DiscordWebhook, DiscordEmbed

#Return BeautifulSoup html from user link
def GetSoup(link):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    src = requests.get(link, headers = headers)
    soup = BeautifulSoup(src.content, 'lxml')

    return soup

#Gets the price, image, sku, title, and price of product
def GetProductDetails(soup):
    img_link = soup.find("img", attrs={"class":"primary-image"})['src']
    sku = soup.find("div", attrs={"class": "sku product-data"}).find('span', attrs={"class": "product-data-value body-copy"}).text.strip()
    title = soup.find("h1").text
    price = soup.find("div", attrs={"class":"priceView-hero-price priceView-customer-price"}).find("span").text

    product_details = {
        "img_link": img_link,
        "sku": sku,
        "title": title,
        "price": price
    }

    return product_details

#Checks if the current price is below the desired price
def IsDiscounted(product_details, desired_price):
    current_price = float(product_details['price'].replace("$",""))
    if current_price <= desired_price:
        return True
    else:
        return False

#Sends discord notification to user provided webhook url
def SendDiscordWebhook(product_details, discord_webhook, link):
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%Y-%m-%d %H:%M:%S')

    webhook = DiscordWebhook(url=discord_webhook)

    embed = DiscordEmbed(title=product_details['title'], url=link, color=65280)

    embed.set_thumbnail(url=product_details['img_link'])
    embed.set_footer(text="Bestbuy price checker | " + currentDT)

    embed.add_embed_field(name="Website", value='Bestbuy', inline=True)
    embed.add_embed_field(name="SKU", value=product_details['sku'], inline=True)
    embed.add_embed_field(name="Price", value=product_details['price'], inline=True)
    embed.add_embed_field(name="ATC Link", value="[ATC](https://api.bestbuy.com/click/blaze/"+ product_details['sku'] +"/cart)", inline=True)
    
    webhook.add_embed(embed)
    webhook.execute()

#Logs progress to terminal
def logger(is_discounted):
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%Y-%m-%d %H:%M:%S')
    
    if is_discounted == False:
        print(f"{currentDT} - price requirement not met")
    else:
        print(f"{currentDT} - price requirement met")
        print("Shutting Down")

#Main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--link", help = "Link to product", required = True)
    parser.add_argument("-d", "--delay", help = "Monitor delay in seconds", required = True)
    parser.add_argument("-p", "--price", help = "Desired Price", required = True)
    parser.add_argument("-w", "--webhook", help = "Discord webhook", required = True)

    args = parser.parse_args()
    link = args.link
    delay = int(args.delay)
    desired_price = float(args.price)
    discord_webhook = args.webhook

    while True:
        soup = GetSoup(link)
        product_details = GetProductDetails(soup)
        if IsDiscounted(product_details, desired_price) == True:
            SendDiscordWebhook(product_details, discord_webhook, link)
            logger(True)
            break
        
        logger(False)
        time.sleep(delay)

main()