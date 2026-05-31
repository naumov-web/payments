import asyncio

from app.workers.subscription_billing_worker import SubscriptionBillingWorker

async def main():
    worker = SubscriptionBillingWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())