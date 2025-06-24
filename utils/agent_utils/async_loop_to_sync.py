import asyncio
import traceback


def sync_generator_from_async(async_gen_func, *args, **kwargs):
    """
    Wrap an async generator function into a synchronous generator.

    :param async_gen_func: The async generator function to wrap.
    :param args: Positional arguments for the async generator function.
    :param kwargs: Keyword arguments for the async generator function.
    :return: A synchronous generator.
    """
    async_gen = async_gen_func(*args, **kwargs)

    async def _sync_wrapper():
        try:
            async for item in async_gen:
                yield item
        except Exception as e:
            exc = traceback.format_exc()
            print(f"!!!SMTH WRONG DURING ITERATION!!!:{exc}")
            yield f"ERR::{e}"
            raise e

        finally:
            await async_gen.aclose()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sync_gen = _sync_wrapper()

    while True:
        try:
            # Fetch the next item by running the event loop until the next item is available
            item = loop.run_until_complete(sync_gen.__anext__())

            yield item
        except StopAsyncIteration:
            # exc = traceback.format_exc()
            print(f"FINAL RESPONSE StopAsyncIteration")
            break
        except Exception:
            # exc = traceback.format_exc()
            print(f"FINAL RESPONSE StopAsyncIteration wit error")
            break

    loop.close()
