#importações
import os
from cidadeparticipativa import app, db
from models import tb_user, tb_usertype, tb_tiposolicitacao, tb_tiposervico
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, SubmitField,IntegerField, SelectField,PasswordField,DateField,EmailField,BooleanField,RadioField, TextAreaField, TimeField, TelField, DateTimeLocalField,FloatField, DecimalField 

##################################################################################################################################
#PESQUISA
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: pesquisa (geral)
#TIPO: edição
#TABELA: nenhuma
#---------------------------------------------------------------------------------------------------------------------------------
class frm_pesquisa(FlaskForm):
    pesquisa = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    pesquisa_responsiva = StringField('Pesquisa:', [validators.Length(min=1, max=50)],render_kw={"placeholder": "digite sua pesquisa"} )
    salvar = SubmitField('Pesquisar')

##################################################################################################################################
#USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_usuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o nome do usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")])
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o login do usuário"})    
    tipousuario = SelectField('Situação:', coerce=int,  choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')])
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={"placeholder": "digite o email do usuário"})
    salvar = SubmitField('Salvar')


#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: usuários
#TIPO: visualização
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_usuario(FlaskForm):
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)],render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0,"Ativo"),(1,"Inativo")], render_kw={'readonly': True})
    login = StringField('Login:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    tipousuario = SelectField('Tipo:', coerce=int, choices=[(g.cod_usertype, g.desc_usertype) for g in tb_usertype.query.order_by('desc_usertype')], render_kw={'readonly': True})
    email = EmailField('Email:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    salvar = SubmitField('Editar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: trocar senha do usuário
#TIPO: edição
#TABELA: tb_user
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_senha(FlaskForm):
    senhaatual = PasswordField('Senha Atual:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a senha atual"})
    novasenha1 = PasswordField('Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a nova senha"})
    novasenha2 = PasswordField('Confirme Nova Senha:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite novamente a senha"})
    salvar = SubmitField('Editar')  

##################################################################################################################################
#TIPO DE USUÁRIO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: edição
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_tipousuario(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de usuário
#TIPO: visualização
#TABELA: tb_usertype
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_tipousuario(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')    


##################################################################################################################################
#TIPO DE SERVIÇO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de serviço
#TIPO: edição
#TABELA: tb_tiposervico
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_tiposervico(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de serviço
#TIPO: visualização
#TABELA: tb_tiposervico
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_tiposervico(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')  

##################################################################################################################################
#TIPO DE SOLICITAÇÃO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de solicitação
#TIPO: edição
#TABELA: tb_tiposolicitacao
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_tiposolicitacao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição do tipo de usuário"})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: tipo de solicitação
#TIPO: visualização
#TABELA: tb_tiposolicitacao
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_tiposolicitacao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')  

##################################################################################################################################
#SOLICITAÇÃO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: solicitação
#TIPO: edição
#TABELA: tb_solicitacao
#---------------------------------------------------------------------------------------------------------------------------------
class frm_editar_solicitacao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a descrição da solicitação"})
    tiposolicitacao = SelectField('Tipo de Solicitação:', coerce=int,  choices=[(g.cod_tiposolicitacao, g.desc_tiposolicitacao) for g in tb_tiposolicitacao.query.order_by('desc_tiposolicitacao')])
    tiposervico = SelectField('Tipo de Serviço:', coerce=int,  choices=[(g.cod_tiposervico, g.desc_tiposervico) for g in tb_tiposervico.query.order_by('desc_tiposervico')])
    cep = IntegerField('CEP:', [validators.DataRequired()], id="cep")
    rua = StringField('Logradouro:', [validators.DataRequired(), validators.Length(min=1, max=50)], id="rua", render_kw={"placeholder": "digite o nome da rua da solicitação"})
    numero = StringField('Nº:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o número do logradouro da solicitação"})
    bairro = StringField('Bairro:', [validators.DataRequired(), validators.Length(min=1, max=50)], id="bairro", render_kw={"placeholder": "digite o bairro do logradouro da solicitação"})
    uf = StringField('Estado:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a o estado da solicitação"})
    cidade = StringField('Cidade:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a cidade da solicitação"})
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome do solicitante"})
    sexo = StringField('Sexo:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o sexo do solicitante"})
    cepsolicitante = IntegerField('CEP:', [validators.DataRequired()])
    ruasolicitante = StringField('Logradouro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o nome da rua da solicitação"})
    numerosolicitante = StringField('Nº:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o número do logradouro da solicitação"})
    bairrosolicitante = StringField('Bairro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite o bairro do logradouro da solicitação"})
    ufsolicitante = StringField('Estado:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a o estado da solicitação"})
    cidadesolicitante = StringField('Cidade:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={"placeholder": "digite a cidade da solicitação"})    
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')])
    salvar = SubmitField('Salvar')    

#---------------------------------------------------------------------------------------------------------------------------------
#FORMUÁRIO: solicitação
#TIPO: visualização
#TABELA: tb_solicitacao
#---------------------------------------------------------------------------------------------------------------------------------
class frm_visualizar_solicitacao(FlaskForm):
    descricao = StringField('Descrição:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    tiposolicitacao = SelectField('Tipo de Solicitação:', coerce=int,  choices=[(g.cod_tiposolicitacao, g.desc_tiposolicitacao) for g in tb_tiposolicitacao.query.order_by('desc_tiposolicitacao')], render_kw={'readonly': True})
    tiposervico = SelectField('Tipo de Serviço:', coerce=int,  choices=[(g.cod_tiposervico, g.desc_tiposervico) for g in tb_tiposervico.query.order_by('desc_tiposervico')], render_kw={'readonly': True})    
    cep = IntegerField('CEP:', [validators.DataRequired()], render_kw={'readonly': True})
    rua = StringField('Logradouro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    numero = StringField('Nº:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    bairro = StringField('Bairro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    uf = StringField('Estado:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    cidade = StringField('Cidade:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})   
    nome = StringField('Nome:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    sexo = StringField('Sexo:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    cepsolicitante = IntegerField('CEP:', [validators.DataRequired()])
    ruasolicitante = StringField('Logradouro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    numerosolicitante = StringField('Nº:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    bairrosolicitante = StringField('Bairro:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    ufsolicitante = StringField('Estado:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})
    cidadesolicitante = StringField('Cidade:', [validators.DataRequired(), validators.Length(min=1, max=50)], render_kw={'readonly': True})     
    status = SelectField('Situação:', coerce=int, choices=[(0, 'Ativo'),(1, 'Inativo')], render_kw={'readonly': True})
    salvar = SubmitField('Salvar')  
