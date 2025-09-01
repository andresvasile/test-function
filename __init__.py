import json
import logging
import azure.functions as func
from typing import Any, List, Optional
from datetime import datetime

# In-memory database for books
books_db = [
    {
        "id": 1,
        "title": "El Señor de los Anillos",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasía",
        "year": 1954,
        "pages": 1216,
        "rating": 4.8,
        "description": "Una épica historia de fantasía sobre la búsqueda para destruir un anillo poderoso.",
        "available": True,
        "added_date": "2024-01-15"
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "genre": "Distopía",
        "year": 1949,
        "pages": 328,
        "rating": 4.6,
        "description": "Una novela distópica sobre vigilancia gubernamental y control social.",
        "available": True,
        "added_date": "2024-01-20"
    },
    {
        "id": 3,
        "title": "Cien Años de Soledad",
        "author": "Gabriel García Márquez",
        "genre": "Realismo Mágico",
        "year": 1967,
        "pages": 417,
        "rating": 4.7,
        "description": "La historia de la familia Buendía a lo largo de siete generaciones.",
        "available": False,
        "added_date": "2024-01-10"
    },
    {
        "id": 4,
        "title": "Harry Potter y la Piedra Filosofal",
        "author": "J.K. Rowling",
        "genre": "Fantasía",
        "year": 1997,
        "pages": 309,
        "rating": 4.5,
        "description": "La primera aventura del joven mago Harry Potter.",
        "available": True,
        "added_date": "2024-01-25"
    },
    {
        "id": 5,
        "title": "Don Quijote de la Mancha",
        "author": "Miguel de Cervantes",
        "genre": "Novela",
        "year": 1605,
        "pages": 863,
        "rating": 4.4,
        "description": "Las aventuras del ingenioso hidalgo Don Quijote y su fiel escudero Sancho Panza.",
        "available": True,
        "added_date": "2024-01-05"
    }
]

# Counter for generating new IDs
next_id = len(books_db) + 1

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Books MCP Server HTTP trigger function processed a request.')

    try:
        # Get the method from query parameters or request body
        method = req.params.get('method')
        if not method:
            try:
                req_body = req.get_json()
                method = req_body.get('method') if req_body else None
            except ValueError:
                pass

        if not method:
            return func.HttpResponse(
                json.dumps({
                    "error": "Method parameter is required",
                    "available_methods": [
                        "list_books", "search_books", "get_book_details", 
                        "add_book", "borrow_book", "return_book", 
                        "rate_book", "get_library_stats"
                    ]
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Route to appropriate function
        if method == "list_books":
            return handle_list_books(req)
        elif method == "search_books":
            return handle_search_books(req)
        elif method == "get_book_details":
            return handle_get_book_details(req)
        elif method == "add_book":
            return handle_add_book(req)
        elif method == "borrow_book":
            return handle_borrow_book(req)
        elif method == "return_book":
            return handle_return_book(req)
        elif method == "rate_book":
            return handle_rate_book(req)
        elif method == "get_library_stats":
            return handle_get_library_stats(req)
        else:
            return func.HttpResponse(
                json.dumps({"error": f"Unknown method: {method}"}),
                status_code=400,
                mimetype="application/json"
            )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def handle_list_books(req: func.HttpRequest) -> func.HttpResponse:
    """List all books with optional filtering by genre and availability."""
    genre = req.params.get('genre')
    available_only = req.params.get('available_only', 'false').lower() == 'true'
    
    # Also check request body for parameters
    try:
        req_body = req.get_json()
        if req_body:
            genre = genre or req_body.get('genre')
            available_only = available_only or req_body.get('available_only', False)
    except ValueError:
        pass

    filtered_books = books_db
    
    if genre:
        filtered_books = [book for book in filtered_books if book["genre"].lower() == genre.lower()]
    
    if available_only:
        filtered_books = [book for book in filtered_books if book["available"]]
    
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": filtered_books,
            "count": len(filtered_books)
        }),
        status_code=200,
        mimetype="application/json"
    )

def handle_search_books(req: func.HttpRequest) -> func.HttpResponse:
    """Search books by title, author, or description."""
    query = req.params.get('query')
    
    # Also check request body
    try:
        req_body = req.get_json()
        if req_body:
            query = query or req_body.get('query')
    except ValueError:
        pass

    if not query:
        return func.HttpResponse(
            json.dumps({"error": "Query parameter is required"}),
            status_code=400,
            mimetype="application/json"
        )

    query_lower = query.lower()
    found_books = []
    
    for book in books_db:
        if (query_lower in book["title"].lower() or 
            query_lower in book["author"].lower() or 
            query_lower in book["description"].lower()):
            found_books.append(book)
    
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": found_books,
            "count": len(found_books),
            "query": query
        }),
        status_code=200,
        mimetype="application/json"
    )

def handle_get_book_details(req: func.HttpRequest) -> func.HttpResponse:
    """Get detailed information about a specific book."""
    book_id = req.params.get('book_id')
    
    # Also check request body
    try:
        req_body = req.get_json()
        if req_body:
            book_id = book_id or req_body.get('book_id')
    except ValueError:
        pass

    if not book_id:
        return func.HttpResponse(
            json.dumps({"error": "book_id parameter is required"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        book_id = int(book_id)
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "book_id must be a number"}),
            status_code=400,
            mimetype="application/json"
        )

    book = next((b for b in books_db if b["id"] == book_id), None)
    
    if not book:
        return func.HttpResponse(
            json.dumps({"error": f"Book with ID {book_id} not found"}),
            status_code=404,
            mimetype="application/json"
        )
    
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": book
        }),
        status_code=200,
        mimetype="application/json"
    )

def handle_add_book(req: func.HttpRequest) -> func.HttpResponse:
    """Add a new book to the library."""
    global next_id
    
    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )

        required_fields = ['title', 'author', 'genre', 'year', 'pages', 'description']
        for field in required_fields:
            if field not in req_body:
                return func.HttpResponse(
                    json.dumps({"error": f"Missing required field: {field}"}),
                    status_code=400,
                    mimetype="application/json"
                )

        new_book = {
            "id": next_id,
            "title": req_body['title'],
            "author": req_body['author'],
            "genre": req_body['genre'],
            "year": int(req_body['year']),
            "pages": int(req_body['pages']),
            "rating": 0.0,
            "description": req_body['description'],
            "available": True,
            "added_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        books_db.append(new_book)
        next_id += 1
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "data": new_book,
                "message": "Book added successfully"
            }),
            status_code=201,
            mimetype="application/json"
        )

    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": f"Invalid data format: {str(e)}"}),
            status_code=400,
            mimetype="application/json"
        )

def handle_borrow_book(req: func.HttpRequest) -> func.HttpResponse:
    """Borrow a book (mark as unavailable)."""
    book_id = req.params.get('book_id')
    
    # Also check request body
    try:
        req_body = req.get_json()
        if req_body:
            book_id = book_id or req_body.get('book_id')
    except ValueError:
        pass

    if not book_id:
        return func.HttpResponse(
            json.dumps({"error": "book_id parameter is required"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        book_id = int(book_id)
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "book_id must be a number"}),
            status_code=400,
            mimetype="application/json"
        )

    book = next((b for b in books_db if b["id"] == book_id), None)
    
    if not book:
        return func.HttpResponse(
            json.dumps({"error": f"Book with ID {book_id} not found"}),
            status_code=404,
            mimetype="application/json"
        )
    
    if not book["available"]:
        return func.HttpResponse(
            json.dumps({"error": f"Book '{book['title']}' is already borrowed"}),
            status_code=400,
            mimetype="application/json"
        )
    
    book["available"] = False
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": book,
            "message": f"Book '{book['title']}' borrowed successfully"
        }),
        status_code=200,
        mimetype="application/json"
    )

def handle_return_book(req: func.HttpRequest) -> func.HttpResponse:
    """Return a book (mark as available)."""
    book_id = req.params.get('book_id')
    
    # Also check request body
    try:
        req_body = req.get_json()
        if req_body:
            book_id = book_id or req_body.get('book_id')
    except ValueError:
        pass

    if not book_id:
        return func.HttpResponse(
            json.dumps({"error": "book_id parameter is required"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        book_id = int(book_id)
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "book_id must be a number"}),
            status_code=400,
            mimetype="application/json"
        )

    book = next((b for b in books_db if b["id"] == book_id), None)
    
    if not book:
        return func.HttpResponse(
            json.dumps({"error": f"Book with ID {book_id} not found"}),
            status_code=404,
            mimetype="application/json"
        )
    
    if book["available"]:
        return func.HttpResponse(
            json.dumps({"error": f"Book '{book['title']}' is already available"}),
            status_code=400,
            mimetype="application/json"
        )
    
    book["available"] = True
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": book,
            "message": f"Book '{book['title']}' returned successfully"
        }),
        status_code=200,
        mimetype="application/json"
    )

def handle_rate_book(req: func.HttpRequest) -> func.HttpResponse:
    """Rate a book (1.0 to 5.0)."""
    book_id = req.params.get('book_id')
    rating = req.params.get('rating')
    
    # Also check request body
    try:
        req_body = req.get_json()
        if req_body:
            book_id = book_id or req_body.get('book_id')
            rating = rating or req_body.get('rating')
    except ValueError:
        pass

    if not book_id or not rating:
        return func.HttpResponse(
            json.dumps({"error": "book_id and rating parameters are required"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        book_id = int(book_id)
        rating = float(rating)
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "book_id must be a number and rating must be a float"}),
            status_code=400,
            mimetype="application/json"
        )

    if not 1.0 <= rating <= 5.0:
        return func.HttpResponse(
            json.dumps({"error": "Rating must be between 1.0 and 5.0"}),
            status_code=400,
            mimetype="application/json"
        )
    
    book = next((b for b in books_db if b["id"] == book_id), None)
    
    if not book:
        return func.HttpResponse(
            json.dumps({"error": f"Book with ID {book_id} not found"}),
            status_code=404,
            mimetype="application/json"
        )
    
    book["rating"] = rating
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": book,
            "message": f"Rating updated for '{book['title']}': {rating}/5.0"
        }),
        status_code=200,
        mimetype="application/json"
    )

def handle_get_library_stats(req: func.HttpRequest) -> func.HttpResponse:
    """Get statistics about the library."""
    total_books = len(books_db)
    available_books = len([b for b in books_db if b["available"]])
    borrowed_books = total_books - available_books
    
    genres = {}
    for book in books_db:
        genre = book["genre"]
        genres[genre] = genres.get(genre, 0) + 1
    
    avg_rating = sum(b["rating"] for b in books_db) / total_books if total_books > 0 else 0
    
    stats = {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books,
        "average_rating": round(avg_rating, 1),
        "genres": genres
    }
    
    return func.HttpResponse(
        json.dumps({
            "success": True,
            "data": stats
        }),
        status_code=200,
        mimetype="application/json"
    )
