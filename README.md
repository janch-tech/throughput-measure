# throughput-measure
A tool for measuring throughput

# Usage

```bash
python3 main.py
```

# Modification

```python3

# Pass required params in main.py

if __name__ == '__main__':
    log("Starting")
    try:
        asyncio.run(runner(
            source_config=example_config_file,
            target_response_rate_in_sec=5
        ))
    except KeyboardInterrupt:
        log("Bye!!")
        sys.exit()


```
