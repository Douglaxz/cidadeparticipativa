from cidadeparticipativa import db

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: USUÁRIOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_user(db.Model):
    cod_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_user = db.Column(db.String(50), nullable=False)
    password_user = db.Column(db.String(50), nullable=False)
    status_user = db.Column(db.Integer, nullable=False)
    login_user = db.Column(db.String(50), nullable=False)
    cod_usertype = db.Column(db.Integer, nullable=False)
    email_user = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: TIPO USUÁRIOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_usertype(db.Model):
    cod_usertype = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_usertype = db.Column(db.String(50), nullable=False)
    status_usertype = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    
 

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: TIPO SOLCIITAÇÃO
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_tiposolicitacao(db.Model):
    cod_tiposolicitacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_tiposolicitacao = db.Column(db.String(50), nullable=False)
    status_tiposolicitacao = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    


#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: TIPO SERVIÇO
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_tiposervico(db.Model):
    cod_tiposervico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_tiposervico = db.Column(db.String(50), nullable=False)
    status_tiposervico = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: SOLICITAÇÕES
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_solicitacao(db.Model):
    cod_solicitacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc_solicitacao = db.Column(db.String(500), nullable=False)
    cod_tiposervico = db.Column(db.Integer, nullable=False)
    cod_tiposolicitacao = db.Column(db.Integer, nullable=False)
    cep_solicitacao = db.Column(db.Integer, nullable=False)
    rua_solicitacao = db.Column(db.String(50), nullable=False)
    numerores_solicitacao = db.Column(db.String(50), nullable=False)
    bairro_solicitacao = db.Column(db.String(50), nullable=False)
    cidade_solicitacao = db.Column(db.String(50), nullable=False)
    uf_solicitacao = db.Column(db.String(50), nullable=False)
    nome_solicitacao = db.Column(db.String(50), nullable=False)
    sexo_solicitacao = db.Column(db.String(50), nullable=False)
    cepsolicitante_solicitacao = db.Column(db.String(50), nullable=False)
    ruasolicitante_solicitacao = db.Column(db.String(50), nullable=False)
    numeroressolicitante_solicitacao = db.Column(db.String(50), nullable=False)
    bairrosolicitante_solicitacao = db.Column(db.String(50), nullable=False)
    cidadesolicitante_solicitacao = db.Column(db.String(50), nullable=False)
    ufsolicitante_solicitacao = db.Column(db.String(50), nullable=False)    
    status_solicitacao = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Name %r>' % self.name    

#---------------------------------------------------------------------------------------------------------------------------------
#TABELA: SOLICITAÇÕES / FOTOS
#ORIGEM: BANCO DE DADOS
#---------------------------------------------------------------------------------------------------------------------------------
class tb_solicitacao_foto(db.Model):
    cod_solicitacao_foto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arquivo_solicitacao_foto = db.Column(db.String(500), nullable=False)
    cod_solicitacao = db.Column(db.Integer, nullable=False)
