# sanic-currency-converter
Web application to help convert currencies, based on Sanic

# Test
For test use postman
Example request args - localhost:8002/calc?out_currency=USDT&in_amount=2&in_currency=BTC
If you didn't pass signature in headers, responce will ne with nessesary signature, you can paste it

# Start local
pip3 install -r requirements.txt
python3 main.py