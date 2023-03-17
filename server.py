from starlette.applications import Starlette
from starlette.websockets import WebSocketDisconnect
import json
import uvicorn
import random
import asyncio
import pyautogui

app = Starlette()
websockets = {}
user = None
TIME = 3
flag = 0


async def send_all(msg):
    for client in list(websockets.values()):
            try:
                await client.send_text(msg)
            except KeyError:
                pass

async def select_user():
    global user
    while(True):
        for i in range(TIME, -1, -1):
            await asyncio.sleep(1)
            print("sending time")
            await send_all(f'{{"event":"timer","value":"{i}"}}')
        user = random.choice(list(websockets.keys()))
        #print("sending user")
        await send_all(f'{{"event":"curr_user","value": "{user}"}}')
        #print(f'current user: {user}')
        #print("USINGNNG")
    

async def receive_json(websocket):
    message = await websocket.receive_text()
    return json.loads(message)

@app.websocket_route('/ws')
async def websocket_endpoint(websocket):
    global flag
    await websocket.accept()
    message = await receive_json(websocket)
    client_id = message['client_id']
    websockets[client_id] = websocket
    if flag == 0:
        task = asyncio.create_task(select_user())
        flag = 1

    
    while (True):
        try:
            message = await receive_json(websocket)
            print("message: ", json.dumps(message))
            if message['event'] == 'mouse':
                try:
                    pointer = message['pos'].split(',')
                    pyautogui.moveTo(int(pointer[0]), int(pointer[1]))
                    print('X : ', pointer[0])
                    print('Y : ', pointer[1])
                except:
                    pass
            elif message['event'] == 'keypress' :
                    try:
                        #('key pressed: ', message['key'])
                        pyautogui.keyDown(message['key'])
                        await asyncio.sleep(.1)
                        pyautogui.keyUp(message['key'])
                    except:
                        pass
                    print("\a")
            #print("websockets: ", websockets)
        except WebSocketDisconnect:
            break

    del websockets[client_id]
    await websocket.close()

if __name__ == '__main__':
    uvicorn.run(app, host='192.168.1.27', port=8021)