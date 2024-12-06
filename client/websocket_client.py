import asyncio
import websockets
import json

async def test_websocket():
    async with websockets.connect("ws://127.0.0.1:8000/ws/qa/") as websocket:
        
        pdf_id = "3d53989f-3e95-4594-83e0-c0892950bd69"
        question = "Tell me why should ananya work as a Python Developer"
        
        # Send the JSON message to the WebSocket server
        await websocket.send(json.dumps({"pdf_id": pdf_id, "question": question}))

        response = await websocket.recv()
        print("Response:", response)

asyncio.run(test_websocket())
