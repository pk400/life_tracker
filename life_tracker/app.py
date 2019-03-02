from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse
import uvicorn

app = Starlette()

@app.exception_handler(IOError)
async def on_ioerror(request, exc):
  return JSONResponse(exc)

@app.websocket_route('/ws')
class WS(WebSocketEndpoint):
  encoding = 'json'

  def __init__(self, scope):
    super().__init__(scope)
    self._clients = []
    self._sequence_id = 0

  async def on_connect(self, websocket):
    await websocket.accept()
    self._clients.append(websocket.client)
    print(websocket.client, 'connected!')

  async def on_receive(self, websocket, data):
    if 'jsonrpc' not in data or data['jsonrpc'] != '2.0':
      await self.send_jsonrpc(websocket, dict(data, error='Invalid JSON-RPC.'))
      return
    await websocket.send_json({
      'message': data
    })

  async def on_disconnect(self, websocket, close_code):
    print(websocket.client, 'disconnected!')

  def send_jsonrpc(self, websocket, data):
    rpc = dict(data, jsonrpc='2.0', id=self._sequence_id)
    self._sequence_id += 1
    return websocket.send_json(rpc)

if __name__ == '__main__':
  uvicorn.run(app)
