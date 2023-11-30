import telebot
import json
import requests

TOKEN = "Your token"
bot = telebot.TeleBot(TOKEN)

keys = {
    'рубль': 'RUB',
    'евро': 'EUR',
    'доллар': 'USD',
}

class ConvertionExeption(Exception):
    pass

class CryptoConverter:
    @staticmethod
    def convert(quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertionExeption(f'Невозможно произвести расчет одинаковой валюты {base}')

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConvertionExeption(f'Не удалось обработать валюту {quote}')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionExeption(f'Не удалось обработать валюту {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionExeption(f'Не удалось обработать количество {amount}')
        r = requests.get(
            f'https://api.apilayer.com/exchangerates_data/convert?to={base_ticker}&from{quote_ticker}&amount={amount}&apikey=GovpRKcwoNZciL8RKG8fsRq922pFvgWp')
        total_base = json.loads(r.content)[keys[base]]
        return total_base


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):
    text = "Чтобы начать работу введите команду в следующем формате: \n<имя валюты, цену которой хотите узнать>\
<имя валюты, в которой надо узнать цену первой валюты> \
<количество первой валюты>\nУвидеть список всех доступных валют: /values"
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'], )
def convert(message: telebot.types.Message):
    try:
        values = message.text.split(' ')
        if len(values) > 3:
            raise ConvertionExeption('Слишком много параметров')

        if len(values) != 3:
            raise ConvertionExeption('Слишком много параметров')

        quote, base, amount = values
        quote_ticker, base_ticker = keys[quote], keys[base]
        total_base = CryptoConverter.convert(quote, base, amount)
    except ConvertionExeption as e:
        bot.reply_to(message, f'Ошибка пользователя\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Цена {amount} {quote_ticker} в {base_ticker} - {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
