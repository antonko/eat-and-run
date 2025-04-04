import gel
import asyncio

async def main():
    client = gel.create_async_client()
    result = await client.query_single("select 'Hello from Gel!';")
    print(result)

asyncio.run(main())