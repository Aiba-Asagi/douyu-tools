import re
from loguru import logger

import asyncio
import aiohttp

from .douyu import Douyu

__all__ = ['DanmukuClient']


class DanmukuClient:

    def __init__(self, url, q):
        # logger.info(locals())
        self.__url = ''
        self.__site = None
        self.__aioSession = None
        self.__ws = None
        self.__stop = False
        self.__dm_queue = q
        self.__link_status = True

        if 'http://' == url[:7] or 'https://' == url[:8]:
            self.__url = url
        else:
            self.__url = 'http://' + url

        for d, s in {'douyu.com': Douyu}.items():
            if re.match(r'^(?:http[s]?://)?.*?%s/(.+?)$' % d, url):
                self.__site = s
                self.__domain = d  # 主域名
                break
        if self.__site is None:
            print('Invalid link!')
            exit()

        self.__aioSession = aiohttp.ClientSession()

    async def init_ws(self):
        # logger.info(locals())
        ws_url, reg_datas = await self.__site.get_ws_info(self.__url)
        self.__ws = await self.__aioSession.ws_connect(ws_url)
        if reg_datas:
            for reg_data in reg_datas:
                await self.__ws.send_bytes(reg_data)

    async def heartbeats(self):
        # logger.info(locals())
        while not self.__stop and self.__site.heartbeat:
            await asyncio.sleep(self.__site.heartbeatInterval)
            try:
                await self.__ws.send_bytes(self.__site.heartbeat)
            except():
                print('错误')
                pass

    async def fetch_danmuku(self):
        logger.info(locals())
        while not self.__stop:
            async for msg in self.__ws:
                self.__link_status = True
                ms = self.__site.decode_msg(msg.data)
                for m in ms:
                    await self.__dm_queue.put(m)
            await asyncio.sleep(1)
            await self.init_ws()
            await asyncio.sleep(1)

    async def start(self):
        # logger.info(locals())

        await self.init_ws()

        await asyncio.gather(
            self.heartbeats(),
            self.fetch_danmuku(),
        )

    async def stop(self):
        logger.info(locals())
        self.__stop = True
        await self.__aioSession.close()
