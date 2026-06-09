class Cliente:
    def __init__(self, id, nome, email, senha, telefone, cidade):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.cidade = cidade

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cidade': self.cidade
        }