Binance USDT-M Futures Trading Bot

A command-line interface (CLI) based trading bot for Binance USDT-M Futures that supports both basic and advanced order types. This bot includes structured logging, robust input validation, and secure environment configuration.

Project Structure

binance_trading_bot/
├── src/
│ ├── config.py
│ ├── logger_config.py
│ ├── validators.py
│ ├── binance_client.py
│ ├── market_orders.py
│ ├── limit_orders.py
│ ├── advanced/
│ │ ├── oco.py
│ │ ├── grid_orders.py
│ │ ├── stop_limit.py
│ │ ├── twap.py
│ └── init.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
