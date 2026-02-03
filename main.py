from fastapi import FastAPI

app = FastAPI(
    title="BookShelf App",
    description="A web application",
    version="1.0.0"
)


@app.get("/")
def read_root():
    return {"message": "Hello, Guys!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """
    Get an item by its ID.

    - item_id: The unique identifier for the item (path parameter)
    - q: Optional query string for filtering (query parameter)
    """
    return {"item_id": item_id, "query": q}

