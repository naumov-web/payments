# Internal Wallet Service

## Overview

Internal Wallet Service is a wallet and subscription billing platform built using Domain-Driven Design (DDD), Clean Architecture, and the Transactional Outbox Pattern.

Key features:

- Actor management
- Wallet balances
- Money transfers
- Subscription management
- Automated recurring billing
- Retry logic for failed charges
- Kafka integration via Outbox Pattern
- Integration testing
- GitHub Actions CI

---

# Architecture

```text
app/
├── api/
├── application/
├── domain/
├── infrastructure/
├── workers/
└── config/
```

## Layers

### Domain

Contains:

- Aggregates
- Value Objects
- Domain Events
- Business Rules

### Application

Contains use cases such as:

- CreateSubscriptionUseCase
- ChargeSubscriptionUseCase
- CancelSubscriptionUseCase

### Infrastructure

Contains:

- PostgreSQL integration
- SQLAlchemy models
- Repositories
- Kafka integration
- Redis integration
- Unit of Work implementation

---

# Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| API | FastAPI |
| ORM | SQLAlchemy 2.0 Async |
| Database | PostgreSQL |
| Cache | Redis |
| Messaging | Kafka |
| Migrations | Alembic |
| Testing | Pytest |
| Containers | Docker Compose |
| CI | GitHub Actions |

---

# Running the Project

## Build

```bash
    make build
```

## Start

```bash
    make up
```

## Application:

```text
http://127.0.0.1:8000
```

## Documentation
```text
http://127.0.0.1:8000/docs
```

---

# Database

The project uses two databases.

## Main Database

```text
wallet_db
```

## Test Database

```text
wallet_test
```

---

# Migrations

Apply migrations:

```bash
alembic upgrade head
```

Rollback migrations:

```bash
alembic downgrade base
```

Create a migration:

```bash
alembic revision --autogenerate -m "description"
```

---

# Subscription Model

A subscription contains:

- subscriber_actor_id
- service_actor_id
- amount
- billing_period
- status
- next_billing_at
- retry_after

Statuses:

```text
ACTIVE
PAST_DUE
CANCELLED
```

---

# Billing Worker

Responsibilities:

1. Find subscriptions due for billing.
2. Execute ChargeSubscriptionUseCase.
3. Handle retries.
4. Move subscriptions to PAST_DUE when needed.

Flow:

```text
Worker
   |
   v
DueSubscriptionsRepository
   |
   v
ChargeSubscriptionUseCase
   |
   +--> SUCCESS
   |
   +--> INSUFFICIENT_FUNDS
            |
            v
         PAST_DUE
```

---

# Transactional Outbox Pattern

The service uses the Transactional Outbox Pattern to guarantee reliable event delivery.

Flow:

```text
Business Transaction
        |
        v
Outbox Message
        |
        v
Database Commit
        |
        v
Outbox Worker
        |
        v
Kafka
```

Benefits:

- Atomicity
- Reliability
- No lost messages
- Eventual consistency

---

# Testing

Run all tests:

```bash
python -m pytest -vv
```

Run a specific test file:

```bash
python -m pytest tests/integration/application/subscriptions/test_create_subscription.py -vv
```

Coverage includes:

- Use Cases
- Repositories
- Workers
- PostgreSQL integration

---

# CI

GitHub Actions automatically:

- Builds containers
- Starts infrastructure
- Runs migrations
- Executes integration tests

Triggered on:

- Push
- Pull Request

---

# Docker Compose Services

```text
app
postgres
postgres_test
redis
zookeeper
kafka
```

---

# Business Flows

## Create Subscription

```text
CreateSubscriptionUseCase
        |
        v
Validate Actors
        |
        v
Check Balance
        |
        v
Charge Wallet
        |
        v
Create Subscription
```

## Cancel Subscription

```text
CancelSubscriptionUseCase
        |
        v
Load Subscription
        |
        v
Set Status = CANCELLED
```

## Recurring Billing

```text
SubscriptionBillingWorker
        |
        v
ChargeSubscriptionUseCase
        |
        +--> Success
        |
        +--> Past Due
```

---

# Local Development

Start infrastructure:

```bash
    docker compose up -d postgres postgres_test redis zookeeper kafka
```

Run tests:

```bash
    docker compose run --rm app python -m pytest -vv
```

---

# License

Educational / Demonstration Project.
