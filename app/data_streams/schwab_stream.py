import json
import asyncio
import websockets

from SchwabAPIClient import SchwabAPIClient


class SchwabStreamer:
    def __init__(self):
        self.client = SchwabAPIClient(
            credentials_file="credentials.json",
            grant_flow_type_filenames_file="grant_flow_type_filenames.json"
        )

        self.access_token = self.client.oauth_client.access_token

    async def connect(self):
        # Step 1: Get user preferences (REQUIRED for streaming endpoint + IDs)
        prefs = self.client.get_user_preferences()

        streamer_info = prefs["streamerInfo"][0]

        self.url = streamer_info["streamerSocketUrl"]
        self.customer_id = streamer_info["schwabClientCustomerId"]
        self.correl_id = streamer_info["schwabClientCorrelId"]
        self.channel = streamer_info["schwabClientChannel"]
        self.function_id = streamer_info["schwabClientFunctionId"]

        print("Connecting to:", self.url)

        async with websockets.connect(self.url) as ws:
            await self.login(ws)
            await self.subscribe(ws, "AAPL")

            await self.listen(ws)

    async def login(self, ws):
        login_payload = {
            "requests": [
                {
                    "service": "ADMIN",
                    "command": "LOGIN",
                    "requestid": "1",
                    "SchwabClientCustomerId": self.customer_id,
                    "SchwabClientCorrelId": self.correl_id,
                    "parameters": {
                        "Authorization": self.access_token,
                        "SchwabClientChannel": self.channel,
                        "SchwabClientFunctionId": self.function_id
                    }
                }
            ]
        }

        await ws.send(json.dumps(login_payload))
        print("Sent LOGIN")

    async def subscribe(self, ws, symbol):
        sub_payload = {
            "requests": [
                {
                    "service": "LEVELONE_EQUITIES",
                    "command": "SUBS",
                    "requestid": "2",
                    "SchwabClientCustomerId": self.customer_id,
                    "SchwabClientCorrelId": self.correl_id,
                    "parameters": {
                        "keys": symbol,
                        "fields": "1,2,3,4,5,8,9"
                    }
                }
            ]
        }

        await ws.send(json.dumps(sub_payload))
        print(f"Subscribed to {symbol}")

    async def listen(self, ws):
        while True:
            message = await ws.recv()
            data = json.loads(message)

            if "data" in data:
                for entry in data["data"]:
                    for item in entry["content"]:
                        parsed = self.parse_tick(item)
                        print(parsed)

    def parse_tick(self, item):
        return {
            "symbol": item.get("key"),
            "bid": item.get("1"),
            "ask": item.get("2"),
            "last": item.get("3"),
            "bid_size": item.get("4"),
            "ask_size": item.get("5"),
            "volume": item.get("8"),
            "last_size": item.get("9"),
        }


if __name__ == "__main__":
    streamer = SchwabStreamer()
    asyncio.run(streamer.connect())
