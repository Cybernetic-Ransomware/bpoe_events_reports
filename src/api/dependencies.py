import httpx
from fastapi import Request


#TODO remove AsyncConnector from state
def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client
