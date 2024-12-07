import asyncio
import websockets
import json

async def test_websocket():
    async with websockets.connect("ws://127.0.0.1:8000/ws/qa/") as websocket:
        
        pdf_id = "4b253083-8064-4830-aa4b-fd2f64b43f4c"
        question = "Tell me the topic of this file"
        
        # Send the JSON message to the WebSocket server
        await websocket.send(json.dumps({"pdf_id": pdf_id, "question": question}))

        response = await websocket.recv()
        print("Response:", response)

asyncio.run(test_websocket())
