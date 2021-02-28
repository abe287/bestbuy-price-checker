## Description
The bot will monitor the current price of an item. When the product's price falls below your desired price it will send you a notification via discord webhook.

## Usage
```
python app.py --link product_link --delay 300 --price 25 --webhook discord_webhook_url
```

## Options
```
-h, --help      Show this help message and exit
-l, --link      Link to product
-d, --delay     Monitor delay in seconds
-p, --price     Desired price
-w, --webhook   Discord webhook URL
```
