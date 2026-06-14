CREATE DATABASE apollo_shop_bd;
USE apollo_shop_bd;

CREATE TABLE clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    cidade VARCHAR(80),
    data_cadastro DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE produtos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    preco DECIMAL(10,2) NOT NULL,
    estoque INT DEFAULT 0,
    foto VARCHAR(255), 
    data_cadastro DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE pedidos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT NOT NULL,
    data_pedido DATE DEFAULT (CURRENT_DATE),
    valor_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE itens_pedido (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    preco_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

INSERT INTO produtos (nome, categoria, preco, estoque, foto) VALUES
('Guitarra Fender Stratocaster', 'Cordas', 5999.90, 5, 'fender_strato.png'),
('Teclado Sintetizador Roland XPS-10', 'Teclados', 3499.00, 8, 'roland_xps10.webp'),
('Violão Acústico Taylor GS Mini', 'Cordas', 4200.00, 12, 'taylor_gs.webp'),
('Amplificador Marshall DSL40CR', 'Áudio', 2899.90, 6, 'marshall_dsl40.jpg'),
('Bateria Eletrónica Yamaha DTX402K', 'Percussão', 5100.00, 4, 'yamaha_dtx.jpg'),
('Interface de Áudio Focusrite Scarlett 2i2', 'Áudio', 1299.00, 25, 'focusrite_2i2.webp'),
('Microfone Dinâmico Shure SM58', 'Áudio', 899.00, 40, 'shure_sm58.jpg'),
('Controlador MIDI Novation Launchkey', 'Teclados', 1599.90, 15, 'novation_launch.png'),
('Baixo Ibanez GSR200', 'Cordas', 2199.90, 7, 'ibanez_gsr200.webp'),
('Cajón FSA Strike SK400', 'Percussão', 749.90, 10, 'cajon_fsa.webp');