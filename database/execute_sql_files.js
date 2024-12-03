const fs = require("fs");
const path = require("path");
const sqlite3 = require("sqlite3").verbose();

// Caminhos absolutos
const baseDir = path.dirname(__filename); // Diretório do script atual
const sqlFolder = path.join(baseDir, "sql"); // Caminho absoluto da pasta SQL
const dbPath = path.join(baseDir, "bible.db"); // Caminho absoluto do banco de dados SQLite

// Conectar ao banco de dados
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error("Erro ao conectar ao banco de dados:", err.message);
    return;
  }
  console.log("Conectado ao banco de dados SQLite.");
});

// Função para executar um arquivo SQL
function executeSQLFile(filePath) {
  const sqlContent = fs.readFileSync(filePath, "utf8");
  db.exec(sqlContent, (err) => {
    if (err) {
      console.error(`Erro ao executar o arquivo ${filePath}:`, err.message);
    } else {
      console.log(`Arquivo executado com sucesso: ${filePath}`);
    }
  });
}

// Função principal
function executeAllSQLFiles() {
  // Verificar se a pasta existe
  if (!fs.existsSync(sqlFolder)) {
    console.error("A pasta de arquivos SQL não foi encontrada:", sqlFolder);
    return;
  }

  // Ler todos os arquivos na pasta
  const files = fs.readdirSync(sqlFolder).filter((file) => file.endsWith(".sql"));

  if (files.length === 0) {
    console.log("Nenhum arquivo SQL encontrado na pasta:", sqlFolder);
    return;
  }

  console.log(`Encontrados ${files.length} arquivos SQL. Executando...`);

  // Executar cada arquivo SQL
  files.forEach((file) => {
    const filePath = path.join(sqlFolder, file);
    executeSQLFile(filePath);
  });

  // Fechar a conexão após a execução
  db.close((err) => {
    if (err) {
      console.error("Erro ao fechar o banco de dados:", err.message);
    } else {
      console.log("Conexão com o banco de dados encerrada.");
    }
  });
}

// Executar a função principal
executeAllSQLFiles();
