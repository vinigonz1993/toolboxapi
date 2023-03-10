import requests
import discord
from api.weather import WeatherApi
from api.exchange import Exchange
from api.quotes import Quotes
from api.octranspo import OCTranspo
from api.openai import OpenAI


def handle_response(message):
    message = message.lower()

    if message.startswith('!quote'):
        quotes = Quotes()
        return quotes.run()

    if message.startswith('!usd'):

        find_rate = message.split(' ')[1].upper()

        exchange = Exchange()
        request = exchange.run()

        try:
            response = f'''
                1 USD = {request["rates"][find_rate]} {find_rate.upper()}
            '''
        except:
            return 'Symbol not found'

        return response

    if message.startswith('!w'):
        try:
            params =  message.split(' ')

            location = params[1]
            country = params[2]
        except:
            return discord.Embed(
                title="Error",
                color=0xED4245,
                description='''Invalid location. Try something like:
                    ```!w ottawa ca```
                '''
            )
        try:
            request = WeatherApi().run(
                location, country
            )

            embed = discord.Embed(
                title=f"Weather in {request['name']}",
                color=0x109319,
            )

            def calculate_celcius(value):
                k = 273.15
                return f'{round(value - k, 2)} °C'

            embed.add_field(
                name=request['weather'][0]['main'],
                value=request['weather'][0]['description'],
                inline=False
            )
            embed.add_field(
                name='Temperature',
                value='',
                inline=False
            )
            embed.add_field(
                name='',
                value=f"Now {calculate_celcius(request['main']['temp'])}",
                inline=False
            )
            embed.add_field(
                name='',
                value=f"Max {calculate_celcius(request['main']['temp_max'])}",
                inline=False
            )
            embed.add_field(
                name='',
                value=f"Min {calculate_celcius(request['main']['temp_min'])}",
                inline=False
            )
            embed.add_field(
                name='',
                value=f"Feels like {calculate_celcius(request['main']['feels_like'])}",
                inline=False
            )
            return embed
        except:
            return "Sorry I couldn't find the location"

    if message.startswith('!bus'):
        try:
            list_string = message.split(' ')
            stopNo = list_string[1]
            oct = OCTranspo()
            request = oct.run(stopNo)

            embed = discord.Embed(
                title=request['GetRouteSummaryForStopResult']['StopDescription'],
                color=0x109319,
                description=f"Stop # {request['GetRouteSummaryForStopResult']['StopNo']}"
            )

            if len(list_string) == 3:
                routeNo = list_string[2]
                for route in request['GetRouteSummaryForStopResult']['Routes']['Route']:
                    if int(route['RouteNo']) == int(routeNo):
                        trips = route['Trips']
                        value=''
                        for trip in trips:
                            value += f"\n{trip['AdjustedScheduleTime']}min"
                        embed.add_field(
                            name=f"{route['RouteNo']} - {route['RouteHeading']}",
                            value=value,
                            inline=False
                        )
            else:
                for route in request['GetRouteSummaryForStopResult']['Routes']['Route']:
                    embed.add_field(
                        name=f"{route['RouteNo']} - {route['RouteHeading']}",
                        value='',
                        inline=False
                    )

            return embed
        except Exception as erro:
            print(erro)
            return discord.Embed(
                title="Error",
                color=0xED4245,
                description='''Sorry, the service unavailable right now, or the information is invalid'''
            )

    if message.startswith('!img'):
        if message.strip() == '!' or len(message.split(' ')) < 2:
            return 'Are you trying to ask something? Try again'
        message = message.replace('!img', '')
        request = OpenAI(message).run_image()
        return request

    if message.startswith('!'):
        if message.strip() == '!' or len(message.split(' ')) < 2:
            return 'Are you trying to ask something? Try again'
        request = OpenAI(message).run()
        return request
