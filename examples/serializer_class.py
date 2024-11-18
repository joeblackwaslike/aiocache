import asyncio
import zlib

from aiocache import Cache
from aiocache.serializers import BaseSerializer


class CompressionSerializer(BaseSerializer):

    # This is needed because zlib works with bytes.
    # this way the underlying backend knows how to
    # store/retrieve values
    DEFAULT_ENCODING = None

    def dumps(self, value):
        print(f"I've received:\n{value}")
        compressed = zlib.compress(value.encode())
        print(f"But I'm storing:\n{compressed}")
        return compressed

    def loads(self, value):
        print(f"I've retrieved:\n{value}")
        decompressed = zlib.decompress(value).decode()
        print(f"But I'm returning:\n{decompressed}")
        return decompressed


cache = Cache(Cache.REDIS, serializer=CompressionSerializer(), namespace="main")


async def serializer():
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt"
        "ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation"
        "ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in"
        "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur"
        "sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit"
        "anim id est laborum.")
    await cache.set("key", text)
    print("-----------------------------------")
    real_value = await cache.get("key")
    compressed_value = await cache.raw("get", "main:key")
    assert len(compressed_value) < len(real_value.encode())


def test_serializer():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serializer())
    loop.run_until_complete(cache.delete("key"))
    loop.run_until_complete(cache.close())


if __name__ == "__main__":
    test_serializer()
