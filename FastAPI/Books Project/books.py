from fastapi import Body,FastAPI

app=FastAPI()

books = [
    {'title': "Title 1", 'author': "Author 1", 'year': 2020, 'category': "Science"},
    {'title': "Title 2", 'author': "Author 2", 'year': 2021, 'category': "Fiction"},
    {'title': "Title 3", 'author': "Author 3", 'year': 2019, 'category': "History"},
    {'title': "Title 4", 'author': "Author 4", 'year': 2022, 'category': "Science"},
    {'title': "Title 5", 'author': "Author 5", 'year': 2020, 'category': "Fiction"},
    {'title': "Title 6", 'author': "Author 6", 'year': 2018, 'category': "History"},
    {'title': "Title 7", 'author': "Author 2", 'year': 2021, 'category': "Science"},    
        ]

@app.get("/")
async def first_api():
    return {"This is Home Page"}

@app.get("/books")
async def read_all_books():
    return books

@app.get("/books/{book_title}") #dynamic param should always eb after static ones
def read_book_by_title(book_title: str):
    for book in books:
        if book['title'].casefold() == book_title.casefold():
            return book
    return {"message": "Book not found"}

@app.get("/books/")
def read_category_by_query(category: str):
    books_to_return = []
    for book in books:
        if book['category'].casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/byauthor/") #by query param
def read_author_by_query(author: str):
    books_to_return = []
    for book in books:
        if book['author'].casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/author/{author_name}/") #by dynamic param
def read_author_category_by_query(author_name: str, category: str):
    books_to_return = []
    for book in books:
        if book['author'].casefold() == author_name.casefold() and book['category'].casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


#post has a body where we can send data which can lager be used to create a new resource in the server
#get can not have any body and is used to read data from the server
@app.post("/books/create_book")
async def create_book(new_book=Body()): #body doesnt give any validation. Pydanatic will be used for validation later
    books.append(new_book)
    return {"message": "Book created successfully", "book": new_book}
@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(books)):
        if books[i]['title'].casefold() == updated_book['title'].casefold():
            books[i] = updated_book
            return {"message": "Book updated successfully", "book": updated_book}
        
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(books)):
        if books[i]['title'].casefold() == book_title.casefold():
            deleted_book = books.pop(i)
            return {"message": "Book deleted successfully", "book": deleted_book}
    return {"message": "Book not found"}