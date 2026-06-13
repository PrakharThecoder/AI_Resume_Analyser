import time

class MetricsTracker:
    cache_hits: int = 0
    cache_misses: int = 0
    parsed_resumes_cache: dict[str, dict] = {}  # In-memory SHA-256 keyed cache
    
    total_inference_time_ms: float = 0.0
    inference_count: int = 0
    last_model_load_time_ms: float = 0.0

    @classmethod
    def increment_cache_hit(cls):
        cls.cache_hits += 1

    @classmethod
    def increment_cache_miss(cls):
        cls.cache_misses += 1

    @classmethod
    def add_inference_time(cls, duration_ms: float):
        cls.total_inference_time_ms += duration_ms
        cls.inference_count += 1

    @classmethod
    def get_average_inference_time(cls) -> float:
        if cls.inference_count == 0:
            return 0.0
        return cls.total_inference_time_ms / cls.inference_count

    @classmethod
    def set_model_load_time(cls, load_time_ms: float):
        cls.last_model_load_time_ms = load_time_ms

    @classmethod
    def get_cached_resumes_count(cls) -> int:
        return len(cls.parsed_resumes_cache)
        
    @classmethod
    def get_cache_keys(cls) -> list[str]:
        return list(cls.parsed_resumes_cache.keys())

metrics = MetricsTracker()
