import tkinter
import tkinter.ttk
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import time


class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    year_of_publishing: Mapped[int] = mapped_column()

    def __str__(self):
        print(f"Id: {self.id}\nАвтор: {self.author}\nНазвание: {self.title}\nГод издания: {self.year_of_publishing}\n")


class BooksFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.Session = Session
        self.__labels = []

        self.__label: tkinter.ttk.Label

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        with self.Session() as session:
            stmt = select(Book)
            books = session.scalars(stmt).all()
            for book in books:
                self.__label = tkinter.ttk.Label(self, text=f"\nId: {book.id}\nАвтор: {book.author}\nНазвание: {book.title}\nГод издания: {book.year_of_publishing}")
                self.__labels.append(self.__label)

    def __pack_widgets(self):
        for l in self.__labels:
            l.pack(pady=5)
        
    def show(self):
        self.pack()


class Show(tkinter.Toplevel):
    def __init__(self, parent, Session):
        super().__init__(parent)
        self.Session = Session

        self.canvas: tkinter.Canvas
        self.scrollbar: tkinter.Scrollbar 
        self.books_frame: BooksFrame

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()


    def __configure_window(self):
        self.title("Все книги")
        self.geometry("400x400")


    def __configure_widgets(self):
        self.canvas = tkinter.Canvas(self) 
        self.scrollbar = tkinter.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set) 
        self.books_frame = BooksFrame(self, self.Session)

        self.bind_all("<MouseWheel>", self._on_mousewheel)


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


    def __pack_widgets(self):
        self.scrollbar.pack(side="right", fill="y")  
        self.canvas.pack(fill="both", expand=True) 
        self.canvas.create_window((0, 0), window=self.books_frame, anchor="nw")
        self.books_frame.update_idletasks()  
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class Add(tkinter.Toplevel):
    def __init__(self, parent, Session):
        super().__init__(parent)
        
        # self.parent = parent

        self.Session = Session

        self.__main_label: tkinter.ttk.Label
        self.__author_label: tkinter.ttk.Label
        self.__author_entry: tkinter.ttk.Entry
        self.__title_label: tkinter.ttk.Label
        self.__title_entry: tkinter.ttk.Entry
        self.__year_of_publishing_label: tkinter.ttk.Label
        self.__year_of_publishing_entry: tkinter.ttk.Entry
        self.__save_button: tkinter.ttk.Button

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()


    def __configure_window(self):
        self.title("Добавить книгу")
        self.geometry("400x260")

    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Добавление новой книги")
        self.__author_label = tkinter.ttk.Label(self, text="Введите автора книги: ")
        self.__author_entry = tkinter.ttk.Entry(self)
        self.__title_label = tkinter.ttk.Label(self, text="Введите название книги: ")
        self.__title_entry = tkinter.ttk.Entry(self)
        self.__year_of_publishing_label = tkinter.ttk.Label(self, text="Введите год издания книги: ")
        self.__year_of_publishing_entry = tkinter.ttk.Entry(self)
        self.__save_button = tkinter.ttk.Button(self, text="Сохранить", command=self.__save)

    def __pack_widgets(self):
        self.__main_label.pack(pady=10)
        self.__author_label.pack()
        self.__author_entry.pack(pady=3)
        self.__title_label.pack()
        self.__title_entry.pack(pady=3)
        self.__year_of_publishing_label.pack()
        self.__year_of_publishing_entry.pack(pady=3)
        self.__save_button.pack(pady=2)

    def __save(self):
        with self.Session() as session:
            author = self.__author_entry.get()
            title = self.__title_entry.get()
            year_of_publishing = self.__year_of_publishing_entry.get()
            book = Book(author=author, title=title, year_of_publishing=year_of_publishing)
            session.add(book)
            session.commit()
            stmt = select(Book).where(Book.title == title).where(Book.author == author).where(Book.year_of_publishing == year_of_publishing)
            book: Book | None= session.scalars(stmt).first()
            self.destroy()


class FoundBooksFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session, author_name):
        super().__init__(container)
        self.container = container
        self.Session = Session
        self.__labels = []
        self.author_name = author_name
        

        self.__label: tkinter.ttk.Label

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):
        
        with self.Session() as session:
            stmt = select(Book).where(Book.author==self.author_name)
            books = session.scalars(stmt).all()
            for book in books:
                self.__label = tkinter.ttk.Label(self, text=f"\nId: {book.id}\nАвтор: {book.author}\nНазвание: {book.title}\nГод издания: {book.year_of_publishing}")
                self.__labels.append(self.__label)

    def __pack_widgets(self):
        for l in self.__labels:
            l.pack(pady=5)
        
    def show(self):
        self.pack()


class Find(tkinter.Toplevel):
    def __init__(self, parent, Session):
        super().__init__(parent)
        self.Session = Session

        self.__main_label: tkinter.ttk.Label
        self.__author_label: tkinter.ttk.Label
        self.__author_entry: tkinter.ttk.Entry
        
        self.__find_button: tkinter.ttk.Button
        self.__found_label: tkinter.ttk.Label

        self.canvas: tkinter.Canvas
        self.scrollbar: tkinter.Scrollbar 
        self.found_books_frame: FoundBooksFrame


        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()


    def __configure_window(self):
        self.title("Найти книгу")
        self.geometry("400x320")

    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Поиск новой книги")
        self.__author_label = tkinter.ttk.Label(self, text="Введите автора книги: ")
        self.__author_entry = tkinter.ttk.Entry(self)
        
        self.__find_button = tkinter.ttk.Button(self, text="Найти", command=self.__find)
        self.__found_label = tkinter.ttk.Label(self, text="Найденные книги: ")

        self.canvas = tkinter.Canvas(self) 
        self.scrollbar = tkinter.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set) 

        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def __find(self):
        author_name = self.__author_entry.get()
        self.found_books_frame = FoundBooksFrame(self, self.Session, author_name)
        self.canvas.create_window((0, 0), window=self.found_books_frame, anchor="nw")
        self.found_books_frame.update_idletasks()  
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __pack_widgets(self):
        self.__main_label.pack(pady=10)
        self.__author_label.pack()
        self.__author_entry.pack(pady=3)
        
        self.__find_button.pack(pady=2)
        self.__found_label.pack()

        self.scrollbar.pack(side="right", fill="y")  
        self.canvas.pack(fill="both", expand=True) 
        

    

class FoundToUpdate(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.Session = Session
        self.book: Book

        self.__main_label: tkinter.ttk.Label
        self.__author_label: tkinter.ttk.Label
        self.__author_entry: tkinter.ttk.Entry
        self.__title_label: tkinter.ttk.Label
        self.__title_entry: tkinter.ttk.Entry
        self.__year_of_publishing_label: tkinter.ttk.Label
        self.__year_of_publishing_entry: tkinter.ttk.Entry
        self.__find_button: tkinter.ttk.Button
        self.__book_label: tkinter.ttk.Label
        self.__confirm_label: tkinter.ttk.Label
        self.__confirm_button: tkinter.ttk.Button

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):

        self.__main_label = tkinter.ttk.Label(self, text="Изменение данных о книге")
        self.__author_label = tkinter.ttk.Label(self, text="Введите автора книги: ")
        self.__author_entry = tkinter.ttk.Entry(self)
        self.__title_label = tkinter.ttk.Label(self, text="Введите название книги: ")
        self.__title_entry = tkinter.ttk.Entry(self)
        self.__year_of_publishing_label = tkinter.ttk.Label(self, text="Введите год издания книги: ")
        self.__year_of_publishing_entry = tkinter.ttk.Entry(self)
        self.__find_button = tkinter.ttk.Button(self, text="Найти книгу", command=self.__find)

        self.__confirm_label = tkinter.ttk.Label(self, text="Подтвердите, что найдена верная книга\n В ином случае заново введите данные")
        self.__book_label = tkinter.ttk.Label(self, text=f"\nId: \nАвтор: \nНазвание: \nГод издания: ")
        self.__confirm_button = tkinter.ttk.Button(self, text="Подтвердить", command=self.__confirm)
        

    def __pack_widgets(self):
        self.__main_label.pack(pady=10)
        self.__author_label.pack()
        self.__author_entry.pack(pady=3)
        self.__title_label.pack()
        self.__title_entry.pack(pady=3)
        self.__year_of_publishing_label.pack()
        self.__year_of_publishing_entry.pack(pady=3)
        self.__find_button.pack(pady=3)
        self.__confirm_label.pack(pady=2)
        self.__book_label.pack()
        self.__confirm_button.pack(pady=3)

    def __find(self):
        with self.Session() as session:
            author = self.__author_entry.get()
            title = self.__title_entry.get()
            year_of_publishing = self.__year_of_publishing_entry.get()

            stmt = select(Book).where(Book.title == title).where(Book.author == author).where(Book.year_of_publishing == year_of_publishing)
            self.book: Book | None= session.scalars(stmt).first()
            self.__book_label["text"] = f"\nId: {self.book.id}\nАвтор: {self.book.author}\nНазвание: {self.book.title}\nГод издания: {self.book.year_of_publishing}"
            
    def __confirm(self):
        self.pack_forget()
        self.container.update_frame.show(self.Session, self.book)
        
    def show(self):
        self.pack()



class UpdateFrame(tkinter.ttk.Frame):
    def __init__(self, container, Session):
        super().__init__(container)
        self.container = container
        self.Session = Session
        self.book: Book

        self.__main_label: tkinter.ttk.Label
        self.__author_label: tkinter.ttk.Label
        self.__author_entry: tkinter.ttk.Entry
        self.__title_label: tkinter.ttk.Label
        self.__title_entry: tkinter.ttk.Entry
        self.__year_of_publishing_label: tkinter.ttk.Label
        self.__year_of_publishing_entry: tkinter.ttk.Entry
        self.__save_button: tkinter.ttk.Button

        self.__configure_widgets()
        self.__pack_widgets()

    def __configure_widgets(self):

        self.__main_label = tkinter.ttk.Label(self, text="Изменение данных о книге")
        self.__author_label = tkinter.ttk.Label(self, text="Введите нового автора книги: ")
        self.__author_entry = tkinter.ttk.Entry(self)
        self.__title_label = tkinter.ttk.Label(self, text="Введите новое название книги: ")
        self.__title_entry = tkinter.ttk.Entry(self)
        self.__year_of_publishing_label = tkinter.ttk.Label(self, text="Введите новый год издания книги: ")
        self.__year_of_publishing_entry = tkinter.ttk.Entry(self)
        self.__save_button = tkinter.ttk.Button(self, text="Сохранить", command=self.__update)

    def __pack_widgets(self):
        self.__main_label.pack(pady=10)
        self.__author_label.pack()
        self.__author_entry.pack(pady=3)
        self.__title_label.pack()
        self.__title_entry.pack(pady=3)
        self.__year_of_publishing_label.pack()
        self.__year_of_publishing_entry.pack(pady=3)
        self.__save_button.pack()
        

    def __update(self):
        with self.Session() as session:

            stmt = select(Book).where(Book.title == self.book.title)
            books: Book | None = session.scalars(stmt).all()
            for book in books:
                if book.author == self.book.author and book.year_of_publishing == self.book.year_of_publishing:
                    author = self.__author_entry.get()
                    title = self.__title_entry.get()
                    year_of_publishing = self.__year_of_publishing_entry.get()
                    book.author = author
                    book.title = title
                    book.year_of_publishing = year_of_publishing
                    session.commit()

                    stmt = select(Book).where(Book.title == self.book.title)
                    book = session.scalars(stmt).all()
                    self.pack_forget()
                    self.container.destroy()

                    
            
    
        
    def show(self, Session, book):
        self.Session = Session
        self.book = book
        print("got_bbok")
        self.pack()



class Update(tkinter.Toplevel):
    def __init__(self, parent, Session):
        super().__init__(parent)

        self.Session = Session

        self.found_to_update: FoundToUpdate
        self.update_frame: UpdateFrame

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()


    def __configure_window(self):
        self.title("Обновить книгу")
        self.geometry("400x500")


    def __configure_widgets(self):
        self.found_to_update = FoundToUpdate(self, self.Session)
        self.update_frame = UpdateFrame(self, self.Session)

    def __pack_widgets(self):
        self.found_to_update.show()



class Delete(tkinter.Toplevel):
    def __init__(self, parent, Session):
        super().__init__(parent)

        self.Session = Session

        self.__main_label: tkinter.ttk.Label
        self.__author_label: tkinter.ttk.Label
        self.__author_entry: tkinter.ttk.Entry
        self.__title_label: tkinter.ttk.Label
        self.__title_entry: tkinter.ttk.Entry
        self.__year_of_publishing_label: tkinter.ttk.Label
        self.__year_of_publishing_entry: tkinter.ttk.Entry
        self.__find_button: tkinter.ttk.Button
        self.__book_label: tkinter.ttk.Label
        self.__confirm_label: tkinter.ttk.Label
        self.__confirm_button: tkinter.ttk.Button

        

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()


    def __configure_window(self):
        self.title("Удалить")
        self.geometry("445x500")


    def __configure_widgets(self):
        self.__main_label = tkinter.ttk.Label(self, text="Изменение данных о книге")
        self.__author_label = tkinter.ttk.Label(self, text="Введите автора книги: ")
        self.__author_entry = tkinter.ttk.Entry(self)
        self.__title_label = tkinter.ttk.Label(self, text="Введите название книги: ")
        self.__title_entry = tkinter.ttk.Entry(self)
        self.__year_of_publishing_label = tkinter.ttk.Label(self, text="Введите год издания книги: ")
        self.__year_of_publishing_entry = tkinter.ttk.Entry(self)
        self.__find_button = tkinter.ttk.Button(self, text="Найти книгу", command=self.__find)

        self.__confirm_label = tkinter.ttk.Label(self, text='Нажимая кнопку "Удалить", вы подтверждаете,\n что найдена верная книга для удаления\n В ином случае заново введите данные')
        self.__book_label = tkinter.ttk.Label(self, text=f"\nId: \nАвтор: \nНазвание: \nГод издания: ")
        self.__confirm_button = tkinter.ttk.Button(self, text="Удалить", command=self.__confirm)
        

    def __pack_widgets(self):
        self.__main_label.pack(pady=10)
        self.__author_label.pack()
        self.__author_entry.pack(pady=3)
        self.__title_label.pack()
        self.__title_entry.pack(pady=3)
        self.__year_of_publishing_label.pack()
        self.__year_of_publishing_entry.pack(pady=3)
        self.__find_button.pack()
        self.__confirm_label.pack(pady=2)
        self.__book_label.pack()
        self.__confirm_button.pack(pady=2)

    def __find(self):
        with self.Session() as session:
            author = self.__author_entry.get()
            title = self.__title_entry.get()
            year_of_publishing = self.__year_of_publishing_entry.get()

            stmt = select(Book).where(Book.title == title).where(Book.author == author).where(Book.year_of_publishing == year_of_publishing)
            self.book: Book | None= session.scalars(stmt).first()
            self.__book_label["text"] = f"\nId: {self.book.id}\nАвтор: {self.book.author}\nНазвание: {self.book.title}\nГод издания: {self.book.year_of_publishing}"
            
    def __confirm(self):
        with self.Session() as session:
            session.delete(self.book)
            session.commit()
            self.destroy()


class App(tkinter.Tk):
    def __init__(self, Session):
        super().__init__()
        self.__child_windows = []
        self.Session = Session

        self.style: tkinter.ttk.Style


        self.__title_label: tkinter.ttk.Label
        self.__desc_label: tkinter.ttk.Label

        self.__show_label: tkinter.ttk.Label
        self.__show_button: tkinter.ttk.Button

        self.__add_label: tkinter.ttk.Label
        self.__add_button: tkinter.ttk.Button

        self.__find_label: tkinter.ttk.Label
        self.__find_button: tkinter.ttk.Button

        self.__update_label: tkinter.ttk.Label
        self.__update_button: tkinter.ttk.Button

        self.__delete_label: tkinter.ttk.Label
        self.__delete_button: tkinter.ttk.Button

        self.__configure_window()
        self.__configure_widgets()
        self.__pack_widgets()



    def __configure_window(self):
        self.title("Библиотека")
        self.geometry("650x420")


    def __configure_widgets(self):

        self.style = tkinter.ttk.Style()
        self.style.configure(
            "Main.TLabel", 
            font=("Arial", 20)
        )
        self.style.configure(
            "TLabel", 
            font=("Arial", 15),
        )
        self.style.configure(
            "TButton", 
            font="Arial"
        )



        self.__title_label = tkinter.ttk.Label(self, text="Библиотека", style="Main.TLabel")
        self.__desc_label = tkinter.ttk.Label(self, text="Это приложение хранит данные о книгах\nЗдесь можно:")

        self.__show_label = tkinter.ttk.Label(self, text="Просмотреть список всех книг:")
        self.__show_button = tkinter.ttk.Button(self, text="Посмотреть", command=self.__open_show)

        self.__add_label = tkinter.ttk.Label(self, text="Добавить новую книгу:")
        self.__add_button = tkinter.ttk.Button(self, text="Добавить", command=self.__open_add)

        self.__find_label = tkinter.ttk.Label(self, text="Найти книги по фамилии автора:")
        self.__find_button = tkinter.ttk.Button(self, text="Найти", command=self.__open_find)

        self.__update_label = tkinter.ttk.Label(self, text="Обновить книгу:")
        self.__update_button = tkinter.ttk.Button(self, text="Обновить", command=self.__open_update)

        self.__delete_label = tkinter.ttk.Label(self, text="Удалить книгу:")
        self.__delete_button = tkinter.ttk.Button(self, text="Удалить", command=self.__open_delete)


    def __open_show(self):
        self.__child_windows.append(Show(self, self.Session))
        self.wait_window(self.__child_windows[-1])

    
    def __open_add(self):
        self.__child_windows.append(Add(self, self.Session))
        self.wait_window(self.__child_windows[-1])


    def __open_find(self):
        self.__child_windows.append(Find(self, self.Session))
        self.wait_window(self.__child_windows[-1])


    def __open_update(self):
        self.__child_windows.append(Update(self, self.Session))
        self.wait_window(self.__child_windows[-1])


    def __open_delete(self):
        self.__child_windows.append(Delete(self, self.Session))
        self.wait_window(self.__child_windows[-1])



    def __pack_widgets(self):
        self.__title_label.pack(pady=5)
        self.__desc_label.pack()

        self.__show_label.pack(pady=3)
        self.__show_button.pack()

        self.__add_label.pack(pady=3)
        self.__add_button.pack()

        self.__find_label.pack(pady=3)
        self.__find_button.pack()

        self.__update_label.pack(pady=3)
        self.__update_button.pack()

        self.__delete_label.pack(pady=3)
        self.__delete_button.pack()



    def run(self):
        self.mainloop()





def main():
    engine = create_engine("sqlite:///library.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    app = App(Session)
    app.run()

if __name__ == "__main__":
    main()