import sqlite3

def initialize_db():
    connection = sqlite3.connect('./database/bible.db')
    cursor = connection.cursor()

    # Criação da tabela
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bible (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL
        );
    ''')
    # Dados de exemplo
    cursor.executemany('''
        INSERT INTO bible (version, book, chapter, verse, text)
        VALUES (?, ?, ?, ?, ?)
    ''', [
        ("NVI", "Gênesis", 1, 1, "No princípio Deus criou os céus e a terra."),
        ("NVI", "Gênesis", 1, 2, "Era a terra sem forma e vazia; trevas cobriam a face do abismo...")
    ])

    connection.commit()
    connection.close()

if __name__ == "__main__":
    initialize_db()
