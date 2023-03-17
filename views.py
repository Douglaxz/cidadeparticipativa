# importação de dependencias
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory,send_file,jsonify
from flask_qrcode import QRcode
from werkzeug.utils import secure_filename
import time
from datetime import date, timedelta
from cidadeparticipativa import app, db
from sqlalchemy import func
from models import tb_user,\
    tb_usertype,\
    tb_tiposolicitacao,\
    tb_tiposervico,\
    tb_solicitacao,\
    tb_solicitacao_foto
from helpers import \
    frm_pesquisa, \
    frm_editar_senha,\
    frm_editar_usuario,\
    frm_visualizar_usuario, \
    frm_visualizar_tipousuario,\
    frm_editar_tipousuario,\
    frm_editar_tiposervico,\
    frm_visualizar_tiposervico,\
    frm_editar_tiposolicitacao,\
    frm_visualizar_tiposolicitacao,\
    frm_editar_solicitacao,\
    frm_visualizar_solicitacao,\
    frm_editar_solicitacao_foto



# ITENS POR PÁGINA
from config import ROWS_PER_PAGE, CHAVE
from flask_bcrypt import generate_password_hash, Bcrypt, check_password_hash

import string
import random
import numbers
import os

##################################################################################################################################
#GERAL
##################################################################################################################################


@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: index
#FUNÇÃO: mostrar pagina principal
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))        
    return render_template('index.html', titulo='Bem vindos')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: logout
#FUNÇÃO: remover seção usuário
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso','success')
    return redirect(url_for('login'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: login
#FUNÇÃO: iniciar seção do usuário
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: autenticar
#FUNÇÃO: autenticar
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/autenticar', methods = ['GET', 'POST'])
def autenticar():
    usuario = tb_user.query.filter_by(login_user=request.form['usuario']).first()
    senha = check_password_hash(usuario.password_user,request.form['senha'])
    if usuario:
        if senha:
            session['usuario_logado'] = usuario.login_user
            session['nomeusuario_logado'] = usuario.name_user
            session['tipousuario_logado'] = usuario.cod_usertype
            session['coduser_logado'] = usuario.cod_user
            flash(usuario.name_user + ' Usuário logado com sucesso','success')
            #return redirect('/')
            return redirect('/')
        else:
            flash('Verifique usuário e senha', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Usuário não logado com sucesso','success')
        return redirect(url_for('login'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: cep
#FUNÇÃO: consultar
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/get_rua_by_cep')
def get_rua_by_cep():
    cep = request.args.get('cep')
    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)
    data = response.json()

    rua = data.get('logradouro')
    return jsonify({'rua': rua})
##################################################################################################################################
#USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: usuario
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/usuario', methods=['POST','GET'])
def usuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('usuario')))        
    form = frm_pesquisa()
    page = request.args.get('page', 1, type=int)
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data

    if pesquisa == "" or pesquisa == None:    
        usuarios = tb_user.query\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)
    else:
        usuarios = tb_user.query\
        .filter(tb_user.name_user.ilike(f'%{pesquisa}%'))\
        .join(tb_usertype, tb_usertype.cod_usertype==tb_user.cod_usertype)\
        .add_columns(tb_user.login_user, tb_user.cod_user, tb_user.name_user, tb_user.status_user, tb_usertype.desc_usertype)\
        .order_by(tb_user.name_user)\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)


    return render_template('usuarios.html', titulo='Usuários', usuarios=usuarios, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoUsuario
#FUNÇÃO: formulário inclusão
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/novoUsuario')
def novoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoUsuario')))     
    form = frm_editar_usuario()
    return render_template('novoUsuario.html', titulo='Novo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuario
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarUsuario', methods=['POST',])
def criarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login',proxima=url_for('criarUsuario')))      
    form = frm_editar_usuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('novoUsuario'))
    nome  = form.nome.data
    status = form.status.data
    login = form.login.data
    tipousuario = form.tipousuario.data
    email = form.email.data
    #criptografar senha
    senha = generate_password_hash("teste@12345").decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('index')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso','success')
    return redirect(url_for('usuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarUsuarioexterno - NÃO DISPONIVEL NESTA VERSAO
#FUNÇÃO: formulário de inclusão
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/criarUsuarioexterno', methods=['POST',])
def criarUsuarioexterno():    
    nome  = request.form['nome']
    status = 0
    email = request.form['email']
    localarroba = email.find("@")
    login = email[0:localarroba]
    tipousuario = 2
    #criptografar senha
    senha = generate_password_hash(request.form['senha']).decode('utf-8')
    usuario = tb_user.query.filter_by(name_user=nome).first()
    if usuario:
        flash ('Usuário já existe','danger')
        return redirect(url_for('login')) 
    novoUsuario = tb_user(name_user=nome, status_user=status, login_user=login, cod_usertype=tipousuario, password_user=senha, email_user=email)
    db.session.add(novoUsuario)
    db.session.commit()
    flash('Usuário criado com sucesso, favor logar com ele','success')
    return redirect(url_for('login'))  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarUsuario
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarUsuario/<int:id>')
def visualizarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = frm_visualizar_usuario()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('visualizarUsuario.html', titulo='Visualizar Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarUsuario
#FUNÇÃO: formulario de edição
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/editarUsuario/<int:id>')
def editarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarUsuario/<int:id>')))  
    usuario = tb_user.query.filter_by(cod_user=id).first()
    form = frm_editar_usuario()
    form.nome.data = usuario.name_user
    form.status.data = usuario.status_user
    form.login.data = usuario.login_user
    form.tipousuario.data = usuario.cod_usertype
    form.email.data = usuario.email_user
    return render_template('editarUsuario.html', titulo='Editar Usuário', id=id, form=form)    
       
#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarUsuario
#FUNÇÃO: alteração no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarUsuario', methods=['POST',])
def atualizarUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = frm_editar_usuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('atualizarUsuario'))
    id = request.form['id']
    usuario = tb_user.query.filter_by(cod_user=request.form['id']).first()
    usuario.name_user = form.nome.data
    usuario.status_user = form.status.data
    usuario.login_user = form.login.data
    usuario.cod_uertype = form.tipousuario.data
    db.session.add(usuario)
    db.session.commit()
    flash('Usuário alterado com sucesso','success')
    return redirect(url_for('visualizarUsuario', id=request.form['id']))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarSenhaUsuario
#FUNÇÃO: formulario de edição
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarSenhaUsuario/')
def editarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarUsuario')))    
    form = frm_editar_senha()
    return render_template('trocarsenha.html', titulo='Trocar Senha', id=id, form=form)  

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: trocarSenhaUsuario
#FUNÇÃO: alteração no banco de dados
#PODE ACESSAR: todos
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/trocarSenhaUsuario', methods=['POST',])
def trocarSenhaUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarUsuario')))          
    form = frm_editar_senha(request.form)
    if form.validate_on_submit():
        id = session['coduser_logado']
        usuario = tb_user.query.filter_by(cod_user=id).first()
        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario'))

        if form.senhaatual.data != usuario.password_user:
            flash('senha atual incorreta','danger')
            return redirect(url_for('editarSenhaUsuario')) 

        if form.novasenha1.data != form.novasenha2.data:
            flash('novas senhas não coincidem','danger')
            return redirect(url_for('editarSenhaUsuario')) 
        usuario.password_user = generate_password_hash(form.novasenha1.data).decode('utf-8')
        db.session.add(usuario)
        db.session.commit()
        flash('senha alterada com sucesso!','success')
    else:
        flash('senha não alterada!','danger')
    return redirect(url_for('editarSenhaUsuario')) 

##################################################################################################################################
#TIPO DE USUARIOS
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tipousuario
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tipousuario', methods=['POST','GET'])
def tipousuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tipousuario')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tiposusuario = tb_usertype.query.order_by(tb_usertype.desc_usertype)\
        .filter(tb_usertype.desc_usertype.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tipousuarios.html', titulo='Tipo Usuário', tiposusuario=tiposusuario, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoUsuario
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoUsuario')
def novoTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoUsuario'))) 
    form = frm_editar_tipousuario()
    return render_template('novoTipoUsuario.html', titulo='Novo Tipo Usuário', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoUsuario
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoUsuario', methods=['POST',])
def criarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoUsuario')))     
    form = frm_editar_tipousuario(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoUsuario'))
    desc  = form.descricao.data
    status = form.status.data
    tipousuario = tb_usertype.query.filter_by(desc_usertype=desc).first()
    if tipousuario:
        flash ('Tipo Usuário já existe','danger')
        return redirect(url_for('tipousuario')) 
    novoTipoUsuario = tb_usertype(desc_usertype=desc, status_usertype=status)
    flash('Tipo de usuário criado com sucesso!','success')
    db.session.add(novoTipoUsuario)
    db.session.commit()
    return redirect(url_for('tipousuario'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoUsuario
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoUsuario/<int:id>')
def visualizarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = frm_visualizar_tipousuario()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('visualizarTipoUsuario.html', titulo='Visualizar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoUsuario
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoUsuario/<int:id>')
def editarTipoUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoUsuario')))  
    tipousuario = tb_usertype.query.filter_by(cod_usertype=id).first()
    form = frm_editar_tipousuario()
    form.descricao.data = tipousuario.desc_usertype
    form.status.data = tipousuario.status_usertype
    return render_template('editarTipoUsuario.html', titulo='Editar Tipo Usuário', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoUsuario
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoUsuario', methods=['POST',])
def atualizarTipoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoUsuario')))      
    form = frm_editar_tipousuario(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tipousuario = tb_usertype.query.filter_by(cod_usertype=request.form['id']).first()
        tipousuario.desc_usertype = form.descricao.data
        tipousuario.status_usertype = form.status.data
        db.session.add(tipousuario)
        db.session.commit()
        flash('Tipo de usuário atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoUsuario', id=request.form['id']))

##################################################################################################################################
#TIPO DE SOLICITAÇÃO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tiposolicitacao
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tiposolicitacao', methods=['POST','GET'])
def tiposolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tiposolicitacao')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tipossolicitacao = tb_tiposolicitacao.query.order_by(tb_tiposolicitacao.desc_tiposolicitacao)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tipossolicitacao = tb_tiposolicitacao.query.order_by(tb_tiposolicitacao.desc_tiposolicitacao)\
        .filter(tb_tiposolicitacao.desc_tiposolicitacao.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tiposolicitacao.html', titulo='Tipo Solicitação', tipossolicitacao=tipossolicitacao, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoSolicitacao
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoSolicitacao')
def novoTipoSolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoSolicitacao'))) 
    form = frm_editar_tiposolicitacao()
    return render_template('novoTiposolicitacao.html', titulo='Novo Tipo Solicitação', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoSolicitacao
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoSolicitacao', methods=['POST',])
def criarTipoSolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTiposolicitacao')))     
    form = frm_editar_tiposolicitacao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTiposolicitacao'))
    desc  = form.descricao.data
    status = form.status.data
    tiposolicitacao = tb_tiposolicitacao.query.filter_by(desc_tiposolicitacao=desc).first()
    if tiposolicitacao:
        flash ('Tipo Solicitação já existe','danger')
        return redirect(url_for('tiposolicitacao')) 
    novoTiposolicitacao = tb_tiposolicitacao(desc_tiposolicitacao=desc, status_tiposolicitacao=status)
    flash('Tipo de solicitação criado com sucesso!','success')
    db.session.add(novoTiposolicitacao)
    db.session.commit()
    return redirect(url_for('tiposolicitacao'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoSolicitacao
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoSolicitacao/<int:id>')
def visualizarTipoSolicitacao(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoSolicitacao')))  
    tiposolicitacao = tb_tiposolicitacao.query.filter_by(cod_tiposolicitacao=id).first()
    form = frm_visualizar_tiposolicitacao()
    form.descricao.data = tiposolicitacao.desc_tiposolicitacao
    form.status.data = tiposolicitacao.status_tiposolicitacao
    return render_template('visualizarTipoSolicitacao.html', titulo='Visualizar Tipo Solicitação', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoSolicitacao
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoSolicitacao/<int:id>')
def editarTipoSolicitacao(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoSolicitacao')))  
    tiposolicitacao = tb_tiposolicitacao.query.filter_by(cod_tiposolicitacao=id).first()
    form = frm_editar_tiposolicitacao()
    form.descricao.data = tiposolicitacao.desc_tiposolicitacao
    form.status.data = tiposolicitacao.status_tiposolicitacao
    return render_template('editarTipoSolicitacao.html', titulo='Editar Tipo Solicitação', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoSolicitacao
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoSolicitacao', methods=['POST',])
def atualizarTipoSolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoSolicitacao')))      
    form = frm_editar_tiposolicitacao(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tiposolicitacao = tb_tiposolicitacao.query.filter_by(cod_tiposolicitacao=request.form['id']).first()
        tiposolicitacao.desc_tiposolicitacao = form.descricao.data
        tiposolicitacao.status_tiposolicitacao = form.status.data
        db.session.add(tiposolicitacao)
        db.session.commit()
        flash('Tipo de solicitação atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoSolicitacao', id=request.form['id']))

##################################################################################################################################
#TIPO DE SERVIÇO
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: tiposervico
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/tiposervico', methods=['POST','GET'])
def tiposervico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('tiposervico')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        tiposservico = tb_tiposervico.query.order_by(tb_tiposervico.desc_tiposervico)\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        tiposservico = tb_tiposervico.query.order_by(tb_tiposervico.desc_tiposervico)\
        .filter(tb_tiposervico.desc_tiposervico.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('tiposervico.html', titulo='Tipo Serviço', tiposservico=tiposservico, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoTipoServico
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoTipoServico')
def novoTipoServico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoTipoServico'))) 
    form = frm_editar_tiposervico()
    return render_template('novoTipoServico.html', titulo='Novo Tipo Serviço', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarTipoServico
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarTipoServico', methods=['POST',])
def criarTipoServico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarTipoServico')))     
    form = frm_editar_tiposervico(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarTipoServico'))
    desc  = form.descricao.data
    status = form.status.data
    tiposervico = tb_tiposervico.query.filter_by(desc_tiposervico=desc).first()
    if tiposervico:
        flash ('Tipo Serviço já existe','danger')
        return redirect(url_for('tiposervico')) 
    novotiposervico = tb_tiposervico(desc_tiposervico=desc, status_tiposervico=status)
    flash('Tipo de serviço criado com sucesso!','success')
    db.session.add(novotiposervico)
    db.session.commit()
    return redirect(url_for('tiposervico'))

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarTipoServico
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarTipoServico/<int:id>')
def visualizarTipoServico(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarTipoServico')))  
    tiposervico = tb_tiposervico.query.filter_by(cod_tiposervico=id).first()
    form = frm_visualizar_tiposervico()
    form.descricao.data = tiposervico.desc_tiposervico
    form.status.data = tiposervico.status_tiposervico
    return render_template('visualizarTipoServico.html', titulo='Visualizar Tipo Solicitação', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarTipoServico
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarTipoServico/<int:id>')
def editarTipoServico(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarTipoSolicitacao')))  
    tiposervico = tb_tiposervico.query.filter_by(cod_tiposervico=id).first()
    form = frm_editar_tiposervico()
    form.descricao.data = tiposervico.desc_tiposervico
    form.status.data = tiposervico.status_tiposervico
    return render_template('editarTipoServico.html', titulo='Editar Tipo Serviço', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarTipoServico
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarTipoServico', methods=['POST',])
def atualizarTipoServico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarTipoServico')))      
    form = frm_editar_tiposervico(request.form)
    if form.validate_on_submit():
        id = request.form['id']
        tiposervico = tb_tiposervico.query.filter_by(cod_tiposervico=request.form['id']).first()
        tiposervico.desc_tiposervico = form.descricao.data
        tiposervico.status_tiposervico = form.status.data
        db.session.add(tiposervico)
        db.session.commit()
        flash('Tipo de serviço atualizado com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('visualizarTipoServico', id=request.form['id']))

##################################################################################################################################
#SOLICITAÇÕES
##################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: solicitacao
#FUNÇÃO: listar
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/solicitacao', methods=['POST','GET'])
def solicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('solicitacao')))         
    page = request.args.get('page', 1, type=int)
    form = frm_pesquisa()   
    pesquisa = form.pesquisa.data
    if pesquisa == "":
        pesquisa = form.pesquisa_responsiva.data
    
    if pesquisa == "" or pesquisa == None:     
        solicitacoes = tb_solicitacao.query\
        .join(tb_tiposervico, tb_tiposervico.cod_tiposervico==tb_solicitacao.cod_tiposervico)\
        .join(tb_tiposolicitacao, tb_tiposolicitacao.cod_tiposolicitacao==tb_solicitacao.cod_tiposolicitacao)\
        .add_columns(tb_tiposolicitacao.desc_tiposolicitacao,\
                     tb_tiposervico.desc_tiposervico, \
                     tb_solicitacao.status_solicitacao,\
                     tb_solicitacao.cod_solicitacao,\
                     tb_solicitacao.data_solicitacao,\
                     tb_solicitacao.datacad_solicitacao
                  )\
        .order_by(tb_solicitacao.datacad_solicitacao.desc())\
        .paginate(page=page, per_page=ROWS_PER_PAGE , error_out=False)
    else:
        solicitacoes = tb_solicitacao.query\
        .join(tb_tiposervico, tb_tiposervico.cod_tiposervico==tb_solicitacao.cod_tiposervico)\
        .join(tb_tiposolicitacao, tb_tiposolicitacao.cod_tiposolicitacao==tb_solicitacao.cod_tiposolicitacao)\
        .add_columns(tb_tiposolicitacao.desc_tiposolicitacao,\
                     tb_tiposervico.desc_tiposervico, \
                     tb_solicitacao.status_solicitacao,\
                     tb_solicitacao.cod_solicitacao,\
                     tb_solicitacao.data_solicitacao,\
                     tb_solicitacao.datacad_solicitacao
                  )\
        .order_by(tb_solicitacao.datacad_solicitacao.desc())\
        .filter(tb_solicitacao.desc_solicitacao.ilike(f'%{pesquisa}%'))\
        .paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)        
    return render_template('solicitacao.html', titulo='Solicitações', solicitacoes=solicitacoes, form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoSolicitacao
#FUNÇÃO: formulario de inclusão
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/novoSolicitacao')
def novoSolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoSolicitacao'))) 
    form = frm_editar_solicitacao()
    return render_template('novoSolicitacao.html', titulo='Nova Solicitação', form=form)

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: criarSolicitacao
#FUNÇÃO: inclusão no banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/criarSolicitacao', methods=['POST',])
def criarSolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('criarSolicitacao')))     
    form = frm_editar_solicitacao(request.form)
    if not form.validate_on_submit():
        flash('Por favor, preencha todos os dados','danger')
        return redirect(url_for('criarSolicitacao'))
    descricao  = form.descricao.data
    status = form.status.data
    tiposolicitacao  = form.tiposolicitacao.data
    tiposervico  = form.tiposervico.data
    cep  = form.cep.data
    rua  = form.rua.data
    numero  = form.numero.data
    bairro  = form.bairro.data
    uf  = form.uf.data
    cidade  = form.cidade.data
    nome  = form.nome.data
    sexo  = form.sexo.data
    cepsolicitante  = form.cepsolicitante.data
    ruasolicitante  = form.ruasolicitante.data
    numerosolicitante  = form.numerosolicitante.data
    bairrosolicitante  = form.bairrosolicitante.data
    ufsolicitante  = form.ufsolicitante.data
    cidadesolicitante  = form.cidadesolicitante.data
    novoSolicitacao = tb_solicitacao(desc_solicitacao = descricao,\
                                    cod_tiposervico = tiposolicitacao,\
                                    cod_tiposolicitacao = tiposervico,\
                                    cep_solicitacao = cep,\
                                    rua_solicitacao = rua,\
                                    numerores_solicitacao = numero,\
                                    bairro_solicitacao = bairro,\
                                    cidade_solicitacao = uf,\
                                    uf_solicitacao = cidade,\
                                    nome_solicitacao = nome,\
                                    sexo_solicitacao = sexo,\
                                    cepsolicitante_solicitacao = cepsolicitante,\
                                    ruasolicitante_solicitacao = ruasolicitante,\
                                    numeroressolicitante_solicitacao = numerosolicitante,\
                                    bairrosolicitante_solicitacao = bairrosolicitante,\
                                    cidadesolicitante_solicitacao = cidadesolicitante,\
                                    ufsolicitante_solicitacao = ufsolicitante,\
                                    status_solicitacao=status\
                                     )
    flash('Solicitação criada com sucesso!','success')
    db.session.add(novoSolicitacao)
    db.session.commit()

    solicitacao = tb_solicitacao.query.filter_by(desc_solicitacao=descricao).first()
    id = solicitacao.cod_solicitacao
    #return redirect(url_for('solicitacao'))
    return redirect(url_for('novoSolicitacaoFoto',id=id))


#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: novoSolicitacaoFoto
#FUNÇÃO: inclusão das imagens banco de dados
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/novoSolicitacaoFoto/<int:id>')
def novoSolicitacaoFoto(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('novoSolicitacaoFoto'))) 
    form = frm_editar_solicitacao_foto()
    return render_template('novoSolicitacaoFoto.html', titulo='Inserir imagens', form=form, id=id)

@app.route('/solicitacao_foto/<int:id>', methods=['POST'])
def solicitacao_foto(id):
    arquivo = request.files['imagem']
    nome_arquivo = secure_filename(arquivo.filename)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    nome_unico = f"{nome_base}_{timestamp}{extensao}"
    caminho_arquivo = os.path.join(app.config['UPLOAD_PATH'], nome_unico)
    arquivo.save(caminho_arquivo)

    flash('Imagem carregada com sucesso!','success')
    novoSolicitacaoFoto = tb_solicitacao_foto(cod_solicitacao=id,arquivo_solicitacao_foto=nome_unico)
    db.session.add(novoSolicitacaoFoto)
    db.session.commit()
    return redirect(url_for('novoSolicitacaoFoto',id=id))


@app.route('/excluirFoto/<int:id>')
def excluirFoto(id):
    solicitacao_foto = tb_solicitacao_foto.query.filter_by(cod_solicitacao_foto=id).first()
    idsolicitacao = solicitacao_foto.cod_solicitacao
    caminho_arquivo = os.path.join(app.config['UPLOAD_PATH'], solicitacao_foto.arquivo_solicitacao_foto)
    try:
        os.remove(caminho_arquivo)
        msg = "Arquivo excluído com sucesso!"
    except Exception as e:
        msg = f"Ocorreu um erro ao excluir o arquivo: {e}"

    apagarFoto = tb_solicitacao_foto.query.filter_by(cod_solicitacao_foto=id).one()
    db.session.delete(apagarFoto)
    db.session.commit()

    flash('Imagem apagada com sucesso!','success')
    return redirect(url_for('visualizarSolicitacao',id=idsolicitacao))



#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: visualizarSolicitacao
#FUNÇÃO: formulario de visualização
#PODE ACESSAR: administrador
#--------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/visualizarSolicitacao/<int:id>')
def visualizarSolicitacao(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('visualizarSolicitacao')))  
    solicitacao = tb_solicitacao.query.filter_by(cod_solicitacao=id).first()
    solicitacao_foto = tb_solicitacao_foto.query.filter_by(cod_solicitacao=id).all()
    nomes_arquivos = [foto.arquivo_solicitacao_foto for foto in solicitacao_foto]
    form = frm_visualizar_solicitacao()
    form.datacadastro.data = solicitacao.datacad_solicitacao
    form.data.data = solicitacao.data_solicitacao
    form.fone.data = solicitacao.fone_solicitacao
    form.descricao.data = solicitacao.desc_solicitacao
    form.tiposolicitacao.data = solicitacao.cod_tiposolicitacao
    form.tiposervico.data = solicitacao.cod_tiposervico
    form.cep.data = solicitacao.cep_solicitacao
    form.rua.data = solicitacao.rua_solicitacao
    form.numero.data = solicitacao.numerores_solicitacao
    form.bairro.data = solicitacao.bairro_solicitacao
    form.uf.data = solicitacao.uf_solicitacao
    form.cidade.data = solicitacao.cidade_solicitacao
    form.nome.data = solicitacao.nome_solicitacao
    form.sexo.data = solicitacao.sexo_solicitacao
    form.cepsolicitante.data = solicitacao.cepsolicitante_solicitacao
    form.ruasolicitante.data = solicitacao.ruasolicitante_solicitacao
    form.numerosolicitante.data = solicitacao.numeroressolicitante_solicitacao
    form.bairrosolicitante.data = solicitacao.bairrosolicitante_solicitacao
    form.ufsolicitante.data = solicitacao.ufsolicitante_solicitacao
    form.cidadesolicitante.data = solicitacao.cidadesolicitante_solicitacao
    form.status.data = solicitacao.status_solicitacao
    endereco = solicitacao.ruasolicitante_solicitacao +","+ solicitacao.numeroressolicitante_solicitacao + "," + solicitacao.bairrosolicitante_solicitacao + "," + solicitacao.cidadesolicitante_solicitacao + solicitacao.ufsolicitante_solicitacao
    return render_template('visualizarSolicitacao.html', titulo='Visualizar Solicitacao', id=id, form=form, nomes_arquivos=nomes_arquivos,solicitacao_foto=solicitacao_foto,endereco=endereco)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: editarSolicitacao
##FUNÇÃO: formulário de edição
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/editarSolicitacao/<int:id>')
def editarSolicitacao(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('editarSolicitacao')))  
    solicitacao = tb_solicitacao.query.filter_by(cod_solicitacao=id).first()
    form = frm_editar_solicitacao()
    form.datacadastro.data = solicitacao.datacad_solicitacao
    form.data.data = solicitacao.data_solicitacao
    form.fone.data = solicitacao.fone_solicitacao
    form.descricao.data = solicitacao.desc_solicitacao
    form.tiposolicitacao.data = solicitacao.cod_tiposolicitacao
    form.tiposervico.data = solicitacao.cod_tiposervico
    form.cep.data = solicitacao.cep_solicitacao
    form.rua.data = solicitacao.rua_solicitacao
    form.numero.data = solicitacao.numerores_solicitacao
    form.bairro.data = solicitacao.bairro_solicitacao
    form.uf.data = solicitacao.uf_solicitacao
    form.cidade.data = solicitacao.cidade_solicitacao
    form.nome.data = solicitacao.nome_solicitacao
    form.sexo.data = solicitacao.sexo_solicitacao
    form.cepsolicitante.data = solicitacao.cepsolicitante_solicitacao
    form.ruasolicitante.data = solicitacao.ruasolicitante_solicitacao
    form.numerosolicitante.data = solicitacao.numeroressolicitante_solicitacao
    form.bairrosolicitante.data = solicitacao.bairrosolicitante_solicitacao
    form.ufsolicitante.data = solicitacao.ufsolicitante_solicitacao
    form.cidadesolicitante.data = solicitacao.cidadesolicitante_solicitacao
    form.status.data = solicitacao.status_solicitacao
    return render_template('editarSolicitacao.html', titulo='Editar Solicitação', id=id, form=form)   

#---------------------------------------------------------------------------------------------------------------------------------
#ROTA: atualizarSolicitacao
#FUNÇÃO: alterar informações no banco de dados
#PODE ACESSAR: administrador
#---------------------------------------------------------------------------------------------------------------------------------
@app.route('/atualizarSolicitacao', methods=['POST',])
def atualizarSolicitacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Sessão expirou, favor logar novamente','danger')
        return redirect(url_for('login',proxima=url_for('atualizarSolicitacao')))      
    form = frm_editar_solicitacao(request.form)
    msg = "1111"
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Erro no campo "{getattr(form, field).label.text}": {error}')
            #return redirect(url_for('editarSolicitacao', id=request.form['id']))
            msg = msg + (f'Erro no campo "{getattr(form, field).label.text}": {error}')
    

    
    if form.validate_on_submit():
        id = request.form['id']
        solicitacao = tb_solicitacao.query.filter_by(cod_solicitacao=request.form['id']).first()
        solicitacao.datacad_solicitacao = form.datacadastro.data
        solicitacao.data_solicitacao = form.data.data
        solicitacao.fone_solicitacao = form.fone.data
        solicitacao.desc_solicitacao = form.descricao.data
        solicitacao.status_solicitacao = form.status.data
        solicitacao.cod_tiposervico = form.tiposervico.data
        solicitacao.cod_tiposolicitacao = form.tiposolicitacao.data
        solicitacao.cep_solicitacao = form.cep.data
        solicitacao.rua_solicitacao = form.rua.data
        solicitacao.numerores_solicitacao = form.numero.data
        solicitacao.bairro_solicitacao = form.bairro.data
        solicitacao.cidade_solicitacao = form.uf.data
        solicitacao.uf_solicitacao = form.cidade.data
        solicitacao.nome_solicitacao = form.nome.data
        solicitacao.sexo_solicitacao = form.sexo.data
        solicitacao.cepsolicitante_solicitacao = form.cepsolicitante.data
        solicitacao.ruasolicitante_solicitacao = form.ruasolicitante.data
        solicitacao.numeroressolicitante_solicitacao = form.numerosolicitante.data
        solicitacao.bairrosolicitante_solicitacao = form.bairrosolicitante.data
        solicitacao.cidadesolicitante_solicitacao = form.cidadesolicitante.data
        solicitacao.ufsolicitante_solicitacao = form.ufsolicitante.data
        db.session.add(solicitacao)
        db.session.commit()
        flash('Solicitação atualizada com sucesso!','success')
    else:
        flash('Favor verificar os campos!','danger')
    return redirect(url_for('editarSolicitacao', id=request.form['id']))