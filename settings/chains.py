class Chain:
    def __init__(self, name: str, chain_id: int, rpc: str, native_token: str):
        self.name = name
        self.id = chain_id
        self.rpc = rpc
        self.native_token = native_token

    def set_rpc_url(self, url: str) -> bool:
        self.rpc = url
        return True


chains = {
    "ethereum": Chain(
        'ethereum',
        1,
        "https://eth.llamarpc.com",
        "ETH"),
    "bsc": Chain(
        'bsc',
        56,
        "https://binance.llamarpc.com",
        "BNB"),
    "arbitrum": Chain(
        'arbitrum',
        42161,
        "https://arbitrum.llamarpc.com",
        "ETH"),
    "base": Chain(
        'base',
        8453,
        "https://base.drpc.org",
        "ETH"),
    "avalance": Chain(
        'avalance',
        43114,
        "https://avalanche.drpc.org",
        "AVAX"),
    "polygon": Chain(
        'polygon',
        137,
        "https://polygon.llamarpc.com",
        "MATIC"),
    "linea": Chain(
        'linea',
        59114,
        "https://linea.decubate.com",
        "ETH"),
    "optimism": Chain(
        'optimism',
        10,
        "https://optimism.llamarpc.com",
        "ETH"),
    "gnosis": Chain(
        'gnosis',
        100,
        "https://gnosis.drpc.org",
        "XDAI")
}
