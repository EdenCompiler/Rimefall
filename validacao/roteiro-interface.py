"""Exercita a interface nativa em X11 virtual, com dados temporários isolados."""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

pasta = Path(__file__).resolve().parents[1]
ambiente = os.environ.copy()
processo = None
janela = ''
registro = None

def comando(*argumentos):
    return subprocess.check_output(['xdotool', *argumentos], text=True).strip()

def clicar(x, y):
    comando('mousemove', '--window', janela, str(x), str(y))
    comando('click', '1')
    time.sleep(.25)

def capturar(nome):
    subprocess.run(['import', '-window', janela, str(pasta/'validacao'/nome)], check=True)

def colar(texto):
    subprocess.run(['xclip', '-selection', 'clipboard'], input=texto, text=True, check=True)
    comando('keydown', 'ctrl')
    time.sleep(.15)
    comando('key', '--delay', '100', 'v')
    time.sleep(.15)
    comando('keyup', 'ctrl')
    time.sleep(.2)

def iniciar():
    global processo, janela, registro
    registro = open(pasta/'validacao'/'interacao-terminal.log', 'a')
    processo = subprocess.Popen([str(pasta/'distribuicao/rimefall')], env=ambiente, stdout=registro, stderr=subprocess.STDOUT)
    janela = ''
    for tentativa in range(150):
        resultado = subprocess.run(['xdotool', 'search', '--name', 'Rimefall / Posto 07'], capture_output=True, text=True)
        if resultado.returncode == 0:
            janela = resultado.stdout.strip().splitlines()[0]
            break
        if processo.poll() is not None:
            raise RuntimeError('O executável encerrou antes de abrir a janela virtual.')
        time.sleep(.1)
    if not janela:
        raise RuntimeError('Janela virtual não encontrada.')
    comando('windowfocus', janela)
    time.sleep(.8)

def encerrar():
    processo.wait(timeout=15)
    registro.close()
    if processo.returncode:
        raise RuntimeError('Falha no executável durante a interação.')

def conferir(dados, verificacao):
    shutil.copyfile(Path(dados)/'rimefall'/'sessao.sexp', pasta/'validacao'/'nativa-estado.sexp')
    programa = f'''(require :asdf)
(asdf:load-asd (truename "{pasta}/rimefall.asd"))
(asdf:load-system "rimefall/nucleo")
(in-package :rimefall)
(let* ((*pasta-dados* #P"{dados}/rimefall/") (*pasta-configuracao* *pasta-dados*)
        (sessao (carregar-sessao)) (soldado (sessao-soldado sessao)))
  (carregar-configuracao)
  {verificacao}
  (format t "Estado nativo conferido.~%"))
'''
    arquivo = Path(dados)/'conferir.lisp'
    arquivo.write_text(programa)
    subprocess.run(['sbcl', '--script', str(arquivo)], check=True, cwd=pasta)

with tempfile.TemporaryDirectory(prefix='rimefall-interface-') as dados:
    ambiente['XDG_DATA_HOME'] = dados
    ambiente['XDG_CONFIG_HOME'] = dados
    try:
        iniciar()
        capturar('interacao-titulo.png')
        clicar(1000, 461)
        clicar(508, 300)
        clicar(434, 352)
        clicar(940, 527)
        comando('key', '--delay', '100', 'p')
        time.sleep(.2)
        capturar('interacao-configuracoes.png')
        clicar(1000, 658)
        clicar(1000, 340)
        clicar(980, 340)
        colar('Silêncio. A escopeta está perto do abrigo.')
        comando('key', '--delay', '100', 'Escape')
        capturar('interacao-diario.png')
        clicar(1000, 634)
        comando('keydown', 'w')
        time.sleep(1.5)
        comando('keyup', 'w')
        comando('keydown', 'd')
        time.sleep(1.0)
        comando('keyup', 'd')
        comando('key', '--delay', '100', 'e')
        time.sleep(.3)
        comando('key', '--delay', '100', 'r')
        time.sleep(2.0)
        comando('mousedown', '3')
        time.sleep(.4)
        capturar('interacao-campo.png')
        comando('mouseup', '3')
        comando('key', '--delay', '100', 'Escape')
        time.sleep(.3)
        capturar('interacao-pausa.png')
        clicar(220, 640)
        encerrar()
        conferir(dados, '''(assert (eq (soldado-arma soldado) :escopeta))
  (assert (= (soldado-carregador soldado) 2))
  (assert (= (soldado-reserva-escopeta soldado) 6))
  (assert (search "Silêncio" (notas-texto (sessao-notas sessao))))
  (assert (= (getf *configuracao* :visao) 77))
  (assert (= (cdr (assoc :dispositivo (getf *configuracao* :atalhos))) 80))''')
        iniciar()
        clicar(1000, 263)
        capturar('interacao-continuar.png')
        clicar(220, 640)
        encerrar()
        # Reutiliza uma transmissão obtida pelo roteiro gráfico, sem revelar o mapa.
        memoria = pasta/'validacao'/'dados'/'memoria.sexp'
        shutil.copyfile(memoria, Path(dados)/'rimefall'/'sessao.sexp')
        iniciar()
        clicar(1000, 263)
        clicar(200, 537)
        clicar(293, 562)
        clicar(850, 386)
        colar('Madeira no abrigo. Atenção ao ruído.')
        comando('key', '--delay', '100', 'Return')
        time.sleep(.2)
        capturar('interacao-mapa.png')
        clicar(1000, 640)
        clicar(540, 485)
        clicar(1000, 634)
        time.sleep(.2)
        comando('key', '--delay', '100', 'p')
        time.sleep(.25)
        comando('keydown', 'w')
        time.sleep(.6)
        comando('keyup', 'w')
        comando('key', '--delay', '100', 'Escape')
        time.sleep(.25)
        clicar(220, 640)
        encerrar()
        conferir(dados, '''(assert (= (sessao-usados sessao) 2))
  (assert (eq (soldado-preparo soldado) :temporizador))
  (assert (= (length (sessao-dispositivos sessao)) 1))
  (assert (some (lambda (marca) (search "Madeira no abrigo" (second marca))) (sessao-marcas sessao)))''')
        print('Interface nativa aprovada: configurações, remapeamento, diário acentuado, coleta, recarga, mira, gravação, continuação, mapa e dispositivo.')
    finally:
        if processo is not None and processo.poll() is None:
            processo.terminate()
        if registro is not None and not registro.closed:
            registro.close()
