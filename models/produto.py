class Produto:
    def __init__(self, id, nome, categoria, preco, estoque, foto):
        self.id = id
        self.nome = nome
        self.categoria = categoria
        self.preco = float(preco)
        self.estoque = estoque
        self.foto = foto

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'categoria': self.categoria,
            'preco': self.preco,
            'estoque': self.estoque,
            'foto': self.foto
        }