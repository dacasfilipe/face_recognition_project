# ------------------------------------------------------------------------------------------------------------
# Este é um programa em Python que utiliza a biblioteca de reconhecimento facial "face recognition".
# Ele permite adicionar fotos ao banco de dados,
# excluir pessoas do banco de dados,
# ativar o modo de scanner, que exibe o nome da pessoa ao entrar em frente à câmera.
# O programa pode ser utilizado para fins de segurança ou controle de acesso, se adaptado.
# Feito por Davicjc por meio de pesquisas, estudos de bibliotecas e análise de códigos de terceiros.
# ------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------
# PARA PERSONALIZAR, DÊ UMA OLHADA NA FUNÇÃO "key()" NO FINAL DO CÓDIGO
# "LEIA AS INSTRUÇÕES NO GITHUB ANTES DE USAR O PROGRAMA (EM PORTUGUÊS)"
# ------------------------------------------------------------------------------------------------------------
#   IMPLEMENTAÇÕES FUTURAS:
# chamada com reconhecimento facial
# https://github.com/Alisson-tech/Chamada_Escolar_com_Reconhecimento_Facial
# ----------------------------------------------------------------------------
# PRÓXIMOS ITENS A ADICIONAR NO PROJETO
# Disponibilizar a API de acesso ao banco de dados
# fazer método e rota para disponibilizar logs para aplicação de gestão
# Desenvolver logins de acesso a usuários.

# importa as bibliotecas necessárias
import cv2
import os
import random
import numpy as np
import glob
import face_recognition
import webbrowser
from pathlib import Path
import time
import tkinter as tk
import random
import mysql.connector
from tkcalendar import DateEntry
import datetime

# Configuração da conexão com o banco de dados
config = {
    'user': 'root',  # Substitua 'username' pelo nome de usuário do MySQL
    'password': 'root',  # Substitua 'password' pela senha do MySQL
    'host': 'localhost',
    'database': 'face_safety',  # Substitua 'nome_do_banco' pelo nome do seu banco de dados
    'raise_on_warnings': True
}

# função para inserir os dados do usuário na tabela do banco de dados
def insert_into_database(nome, cpf, datanascimento, tipo, file_patch):
    # Conecta ao banco de dados
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Insere os dados na tabela (Substitua 'nome_da_tabela' pelo nome da sua tabela)
    query = "INSERT INTO pessoa (nome,cpf,datanascimento,tipo,file_patch) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (nome, cpf, datanascimento, tipo, file_patch))
    # "INSERT INTO log (data, Pessoa_idPessoa, controlador_idcontrolador) VALUES (%s, %s, %s)"
    # Encerra a conexão+
    connection.commit()
    cursor.close()
    connection.close()

def insert_into_log(data, pessoa_id, controlador_id):
    # Conexão com o banco de dados
    # Conecta ao banco de dados
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Query SQL para inserir um registro na tabela log
    sql = "INSERT INTO log (data, Pessoa_idPessoa, controlador_idcontrolador) VALUES (%s, %s, %s)"
    val = (data, pessoa_id, controlador_id)

    # cursor.execute(sql, val)
    # Encerra a conexão+
    connection.commit()
    cursor.close()
    connection.close()

# 1 Função que cria a janela principal
def lobby():
    try:
        # Cria uma janela
        lobby_tk = tk.Tk()

        # Bloqueia o redimensionamento da janela
        lobby_tk.resizable(width=False, height=False)

        # Define o título da janela
        lobby_tk.title("FACE SAFETY")

        # Define o tamanho da janela
        lobby_tk.geometry("620x540")

        # Define a cor de fundo da janela
        lobby_tk.configure(background="black")

        # Define os componentes da janela
        txt_label = tk.Label(lobby_tk, text="Bem vindo ao Face Safety,\no que deseja fazer?", font=(
            "Arial", 18), bg="black", fg="white")
        Badd_button = tk.Button(lobby_tk, text="Adicionar Pessoa", font=(
            # aqui chama a função de cadastro
            "Arial Black", 10), bg="black", fg="white", cursor="hand2", command=capture_name)
        Bremv_button = tk.Button(lobby_tk, text="Remover Pessoa", font=(
            "Arial Black", 10), bg="black", fg="red", cursor="hand2", command=apagar_imagem)
        Scan_button = tk.Button(lobby_tk, text="Ligar Scanner", font=(
            "Arial Black", 10), bg="black", fg="green", cursor="hand2", command=reconhecer)
        Addadm_button = tk.Button(lobby_tk, text="+ Adm", font=(
            "Arial Black", 10), bg="black", fg="white", cursor="hand2", command=admadd)
        Rmva_button = tk.Button(lobby_tk, text="- Adm", font=(
            "Arial Black", 10), bg="black", fg="red", cursor="hand2", command=admrvm)
        # cjc_label = tk.Label(lobby_tk, text="By: Davicjc", font=(
        #    "arial", 8), bg="black", fg="blue", cursor="hand2")

        # Posiciona os componentes na janela
        txt_label.pack()
        Badd_button.place(x=10, y=100)
        Bremv_button.place(x=10, y=150)
        Scan_button.place(x=10, y=200)
        Addadm_button.place(x=200, y=100)
        Rmva_button.place(x=200, y=150)
        # cjc_label.place(x=255, y=220)

        # Loop da janela
        lobby_tk.mainloop()

    # Caso ocorra algum erro, exibe uma mensagem de erro
    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-1'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 1")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nlobby_tk '1'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error, text="Erro em: Criar a janela principal\nProcure ajuda!", font=(
            "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# 2 Função modificada que capturas os dados do usuário e salva no banco de dados.
def capture_name():
    try:
        name_window = tk.Tk()
        name_window.resizable(width=False, height=False)
        name_window.title("Seu Nome:")
        name_window.geometry("290x420")
        name_window.configure(background="black")

        def clear():
            nome = nm_entry.get()
            nome_bd = nm_entry.get()
            cpf = cpf_entry.get()
            datanascimento = datanascimento_entry.get()
            tipo = tipo_entry.get()

            if nome == "":
                # adicionar tratamento para "Não inseriu nome"
                nome = "NoName " + ".jpg"
            else:
                nome = nome + ".jpg"
            name_window.destroy()

            #chama função para capturar imagem do usuário
            nova_imagem(nome_bd, nome, cpf, datanascimento, tipo)

        # Componentes da janela
        nm_label = tk.Label(name_window, text="Nome:", bg="black", fg="white")
        nm_entry = tk.Entry(name_window, width=40)

        cpf_label = tk.Label(name_window, text="CPF:", bg="black", fg="white")
        cpf_entry = tk.Entry(name_window, width=40)

        # Format the selected date as 'YYYY-MM-DD'
        datanascimento_label = tk.Label(name_window, text="Data de Nascimento:", bg="black", fg="white")
        datanascimento_entry = DateEntry(name_window, width=12, background='darkblue', foreground='white',
                                         borderwidth=2, date_pattern='dd/mm/yyyy')
        '''
        datanascimento_label = tk.Label(name_window, text="Data de Nascimento:", bg="black", fg="white")
        datanascimento_entry = tk.Entry(name_window, width=40)
        '''
        tipo_label = tk.Label(name_window, text="Tipo:", bg="black", fg="white")
        tipo_entry = tk.Entry(name_window, width=40)

        nm_button = tk.Button(name_window, text="OK", font=("Arial", 9), bg="black", fg="white", cursor="hand2",
                              command=clear)

        # Posicionando os componentes
        nm_label.place(x=5, y=5)
        nm_entry.place(x=5, y=25)

        cpf_label.place(x=5, y=55)
        cpf_entry.place(x=5, y=75)

        datanascimento_label.place(x=5, y=105)
        datanascimento_entry.place(x=5, y=125)

        tipo_label.place(x=5, y=155)
        tipo_entry.place(x=5, y=175)

        nm_button.place(x=260, y=5)

        name_window.mainloop()

        # Caso ocorra algum erro, exibe uma mensagem de erro
    except:

        def close():
            error.destroy()

        print("Ocorreu um erro 'code-2'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 2")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nNome '2'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error, text="Erro em: Capturar o nome da pessoa\nDica: Nome invalido ou ERRO!", font=(
            "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()

# 2 Função que captura o nome da pessoa
def close_window(window):
    window.destroy()
# 3 Função que captura a imagem da câmera com o nome da pessoa
# Mostra o nome da pessoa salvo
def nameinfo(nome):
    window = tk.Tk()
    window.resizable(width=False, height=False)
    window.title("Nome da Pessoa:")
    window.geometry("290x30")
    window.configure(background="black")
    label = tk.Label(window, text="Nome: " + nome + " Salvo!", font=("Arial", 9), bg="black", fg="white")
    label.place(x=5, y=8)
    button = tk.Button(window, text="OK", font=("Arial", 9), bg="black", fg="white", cursor="hand2", command=lambda: close_window(window))
    button.place(x=260, y=5)
    window.mainloop()

def nova_imagem(nome_bd, nome, cpf, datanascimento, tipo):
    try:
        # Define o nome da pasta onde as fotos serão salvas
        folder_name = "Fotos Data 'Face Safety'"

        # Define o caminho completo da pasta na área de trabalho
        desktop_path = os.path.join(os.path.join(
            os.path.expanduser('~')), 'Desktop')
        folder_path = os.path.join(desktop_path, folder_name)

        # Verifica se a pasta já existe, caso contrário, cria a pasta
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Captura a imagem da câmera
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        # Define o tamanho da janela
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Define a resolução da câmera
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

        # Define a taxa de quadros da câmera
        cap.set(cv2.CAP_PROP_FPS, 60)

        # Aguarda o usuário apertar qualquer tecla para tirar a sua foto
        while True:
            ret, frame = cap.read()
            cv2.imshow("Captura Rosto - 'Aperte Qualquer Tecla'", frame)
            if cv2.waitKey(1) != -1:
                break

        # Salva a imagem capturada na pasta criada
        file_path = os.path.join(folder_path, nome)
        cv2.imwrite(file_path, frame)
        # filipe colocou chama função insert no banco

        # Convert Brazilian date format (DD/MM/YYYY) to Python date object
        datanascimento = datetime.datetime.strptime(datanascimento, '%d/%m/%Y').date()

        # Convert date to desired database format (YYYY-MM-DD)
        datanascimento_db = datanascimento.strftime('%Y-%m-%d')
        print(nome)
        print(cpf)
        print(datanascimento)
        print(tipo)
        print(file_path)

        insert_into_database(nome_bd, cpf, datanascimento_db, tipo, file_path)
        nameinfo(nome_bd)


    # Caso ocorra algum erro, exibe uma mensagem de erro
    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-3'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 3")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nNova_Imagem '3'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error, text="Erro em: Captura a imagem da câmera\nDica: Erro camera/Procure ajuda!",
                              font=(
                                  "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# 4 Tira um nome da lista de ADM

def admrvm():
    try:
        # Cria uma janela
        admadd = tk.Tk()

        # Bloqueia o redimensionamento da janela
        admadd.resizable(width=False, height=False)

        # Define o título da janela
        admadd.title("Remover ADM: ")

        # Define o tamanho da janela
        admadd.geometry("360x200")

        # Define a cor de fundo da janela
        admadd.configure(background="black")

        # Titulo da janela na aba
        esc_label = tk.Label(admadd, text="Nome que deseja remover de ADM:", font=(
            "Arial", 9), bg="black", fg="white")
        esc_label.place(x=145, y=5)

        # Mensagem e avisos
        avs_label = tk.Label(
            admadd, text="Reinicie a aba ao remover !", bg="black", fg="red")
        avs_label.place(x=170, y=180)

        # Aviso de "sem banco de dados encontrados"
        avs_label2 = tk.Label(
            admadd, text="0 Cadastros Encontrados", bg="black", fg="red")
        avs_label2.place(y=5)

        # Campo de texto para digitar o nome da pessoa
        esc_entry = tk.Entry(admadd, width=30)
        esc_entry.place(x=150, y=30)

        def remove():
            # Pegar o nome da pessoa
            get = esc_entry.get()

            # Verifica se o campo está vazio
            if get == "":
                print("Campo vazio!", "\n")
                return

            else:
                # Define o caminho da pasta "Fotos Data 'Face Safety'" na área de trabalho
                pasta = os.path.join(str(Path.home()), "Desktop", "ADM Data 'Face Safety'")

                # Define o caminho completo do arquivo "AMDs.txt" dentro da pasta
                arquivo = os.path.join(pasta, "AMDs.txt")

                # Verifica se o arquivo existe e cria um novo arquivo vazio se ele não existir
                if not os.path.exists(arquivo):
                    print("Lista vazia!", "\n")
                    return

                # Lê o conteúdo do arquivo
                with open(arquivo, "r") as f:
                    conteudo = f.read()

                # Divide o conteúdo em linhas
                linhas = conteudo.split("\n")

                # Remove o nome da lista
                linhas = [linha.strip()
                          for linha in linhas if linha.strip() != get]

                # Junta as linhas em uma string novamente
                conteudo = "\n".join(linhas)

                # Escreve o novo conteúdo no arquivo
                with open(arquivo, "w") as f:
                    f.write(conteudo)

                # Imprime o conteúdo do arquivo
                print(conteudo, "\n")

        # Botão para remover o nome da pessoa
        add_Button = tk.Button(admadd, text="Remover", font=(
            "Arial Black", 9), bg="black", fg="red", cursor="hand2", command=remove)
        add_Button.place(x=150, y=60)

        #  Lista de nomes das pessoas
        pasta = os.path.join(str(Path.home()), "Desktop", "ADM Data 'Face Safety'")
        arquivo = os.path.join(pasta, "AMDs.txt")
        with open(arquivo, "r") as f:
            string = f.read().splitlines()

        # criar um quadro para conter a lista
        frame = tk.Frame(admadd)
        frame.pack(side="left", fill="y")

        # criar uma barra de rolagem vertical
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # conectar a lista à barra de rolagem
        lista = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        for admadd in string:
            lista.insert("end", admadd)
        lista.pack(side="left", fill="y")
        scrollbar.config(command=lista.yview)

        # Inicia a janela
        lista.mainloop()
    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-4'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 4")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nADMRVM '4'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error,
                              text="Houve em: Tira um nome da lista de ADM\nDica: Pode ser que não haja ADMs cadastrados!",
                              font=(
                                  "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# 5 Coloca um nome na lista de ADM

def admadd():
    try:
        # Cria uma janela
        admadd = tk.Tk()

        # Bloqueia o redimensionamento da janela
        admadd.resizable(width=False, height=False)

        # Define o título da janela
        admadd.title("Adicionar ADM: ")

        # Define o tamanho da janela
        admadd.geometry("360x200")

        # Define a cor de fundo da janela
        admadd.configure(background="black")

        # Titulo da janela na aba
        esc_label = tk.Label(admadd, text="Nome que deseja adicionar à ADM:", font=(
            "Arial", 9), bg="black", fg="white")
        esc_label.place(x=145, y=5)

        # Mensagem e avisos
        avs_label = tk.Label(
            admadd, text="Reinicie a aba ao adicionar !", bg="black", fg="red")
        avs_label.place(x=170, y=180)

        # Aviso de "sem banco de dados encontrados"
        avs_label2 = tk.Label(
            admadd, text="0 Cadastros Encontrados", bg="black", fg="red")
        avs_label2.place(y=5)

        # Campo de texto para digitar o nome da pessoa
        esc_entry = tk.Entry(admadd, width=30)
        esc_entry.place(x=150, y=30)

        def add():
            # Pegar o nome da pessoa
            get = esc_entry.get()

            # Verifica se o campo está vazio
            if get == "":
                print("Digite um nome válido!", "\n")
                return

            else:
                # Define o caminho da pasta "Fotos Data 'Face Safety'" na área de trabalho
                pasta = os.path.join(str(Path.home()), "Desktop", "ADM Data 'Face Safety'")

                # Cria a pasta se ela ainda não existir
                if not os.path.exists(pasta):
                    os.makedirs(pasta)

                # Define o caminho completo do arquivo "AMDs.txt" dentro da pasta
                arquivo = os.path.join(pasta, "AMDs.txt")

                # Verifica se o arquivo existe e cria um novo arquivo vazio se ele não existir
                if not os.path.exists(arquivo):
                    with open(arquivo, "w") as f:
                        f.write("")

                # Adiciona o texto com quebra de linha
                if os.path.exists(arquivo) and os.path.getsize(arquivo) > 0:

                    # Lê o conteúdo do arquivo
                    with open(arquivo, "r") as f:
                        conteudo = f.read()

                    # Lê o conteúdo do arquivo
                    with open(arquivo, "r") as f:
                        conteudo = f.read()

                    # Adiciona o texto ao conteúdo
                    conteudo = conteudo + "\n" + get

                    # Escreve o novo conteúdo no arquivo
                    with open(arquivo, "w") as f:
                        f.write(conteudo)

                    # Imprime o conteúdo do arquivo
                    print(conteudo, "\n")

                # Adiciona o texto sem quebra de linha
                else:
                    # Lê o conteúdo do arquivo
                    with open(arquivo, "r") as f:
                        conteudo = f.read()

                    # Adiciona o texto ao conteúdo
                    conteudo = conteudo + get

                    # Escreve o novo conteúdo no arquivo
                    with open(arquivo, "w") as f:
                        f.write(conteudo)

                    # Imprime o conteúdo do arquivo
                    print(conteudo, "\n")

        # Botão para adicionar o nome da pessoa
        add_Button = tk.Button(admadd, text="Adicionar", font=(
            "Arial Black", 9), bg="black", fg="green", cursor="hand2", command=add)
        add_Button.place(x=150, y=60)

        #  Lista de nomes das pessoas
        desktop_path = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop')
        folder_path = os.path.join(desktop_path, "Fotos Data 'Face Safety'")
        files = os.listdir(folder_path)
        string = ', '.join(files)
        print("Nomes encontrados:\n", string, "\n")
        string = string.split(".jpg")
        for i in range(len(string)):
            string[i] = string[i].replace(", ", "")

        # criar um quadro para conter a lista
        frame = tk.Frame(admadd)
        frame.pack(side="left", fill="y")

        # criar uma barra de rolagem vertical
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # conectar a lista à barra de rolagem
        lista = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        for admadd in string:
            lista.insert("end", admadd)
        lista.pack(side="left", fill="y")
        scrollbar.config(command=lista.yview)

        # Inicia a janela
        lista.mainloop()
    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-5'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 5")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nADMADD '5'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error,
                              text="Erro em: Colocar um nome na lista de ADM\nDica: Pode ser que não haja pessoas cadastradas!",
                              font=(
                                  "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# 6 Função que apaga a imagem da pessoa

def apagar_imagem():
    try:
        # Cria uma janela
        apgrt = tk.Tk()

        # Bloqueia o redimensionamento da janela
        apgrt.resizable(width=False, height=False)

        # Define o título da janela
        apgrt.title("Apagar Pessoa: ")

        # Define o tamanho da janela
        apgrt.geometry("360x200")

        # Define a cor de fundo da janela
        apgrt.configure(background="black")

        # Apagar a imagem selecionada
        esc_label = tk.Label(apgrt, text="Escreva o nome que deseja apagar:", font=(
            "Arial", 9), bg="black", fg="white")
        esc_label.place(x=145, y=5)

        def apagar():
            namep = esc_entry.get()
            name = namep + ".jpg"
            desktop_path = os.path.join(os.path.join(
                os.environ['USERPROFILE']), 'Desktop')
            folder_path = os.path.join(desktop_path, "Fotos Data 'Face Safety'")
            files = os.listdir(folder_path)
            for i in range(len(files)):
                if files[i] == name:
                    os.remove(folder_path + "\\" + name)
                    break

        # Mensagem e avisos
        avs_label = tk.Label(
            apgrt, text="Reinicie a aba para atualizar a lista", bg="black", fg="red")
        avs_label.place(x=160, y=180)

        # Campo de texto para digitar o nome da pessoa
        esc_entry = tk.Entry(apgrt, width=30)
        esc_entry.place(x=150, y=30)

        # Seleciona a imagem da pessoa
        esc_Button = tk.Button(apgrt, text="Apagar", font=(
            "Arial Black", 9), bg="black", fg="red", cursor="hand2", command=apagar)
        esc_Button.place(x=150, y=60)

        #  Lista de nomes das pessoas
        desktop_path = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop')
        folder_path = os.path.join(desktop_path, "Fotos Data 'Face Safety'")
        files = os.listdir(folder_path)
        string = ', '.join(files)
        print(string, "\n")
        string = string.split(".jpg")
        for i in range(len(string)):
            string[i] = string[i].replace(", ", "")

        # criar um quadro para conter a lista
        frame = tk.Frame(apgrt)
        frame.pack(side="left", fill="y")

        # criar uma barra de rolagem vertical
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # conectar a lista à barra de rolagem
        lista = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        for apgrt in string:
            lista.insert("end", apgrt)
        lista.pack(side="left", fill="y")
        scrollbar.config(command=lista.yview)
    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-6'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 6")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nApagar Imagem'6'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error,
                              text="Erro em: Apagar a imagem da pessoa\nDica: Pode ser que não haja pessoas cadastradas!",
                              font=(
                                  "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# 7 Função que reconhece a pessoa
def reconhecer():
    try:
        # Obtém o caminho para a área de trabalho do usuário atual
        desktop_path = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop')

        # Concatena o caminho da pasta "Fotos Data 'Face Safety'" na área de trabalho
        data_folder_path = os.path.join(desktop_path, "Fotos Data 'Face Safety'")

        # Cria um objeto PastaOrganizador
        sfr = PastaOrganizador()

        # Carrega as imagens codificadas de faces conhecidas
        sfr.load_encoding_images(data_folder_path)

        # Resto do código é igual ao anterior
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Detecta as faces e as compara com as faces conhecidas
        while True:
            ret, frame = cap.read()
            face_locations, face_names = sfr.detect_known_faces(frame)

            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                cv2.putText(frame, name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

            cv2.imshow("Aperte 'ESC' para sair do modo Scanner", frame)

            # Pressione 'ESC' para sair do modo Scanner
            key = cv2.waitKey(1)

            if key == 27:
                break

        # Fecha a janela
        cap.release()
        cv2.destroyAllWindows()
    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-7'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 7")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nReconhecer '7'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error,
                              text="Erro em: Reconhece a pessoa\nDica: Veja se há cadastros/alguma foto desfocada!",
                              font=(
                                  "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# 8 Função que reconhece a pessoa dentro de uma pasta

class PastaOrganizador:
    try:
        # Método __init__ é definido, que inicializa os atributos da classe
        def __init__(self):

            # Cria duas listas vazias para armazenar os codificações faciais conhecidas e os nomes correspondentes
            self.known_face_encodings = []
            self.known_face_names = []

            # Define o atributo frame_resizing com o valor de 0.25
            self.frame_resizing = 0.25

        # Define o método load_encoding_images, que recebe o caminho para a pasta com as imagens
        def load_encoding_images(self, images_path):

            # Usa a biblioteca glob para encontrar todas as imagens na pasta e armazená-las em uma lista
            images_path = glob.glob(os.path.join(images_path, "*.*"))

            # Imprime o número de imagens encontradas
            print("{} imagens foram encontradas.".format(len(images_path)), "\n")

            # Loop pelas imagens encontradas
            for img_path in images_path:
                # Lê a imagem usando a biblioteca cv2
                img = cv2.imread(img_path)

                # Converte a imagem de BGR para RGB
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Usa a biblioteca face_recognition para extrair as codificações faciais da imagemm
                img_encoding = face_recognition.face_encodings(rgb_img)[0]

                # Extrai o nome do arquivo da imagem e armazena-o na lista de nomes conhecidos
                basename = os.path.basename(img_path)
                (filename, ext) = os.path.splitext(basename)
                self.known_face_names.append(filename)

                # Armazena a codificação facial correspondente na lista de codificações conhecidas
                self.known_face_encodings.append(img_encoding)

            # Imprime os nomes das imagens encontradas
            print("Image's encontrda's: ", self.known_face_names, "\n")

        # Define o método detect_known_faces, que recebe um quadro de imagem como entrada
        def detect_known_faces(self, frame):

            # Redimensiona o quadro de imagem para um quarto do tamanho original
            small_frame = cv2.resize(
                frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)

            # Converte o quadro de imagem de BGR para RGB
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Usa a biblioteca face_recognition para localizar as faces no quadro de imagem redimensionado
            face_locations = face_recognition.face_locations(rgb_small_frame)

            # Extrai as codificações faciais correspondentes às faces encontradas
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)

            # Cria uma lista vazia para armazenar os nomes das faces correspondentes
            face_names = []

            # Loop pelas codificações faciais encontradas
            for face_encoding in face_encodings:

                # Compara as codificações faciais com as codificações faciais conhecidas e retorna uma lista de booleanos
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding)

                # padrão, só alterá-lo se houver uma correspondência
                name = "NoRegistered"

                # Se houver uma correspondência, encontra o índice da codificação facial correspondente com a menor distância
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                # Se a correspondência for encontrada, atribui o nome correspondente à face
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    # função adicionada para salvar no log por prof Filipe
                    # Get the current date and time
                    data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Replace 'id_da_pessoa' and 'id_do_controlador' with the actual IDs
                    id_da_pessoa = 'your_actual_id_da_pessoa'
                    id_do_controlador = 'your_actual_id_do_controlador'
                    print('dados logs')
                    print(data_atual)
                    print(name)
                    insert_into_log(data_atual, 'id_da_pessoa', 'id_do_controlador')

                # Adiciona o nome da face à lista de nomes de faces
                face_names.append(name)

                def loopvf():
                    try:
                        pasta = os.path.join(str(Path.home()), "Desktop",
                                             "ADM Data 'Face Safety'")

                        if not os.path.exists(pasta):
                            os.makedirs(pasta)

                        arquivo = os.path.join(pasta, "AMDs.txt")

                        with open(arquivo, "r") as f:
                            conteudo = f.read()

                        if name in conteudo:
                            key()
                    except:
                        pass

                loopvf()

            # Converte as localizações das faces em um array numpy e divide pelo valor de redimensionamento
            face_locations = np.array(face_locations)
            face_locations = face_locations / self.frame_resizing

            # Converte as localizações das faces em inteiros e retorna tanto as localizações quanto os nomes das faces
            return face_locations.astype(int), face_names
    except:
        pass


# ___________________________________________________________________________
# 9 Função que libera ou tranca o acesso, "Personalize ela como quiser"
# Caso não saiba o que está fazendo, não altere nada fora da função "key()"

def key():
    # __________________________________________________________________________________________________________________________________________
    # LEIA TUDO PARA ENTENDER O FUNCIONAMENTO DO CÓDIGO
    # Aqui você pode personalizar o que acontece quando o reconhecimento facial encontrar um ADM de frente à câmera
    # Automaticamente, quando o programa reconhecer um ADM, ele chamará a função "key()" em loop!!! Até a pessoa sair de frente à câmera.
    # Por isso, é importante o uso do "time.sleep()" para congelar o programa por alguns segundos, porém não é obrigatório.
    # __________________________________________________________________________________________________________________________________________

    # ________________________________________________________________________________________________________________
    # No primeiro "pass", você pode colocar o código para liberar o acesso.
    # No segundo "pass", você pode colocar o código para encerrar o acesso.
    # Caso seu comando seja apenas um, pode deixar o segundo "pass" sem alteração e modificar apenas o primeiro.
    # Se sua tranca for eletrica e só precisa de um comando para abrir,
    # você pode colocar o código para liberar o acesso no primeiro "pass" e deixar o segundo "pass" sem alteração.
    # Se quiser remover o tempo de espera de 5 segundos, basta remover o "time.sleep(5)" ou colocar um "#" na frente.
    # Para modificar o tempo de espera, basta alterar o valor dentro do "time.sleep()".
    # O tempo de espera é em segundos, sendo assim, ele executará o primeiro "pass" e depois de 5 segundos executará o segundo "pass".
    # Lembrando que 5 segundos é o tempo padrão. Caso queira alterar o tempo de espera, altere o valor dentro do "time.sleep()".
    # Este código é apenas um exemplo. Você pode alterá-lo como quiser. No entanto, caso não saiba o que está fazendo,
    # não altere nada fora da função "key()", pois isso pode causar erros no programa.
    # No máximo, adicione novas bibliotecas para melhor compatibilidade com seu dispositivo, por exemplo, "Raspberry Pi".
    # O texto dentro do "print()" é apenas para informar o que está acontecendo. Você pode alterá-lo ou removê-lo como quiser.
    # ________________________________________________________________________________________________________________

    try:
        print("Acesso permitido por 5 segundos e\nO programa será conjelado nesse meio tempo por segurança")
        # Coloque no lugar de "pass" seu codigo para liberar o acesso "como abrir uma tranca"
        # ___________________________________________________________________________________________________________________________
        pass
        # ___________________________________________________________________________________________________________________________

        time.sleep(5)

        print("Acesso expirado após 5 segundos de liberação")
        # Coloque no lugar de "pass" seu codigo de encerrar o acesso "como fechar uma tranca"
        # ___________________________________________________________________________________________________________________________
        pass
        # ___________________________________________________________________________________________________________________________
    # ___________________________________________________________________________________________________________________________
    # PARTE NAO EDITAVEL DO CODIGO, NAO ALTERE NADA ABAIXO
    # V V V V V V V V V V V V V V V V V V V V V V V V V

    except:
        def close():
            error.destroy()

        print("Ocorreu um erro 'code-9'")
        error = tk.Tk()
        error.resizable(width=False, height=False)
        error.title("Erro 9")
        error.geometry("320x180")
        error.configure(background="red")
        error_label = tk.Label(error, text="Erro em:\nKey'9'", font=(
            "Arial", 30), bg="red", fg="black")
        error_label.pack()
        botao = tk.Button(error, text="OK", font=(
            "Arial Black", 10), bg="red", fg="black", cursor="hand2", command=close)
        botao.place(x=10, y=140)
        dica_label = tk.Label(error, text="Erro em: Função 'Personalize ela como quiser'", font=(
            "Arial", 10), bg="red", fg="black")
        dica_label.place(x=10, y=100)
        error.mainloop()


# ___________________________________________________________________________


lobby()
