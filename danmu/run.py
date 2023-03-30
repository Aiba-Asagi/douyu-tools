# 运行斗鱼弹幕姬
import asyncio
from loguru import logger
import danmuku

logger.remove(handler_id=None)
logger.add('out/log/loguru.log')

async def printer(q):
    # logger.info(locals())
    while True:
        logger.info(locals())
        m = await q.get()
        if m['msg_type'] == 'danmaku':
            print(f'{m["name"]}：{m["content"]}')
        if m['msg_type'] == 'enter':
            print(f'{m["name"]}：进入直播间')
            pass
        if m['msg_type'] == 'gift':
            print(f'{m["name"]}：送出礼物')
            pass


async def main(url):
    # logger.info(locals())
    q = asyncio.Queue()  # 消息队列
    dmc = danmuku.DanmukuClient(url, q)
    asyncio.create_task(printer(q))
    await dmc.start()
    pass


liveUrl = input('请输入直播间地址：\n')

asyncio.run(main(liveUrl))
