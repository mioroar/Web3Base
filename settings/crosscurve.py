import random

tokens = [
    {"chain": "Ethereum", "ticker": "USDC", "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
    {"chain": "Ethereum", "ticker": "USDT", "address": "0xdac17f958d2ee523a2206206994597c13d831ec7"},
    {"chain": "Arbitrum", "ticker": "USDC", "address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831"},
    {"chain": "Arbitrum", "ticker": "USDT", "address": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9"},
    {"chain": "Optimism", "ticker": "USDC", "address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85"},
    {"chain": "Optimism", "ticker": "USDT", "address": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"},
    # {"chain": "Avalanche", "ticker": "DAI.e", "address": "0xd586e7f844cea2f87f50152665bcbc2c279d8d70"},
    # {"chain": "Avalanche", "ticker": "USDC.e", "address": "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664"},
    # {"chain": "Avalanche", "ticker": "USDT.e", "address": "0xc7198437980c041c805a1edcba50c1ce5db95118"},
    # {"chain": "Avalanche", "ticker": "avDAI", "address": "0x47afa96cdc9fab46904a55a6ad4bf6660b53c38a"},
    # {"chain": "Avalanche", "ticker": "avUSDC", "address": "0x46a51127c3ce23fb7ab1de06226147f446e4a857"},
    # {"chain": "Avalanche", "ticker": "avUSDT", "address": "0x532e6537fea298397212f09a61e03311686f548e"},
    # {"chain": "Polygon", "ticker": "USDC", "address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"},
    # {"chain": "Polygon", "ticker": "DAI", "address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063"},
    # {"chain": "Polygon", "ticker": "USDC.e", "address": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"},
    # {"chain": "Polygon", "ticker": "USDT", "address": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"},
    # {"chain": "BSC", "ticker": "USDC", "address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"},
    # {"chain": "BSC", "ticker": "USDT", "address": "0x55d398326f99059fF775485246999027B3197955"},
]

SWAP_ONLY_IN_PLUS = False
SWAP_PLUS_SIZE = 0.01 # more than 0.01$

MAX_SWAP_LOSS = 0.1 # less than 0.1$

SWAP_PER_DAY = random.randint(5,10) # or swap_per_day= 10

SWAP_TIME_SLEEP = random.randint(60, 300) # in seconds
