from passlib.context import CryptContext
from starlette.concurrency import run_in_threadpool

class Crypto:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def encrypt(self, secret):
        return await run_in_threadpool(self.pwd_context.hash, secret)
    
    async def verify(self, secret, hash):
        return await run_in_threadpool(self.pwd_context.verify, secret, hash)
    