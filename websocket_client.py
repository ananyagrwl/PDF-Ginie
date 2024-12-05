import asyncio
import websockets
import json

async def test_websocket():
    async with websockets.connect("ws://127.0.0.1:8000/ws/qa/") as websocket:
        
        pdf_id = "42b0edbf-e015-484d-a2aa-2d695c62d957"
        question = "What is the main topic of the file"
        
        # Send the JSON message to the WebSocket server
        await websocket.send(json.dumps({"pdf_id": pdf_id, "question": question}))

        # Wait for and print the response
        response = await websocket.recv()
        print("Response:", response)

asyncio.run(test_websocket())
