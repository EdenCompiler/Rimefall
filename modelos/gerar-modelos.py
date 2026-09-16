"""Cria os modelos autorais de Rimefall no Blender e exporta triângulos coloridos."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

pasta = Path(__file__).resolve().parent
# Trabalha numa cena própria, sem depender de arquivos externos.
# Este gerador reconstrói exclusivamente o arquivo autoral do jogo.
for objeto in list(bpy.context.scene.objects):
    bpy.data.objects.remove(objeto, do_unlink=True)
for colecao in list(bpy.data.collections):
    if colecao.users == 0 or not colecao.objects:
        bpy.data.collections.remove(colecao)
bpy.context.scene.name = 'Rimefall - expansão MCP'
colecoes = {}
materiais = {}

def material(nome, cor):
    if nome not in materiais:
        tinta = bpy.data.materials.new(nome)
        tinta.diffuse_color = (*cor, 1)
        materiais[nome] = tinta
    return materiais[nome]

neve = material('Neve compactada', (.72, .80, .82))
concreto = material('Concreto azulado', (.25, .32, .35))
lona = material('Lona militar', (.29, .34, .32))
madeira = material('Madeira envelhecida', (.24, .17, .12))
metal = material('Aço fosco', (.12, .16, .18))
metal_claro = material('Aço exposto', (.29, .33, .34))
pele = material('Pele de carvão', (.11, .15, .17))
osso = material('Carapaça congelada', (.57, .65, .65))
boca = material('Fenda bucal', (.22, .07, .07))
ambar = material('Sinalização âmbar', (.72, .48, .17))

# Coordenadas do jogo: altura no eixo Y; no Blender, altura no eixo Z.
def ponto(x, y, z):
    return Vector((x, -z, y))

def guardar(objeto, grupo, nome, tinta):
    objeto.name = nome
    objeto.data.materials.append(tinta)
    if grupo not in colecoes:
        colecao = bpy.data.collections.new(grupo)
        bpy.context.scene.collection.children.link(colecao)
        colecoes[grupo] = colecao
    for colecao in list(objeto.users_collection):
        colecao.objects.unlink(objeto)
    colecoes[grupo].objects.link(objeto)
    return objeto

def bloco(grupo, nome, centro, tamanho, tinta, chanfro=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=ponto(*centro))
    objeto = bpy.context.object
    objeto.scale = (tamanho[0], tamanho[2], tamanho[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    guardar(objeto, grupo, nome, tinta)
    if chanfro:
        modificador = objeto.modifiers.new('Quinas gastas', 'BEVEL')
        modificador.width = chanfro
        modificador.segments = 1
        bpy.ops.object.modifier_apply(modifier=modificador.name)
    return objeto

def haste(grupo, nome, inicio, fim, raio, tinta, ponta=None):
    primeiro, segundo = ponto(*inicio), ponto(*fim)
    direcao = segundo - primeiro
    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=raio,
        radius2=raio if ponta is None else ponta, depth=direcao.length,
        location=(primeiro+segundo)/2)
    objeto = bpy.context.object
    objeto.rotation_euler = direcao.to_track_quat('Z', 'Y').to_euler()
    return guardar(objeto, grupo, nome, tinta)

def volume(grupo, nome, centro, escala, tinta):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=ponto(*centro))
    objeto = bpy.context.object
    objeto.scale = (escala[0], escala[2], escala[1])
    return guardar(objeto, grupo, nome, tinta)

# Abrigo aberto, paredes de sacos e depósitos coincidem com os volumes da simulação.
registros = [linha.split() for linha in (pasta.parent/'mapas'/'posto.dat').read_text().splitlines()
             if linha.strip() and not linha.startswith(';')]
paredes = [tuple(map(float, registro[1:6])) + (registro[6],) for registro in registros if registro[0] == 'parede']
bloco('posto', 'Chão de neve', (0,-.18,0), (160,.35,160), neve)
for indice, (x,z,largura,profundidade,altura,tipo) in enumerate(paredes):
    tinta = lona if tipo == 'sacos' else madeira if tipo == 'caixa' else concreto
    bloco('posto', f'{tipo} {indice}', (x,altura/2,z), (largura,altura,profundidade), tinta, .07)
    bloco('posto', f'Neve sobre {indice}', (x,altura+.025,z), (largura+.06,.12,profundidade+.06), neve, .04)
    if tipo == 'sacos':
        # Relevos baixos mantêm o contorno físico previsível.
        horizontal = largura > profundidade
        comprimento = largura if horizontal else profundidade
        quantidade = int(comprimento/1.15)
        for camada in range(3):
            for saco in range(quantidade):
                deslocamento = -comprimento/2 + (saco+.5)*comprimento/quantidade
                centro = (x+deslocamento if horizontal else x, .22+camada*.39, z if horizontal else z+deslocamento)
                dimensoes = (comprimento/quantidade-.05,.35,profundidade+.015) if horizontal else (largura+.015,.35,comprimento/quantidade-.05)
                bloco('posto', 'Saco de contenção', centro, dimensoes, lona, .1)
    if tipo in ('caixa','deposito'):
        for faixa in (-.32,.32):
            bloco('posto', 'Cinta de aço', (x+largura*faixa,altura/2,z), (.12,altura+.015,profundidade+.025), metal)
    if tipo == 'deposito':
        bloco('posto','Porta lacrada',(x,1.15,z+profundidade/2+.015),(1.45,2.3,.06),metal)
        bloco('posto','Placa de advertência',(x+1.8,1.7,z+profundidade/2+.04),(.45,.45,.04),ambar)
# Estrado do abrigo e corrimãos discretos.
for tabua in range(12):
    bloco('posto','Estrado',(0,.015,18.8+tabua*.62),(8.8,.055,.57),madeira)
for lado in (-1,1):
    haste('posto','Antena',(lado*4.2,0,26),(lado*4.2,7,26),.045,metal)
    haste('posto','Travessa da antena',(lado*4.2-1,6.7,26),(lado*4.2+1,6.7,26),.025,metal)
# Montanhas de silhueta irregular, além do limite jogável.
for indice in range(18):
    angulo = indice*math.tau/18
    volume('posto','Crista distante',(math.sin(angulo)*60,2,math.cos(angulo)*60),(12,9+indice%5,11),neve)

# Predador sem olhos, peito anguloso, crista óssea e braços longos.
volume('criatura','Tórax',(0,1.22,.03),(.60,.68,.36),pele)
volume('criatura','Placa dorsal',(0,1.48,.18),(.54,.48,.27),osso)
volume('criatura','Cabeça cega',(0,1.68,-.24),(.28,.32,.38),osso)
bloco('criatura','Boca vertical',(0,1.48,-.53),(.10,.19,.04),boca)
for lado in (-1,1):
    grupo_braco = 'braco-criatura-esquerdo' if lado < 0 else 'braco-criatura-direito'
    haste(grupo_braco,'Braço',(lado*.46,1.5,0),(lado*.68,.78,-.12),.17,pele,ponta=.12)
    haste(grupo_braco,'Antebraço',(lado*.68,.78,-.12),(lado*.48,.28,-.35),.13,pele,ponta=.075)
    for dedo in range(3):
        haste(grupo_braco,'Garra',(lado*.48+(dedo-1)*.07,.30,-.35),(lado*.48+(dedo-1)*.07,.1,-.53),.025,osso,ponta=.005)
    grupo = 'perna-esquerda' if lado < 0 else 'perna-direita'
    haste(grupo,'Coxa',(lado*.24,.95,.04),(lado*.30,.46,.17),.19,pele,ponta=.14)
    haste(grupo,'Canela',(lado*.30,.46,.17),(lado*.27,.12,-.10),.13,pele,ponta=.09)
    bloco(grupo,'Pé',(lado*.27,.08,-.18),(.23,.15,.45),pele,.05)
for indice in range(5):
    haste('criatura','Crista',(0,1.1+indice*.14,.28),(0,1.2+indice*.16,.55),.11,osso,ponta=0)

# Armas em escala real. Frente no eixo -Z do jogo; mira à altura zero.
for grupo in ('fuzil','escopeta'):
    escopeta = grupo == 'escopeta'
    bloco(grupo,'Coronha',(0,-.23,.24),(.105,.19,.48),madeira,.045)
    bloco(grupo,'Chapa da coronha',(0,-.23,.49),(.11,.20,.025),metal,.01)
    haste(grupo,'Pescoço da coronha',(0,-.12,-.01),(0,-.23,.18),.05,madeira)
    bloco(grupo,'Caixa da culatra',(0,-.07,-.12),(.11,.10,.27),metal,.014)
    bloco(grupo,'Guarda-mão',(0,-.12,-.38),(.12,.11,.34),madeira,.025)
    haste(grupo,'Cano',(0,-.055,-.20),(0,-.055,-.90 if not escopeta else -.78),.027 if not escopeta else .038,metal)
    haste(grupo,'Boca do cano',(0,-.055,-.89 if not escopeta else -.77),(0,-.055,-.925 if not escopeta else -.81),.030 if not escopeta else .041,metal_claro)
    if escopeta:
        haste(grupo,'Tubo de munição',(0,-.12,-.25),(0,-.12,-.70),.028,metal)
        bloco('telha','Telha móvel',(0,-.14,-.43),(.14,.12,.20),madeira,.025)
    else:
        haste('ferrolho','Ferrolho',(0,-.045,-.11),(.13,-.035,-.10),.014,metal_claro)
        volume('ferrolho','Manopla do ferrolho',(.13,-.035,-.10),(.025,.025,.025),metal)
    # Alça em U e massa fina: a abertura, não um marcador de tela, define a mira.
    for lado in (-1,1):
        bloco(grupo,'Alça de mira',(lado*.025,-.005,-.19),(.015,.04,.024),metal)
    bloco(grupo,'Massa de mira',(0,-.001,-.76),(.009,.035,.018),metal)
    haste(grupo,'Gatilho',(0,-.12,.03),(0,-.18,.02),.008,metal)
    bloco(grupo,'Arco do guarda-mato',(0,-.19,.02),(.028,.018,.12),metal)

# Carabina e submetralhadora: silhuetas e culatras independentes.
for grupo in ('carabina','submetralhadora'):
    curta = grupo == 'submetralhadora'
    bloco(grupo,'Coronha de madeira',(0,-.23,.24),(.105,.19,.43),madeira,.025)
    bloco(grupo,'Culatra fixa',(0,-.07,-.10),(.11,.12,.30),metal,.015)
    bloco(grupo,'Empunhadura',(0,-.21,.04),(.095,.20,.10),madeira,.025)
    comprimento = -.64 if curta else -.87
    haste(grupo,'Cano refrigerado',(0,-.06,-.23),(0,-.06,comprimento),.033 if curta else .025,metal)
    bloco(grupo,'Guarda-mão frontal',(0,-.13,-.36),(.13,.12,.25),madeira,.025)
    if curta:
        for anel in range(5):
            haste(grupo,'Aleta de refrigeração',(0,-.06,-.40-anel*.036),(0,-.06,-.415-anel*.036),.042,metal_claro)
        bloco('carregador-submetralhadora','Carregador destacável',(0,-.30,-.17),(.07,.34,.13),metal,.01)
    else:
        bloco(grupo,'Depósito interno',(0,-.15,-.12),(.09,.1,.16),metal)
        haste(grupo,'Tubo de gases',(0,-.105,-.40),(0,-.105,-.77),.014,metal)
    grupo_culatra = 'culatra-submetralhadora' if curta else 'culatra'
    bloco(grupo_culatra,'Janela da culatra',(0,-.005,-.10),(.055,.025,.13),metal_claro)
    haste(grupo_culatra,'Alavanca de manejo',(.04,-.045,-.1),(.13,-.045,-.1),.013,metal)
    for lado in (-1,1):
        bloco(grupo,'Alça em U',(lado*.025,-.005,-.19),(.015,.04,.024),metal)
    bloco(grupo,'Massa frontal',(0,-.001,comprimento+.08),(.009,.035,.018),metal)
    haste(grupo,'Gatilho',(0,-.14,.02),(0,-.19,.01),.008,metal)
    bloco(grupo,'Guarda-mato',(0,-.20,.02),(.027,.015,.11),metal)
latão = material('Latão de cartucho',(.64,.43,.17))
haste('cartucho','Estojo de latão',(0,0,-.035),(0,0,.035),.012,latão)
haste('cartucho','Ponta do projétil',(0,0,-.035),(0,0,-.055),.012,metal_claro,ponta=.003)

# Caixa de suprimentos e braços do soldado são modelos independentes.
bloco('suprimento','Caixa de transporte',(0,.18,0),(.72,.36,.44),lona,.035)
for lado in (-1,1):
    bloco('suprimento','Cinta de transporte',(lado*.22,.18,0),(.055,.38,.46),metal)
bloco('suprimento','Etiqueta',(0,.20,.226),(.21,.10,.012),ambar)
for lado in (-1,1):
    grupo_braco = 'braco-esquerdo' if lado < 0 else 'braco-direito'
    haste(grupo_braco,'Manga',(lado*.30,-.46,.2),(lado*.11,-.20,-.18),.10,lona,ponta=.075)
    volume(grupo_braco,'Luva',(lado*.10,-.15,-.23),(.075,.075,.14),metal)

# Adereços finais: neve irregular, corpo, isca e clarão do disparo.
for indice in range(90):
    x = ((indice*13.13)%51)-25.5
    z = ((indice*7.71)%46)-24
    volume('posto','Crosta de neve',(x,.004,z),(.6+(indice%3)*.4,.035,1.3),neve)
for indice in range(32):
    for lado in (-1,1):
        volume('posto','Neve pisada',(lado*.43,.006,16-indice*.85),(.16,.008,.30),concreto)
volume('corpo','Tronco do soldado',(0,.2,0),(.32,.20,.52),lona)
volume('corpo','Capacete',(0,.21,-.64),(.21,.20,.24),lona)
for lado in (-1,1):
    haste('corpo','Perna estendida',(lado*.16,.15,.3),(lado*.23,.12,1.03),.115,lona)
    haste('corpo','Braço caído',(lado*.27,.17,-.3),(lado*.43,.12,.27),.085,lona)
    bloco('corpo','Bota',(lado*.23,.12,1.07),(.20,.22,.3),metal,.04)
volume('isca','Pedra para distração',(0,0,0),(.07,.06,.08),concreto)
fogo = material('Clarão âmbar',(1.0,.68,.18))
for indice in range(4):
    angulo = indice*math.tau/4
    haste('clarao','Língua de fogo',(0,-.055,-.91),(math.sin(angulo)*.09,-.055+math.cos(angulo)*.09,-1.1),.035,fogo,ponta=0)

# Superfícies compartilhadas com a simulação: a cor informa o risco sonoro.
gelo = material('Gelo translúcido fosco', (.36,.59,.65))
for registro in registros:
    if registro[0] == 'superficie':
        x,z,largura,profundidade = map(float,registro[1:5])
        tipo = registro[5]
        if tipo == 'madeira' and z == 22:
            continue  # O estrado existente já ocupa essa região.
        bloco('posto','Piso '+tipo,(x,.035,z),(largura,.06,profundidade),metal_claro if tipo == 'metal' else madeira if tipo == 'madeira' else gelo)
        for faixa in range(7):
            deslocamento = (faixa-3)*largura/8
            haste('posto','Ranhura do piso',(x+deslocamento,.074,z-profundidade*.46),
                  (x+deslocamento+.15,.074,z+profundidade*.46),.012,metal if tipo == 'metal' else concreto)
    if registro[0] == 'porta':
        x,z,largura,profundidade,altura = map(float,registro[1:])
        bloco('porta','Portão de chapa',(0,altura/2,0),(largura,altura,profundidade),metal,.03)
        for lado in (-1,1):
            bloco('posto','Guia do portão',(x+lado*(largura/2+.15),2.2,z),(.2,4.4,.35),concreto)
            bloco('porta','Faixa de advertência',(lado*1.8,1,profundidade/2+.012),(.12,1.7,.02),ambar)
        bloco('posto','Travessa do portão',(x,4.3,z),(largura+.5,.2,.35),metal)
    if registro[0] == 'suprimento' and registro[-1] != 'nenhum':
        x,z = map(float,registro[1:3])
        haste('posto','Baliza de expedição',(x+1,0,z),(x+1,2,z),.04,metal)
        bloco('posto','Placa de equipamento',(x+1,1.7,z),(.6,.4,.07),ambar)
# Chamador: mesmo corpo cego, garganta expandida e hastes acústicas abertas.
for objeto in list(colecoes['criatura'].objects):
    copia = objeto.copy()
    copia.data = objeto.data.copy()
    bpy.context.scene.collection.objects.link(copia)
    guardar(copia,'chamador','Chamador '+objeto.name,objeto.data.materials[0])
volume('chamador','Saco de ressonância',(0,1.45,-.52),(.34,.40,.29),boca)
for lado in (-1,1):
    haste('chamador','Haste acústica',(lado*.18,1.8,-.2),(lado*.58,2.3,-.18),.12,osso,ponta=.025)
# Equipamento experimental em escala real.
bloco('temporizador','Caixa do temporizador',(0,.12,0),(.28,.24,.22),lona,.025)
bloco('temporizador','Mostrador',(0,.19,.115),(.13,.06,.01),ambar)
haste('temporizador','Antena de acionamento',(.09,.23,0),(.09,.55,0),.008,metal)
for lado in (-1,1):
    haste('bipe','Perna do bipé',(0,.5,0),(lado*.23,0,.07),.018,metal)
    bloco('bipe','Sapata',(lado*.23,.02,.07),(.10,.035,.12),metal)
bloco('bipe','Abraçadeira',(0,.51,0),(.14,.06,.12),metal_claro)

# Fuzis com lunetas: ampliação óptica implementada pela câmera do jogo.
for grupo in ('precisao','franco-atirador'):
    longo = grupo == 'franco-atirador'
    bloco(grupo,'Coronha de precisão',(0,-.23,.25),(.12,.21,.48),madeira,.03)
    bloco(grupo,'Apoio da face',(0,-.14,.25),(.12,.065,.23),lona,.01)
    bloco(grupo,'Caixa reforçada',(0,-.07,-.1),(.12,.13,.33),metal,.015)
    bloco(grupo,'Guarda-mão longo',(0,-.13,-.44),(.13,.12,.44),madeira,.025)
    haste(grupo,'Cano pesado',(0,-.055,-.22),(0,-.055,-1.11 if longo else -.95),.032,metal)
    haste(grupo,'Freio de boca',(0,-.055,-1.09 if longo else -.93),
          (0,-.055,-1.14 if longo else -.98),.041,metal_claro)
    bloco(grupo,'Base da luneta',(0,.025,-.13),(.10,.05,.26),metal)
    haste(grupo,'Tubo óptico',(0,.10,.04),(0,.10,-.32),.044,metal)
    haste(grupo,'Objetiva',(0,.10,-.27),(0,.10,-.40),.065 if longo else .055,metal)
    haste(grupo,'Ocular',(0,.10,.04),(0,.10,.095),.052,metal)
    haste(grupo,'Vidro da ocular',(0,.10,.095),(0,.10,.1),.042,concreto)
    bloco(grupo,'Torre de ajuste',(0,.16,-.12),(.065,.07,.07),metal_claro,.006)
    bloco(grupo,'Guarda-mato',(0,-.20,.02),(.035,.018,.13),metal)
    haste(grupo,'Gatilho',(0,-.14,.01),(0,-.20,.01),.008,metal)
    grupo_culatra = 'ferrolho-longo' if longo else 'culatra-precisao'
    bloco(grupo_culatra,'Ferrolho exposto',(0,-.005,-.08),(.07,.04,.20),metal_claro)
    haste(grupo_culatra,'Alavanca lateral',(.03,-.035,-.04),(.16,-.035,-.02),.015,metal)
    volume(grupo_culatra,'Manopla lateral',(.16,-.035,-.02),(.023,.023,.023),metal)

# Assets da guerra: duas identidades visuais e peças próprias para cada função.
aurora = material('Azul Aurora', (.22,.38,.48))
bruma = material('Cinza Bruma', (.33,.28,.30))
insignia_aurora = material('Insígnia Aurora', (.72,.82,.85))
insignia_bruma = material('Insígnia Bruma', (.64,.40,.35))

def animar_membro(objeto, eixo=0):
    # A simulação usa movimento procedural; estes quadros preservam uma prévia editável no Blender.
    objeto.rotation_mode = 'XYZ'
    objeto.rotation_euler[eixo] = -.18
    objeto.keyframe_insert(data_path='rotation_euler', frame=1)
    objeto.rotation_euler[eixo] = .18
    objeto.keyframe_insert(data_path='rotation_euler', frame=12)
    objeto.rotation_euler[eixo] = -.18
    objeto.keyframe_insert(data_path='rotation_euler', frame=24)

def soldado_guerra(grupo, tinta, emblema, funcao):
    volume(grupo,'Capacete',(0,1.78,0),(.28,.25,.25),tinta)
    volume(grupo,'Cabeça',(0,1.55,0),(.22,.25,.20),pele)
    bloco(grupo,'Colete',(0,1.05,0),(.52,.72,.30),tinta,.06)
    bloco(grupo,'Placa de identificação',(0,1.14,-.17),(.20,.13,.025),emblema,.01)
    esquerdo = haste(grupo,'Braço esquerdo',(-.30,1.28,0),(-.42,.73,-.06),.12,tinta,ponta=.08)
    direito = haste(grupo,'Braço direito',(.30,1.28,0),(.42,.73,-.06),.12,tinta,ponta=.08)
    perna_esquerda = haste(grupo,'Perna esquerda',(-.14,.78,0),(-.18,.12,.06),.15,tinta,ponta=.10)
    perna_direita = haste(grupo,'Perna direita',(.14,.78,0),(.18,.12,.06),.15,tinta,ponta=.10)
    bloco(grupo,'Bota esquerda',(-.18,.08,-.10),(.20,.16,.38),metal,.03)
    bloco(grupo,'Bota direita',(.18,.08,-.10),(.20,.16,.38),metal,.03)
    if funcao == 'medico':
        bloco(grupo,'Bolsa médica',(-.42,1.0,.10),(.25,.30,.22),insignia_aurora if emblema == insignia_aurora else insignia_bruma,.03)
        bloco(grupo,'Faixa médica',(0,1.58,.19),(.18,.12,.025),emblema)
    elif funcao == 'suporte':
        bloco(grupo,'Mochila de munição',(0,1.0,.23),(.38,.55,.20),metal,.04)
        bloco(grupo,'Caixa de cartuchos',(.30,.82,.05),(.20,.17,.32),metal,.02)
    elif funcao == 'engenheiro':
        bloco(grupo,'Ferramentas',(-.38,.92,.18),(.22,.45,.16),madeira,.03)
        haste(grupo,'Pá',(.38,.87,.10),(.46,.20,.10),.025,metal)
    elif funcao == 'comandante':
        bloco(grupo,'Rádio de ombro',(.35,1.30,.18),(.17,.28,.10),metal,.02)
        haste(grupo,'Antena',(.35,1.46,.18),(.35,1.86,.18),.012,metal)
    else:
        haste(grupo,'Rifle em mãos',(-.22,1.13,-.08),(.24,.87,-.48),.035,metal)
    for membro in (esquerdo,direito,perna_esquerda,perna_direita):
        animar_membro(membro, 0 if 'Braço' in membro.name else 1)

for prefixo, tinta, emblema in (('aurora',aurora,insignia_aurora),('bruma',bruma,insignia_bruma)):
    for funcao in ('fuzileiro','medico','suporte','engenheiro','comandante'):
        soldado_guerra('soldado-'+prefixo+'-'+funcao, tinta, emblema, funcao)

# Armas e logística do campo de batalha.
bloco('metralhadora','Caixa da metralhadora',(0,-.06,.0),(.16,.15,.38),metal,.02)
bloco('metralhadora','Cano pesado',(0,-.06,-.42),(.08,.08,.55),metal,.015)
bloco('metralhadora','Carregador de fita',(0,-.25,-.04),(.18,.22,.30),lona,.02)
for lado in (-1,1):
    haste('metralhadora','Bipé de metralhadora',(lado*.06,-.14,-.35),(lado*.20,-.55,-.42),.018,metal)
bloco('pistola','Corpo',(0,-.16,-.06),(.10,.20,.25),metal,.02)
bloco('pistola','Empunhadura',(0,-.29,.07),(.09,.30,.12),madeira,.02)
haste('pistola','Cano',(0,-.15,-.20),(0,-.15,-.40),.025,metal)
bloco('morteiro','Placa base',(0,.04,.18),(.68,.10,.48),metal,.04)
haste('morteiro','Tubo',(0,.66,0),(0,.12,0),.11,metal,ponta=.07)
for lado in (-1,1): haste('morteiro','Perna de apoio',(lado*.22,.10,.12),(lado*.38,-.12,.30),.025,metal)
bloco('radio-campo','Rádio',(0,.20,0),(.38,.40,.20),lona,.04)
haste('radio-campo','Antena',(0,.42,0),(0,1.18,0),.018,metal)
bloco('radio-campo','Manivela',(.24,.16,0),(.10,.10,.16),metal)
bloco('caminhao','Carroceria',(0,.75,0),(2.20,1.25,4.50),lona,.10)
bloco('caminhao','Cabine',(0,1.55,1.42),(2.10,1.20,1.42),metal,.09)
bloco('caminhao','Para-brisa',(0,1.72,.69),(1.72,.55,.035),concreto,.01)
for lado in (-1,1):
    for z in (-1.45,1.40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.43, depth=.24, location=ponto(lado*1.12,.43,z), rotation=(0,math.pi/2,0))
        guardar(bpy.context.object,'caminhao','Roda de transporte',metal)
bloco('caminhao','Caixa de suprimentos',(0,1.20,-.85),(1.60,.55,1.35),madeira,.05)

# Novos monstros, com silhuetas distintas para as invasões.
volume('monstro-rastreador','Corpo baixo',(0,.70,0),(.70,.45,1.0),pele)
volume('monstro-rastreador','Cabeça alongada',(0,.88,-.72),(.45,.38,.60),osso)
for lado in (-1,1):
    haste('monstro-rastreador','Membro dianteiro',(lado*.40,.73,-.35),(lado*.85,.28,-.55),.16,pele,ponta=.05)
    haste('monstro-rastreador','Membro traseiro',(lado*.40,.62,.35),(lado*.72,.20,.65),.18,pele,ponta=.06)
for indice in range(5):
    haste('monstro-rastreador','Barbela',(0,.82-.08*indice,-.98),(0,.74-.08*indice,-1.25),.06,osso,ponta=.01)
volume('monstro-couracado','Peito blindado',(0,1.10,0),(.80,.90,.52),osso)
volume('monstro-couracado','Crânio',(0,1.68,-.28),(.42,.40,.43),pele)
for lado in (-1,1):
    haste('monstro-couracado','Braço espesso',(lado*.58,1.30,0),(lado*.92,.48,-.25),.23,pele,ponta=.15)
    haste('monstro-couracado','Perna espessa',(lado*.32,.73,.12),(lado*.40,.12,.38),.24,pele,ponta=.16)
for indice in range(4):
    bloco('monstro-couracado','Placa de gelo',((indice-1.5)*.32,1.26,.48),(.24,.42,.10),osso,.03)
volume('monstro-enxame','Núcleo',(0,1.20,0),(.48,.58,.48),boca)
for indice in range(8):
    angulo = indice*math.tau/8
    haste('monstro-enxame','Tentáculo',(0,1.20,0),(math.cos(angulo)*.95,.62+(.2 if indice%2 else 0),math.sin(angulo)*.95),.06,pele,ponta=.015)

# Exporta a malha avaliada do Blender, triangulada, com iluminação plana por face.
bpy.context.view_layer.update()
direcao_luz = Vector((-.35,-.5,1)).normalized()
resumo = []
for nome, colecao in colecoes.items():
    valores = []
    for objeto in colecao.objects:
        objeto_avaliado = objeto.evaluated_get(bpy.context.evaluated_depsgraph_get())
        malha = objeto_avaliado.to_mesh()
        malha.calc_loop_triangles()
        matriz = objeto_avaliado.matrix_world
        normal_matriz = matriz.to_3x3().inverted().transposed()
        for triangulo in malha.loop_triangles:
            normal = (normal_matriz @ triangulo.normal).normalized()
            intensidade = .62+.38*max(0,normal.dot(direcao_luz))
            cor = objeto.data.materials[triangulo.material_index].diffuse_color
            for indice in triangulo.vertices:
                vertice = matriz @ malha.vertices[indice].co
                valores.extend((vertice.x,vertice.z,-vertice.y,cor[0]*intensidade,cor[1]*intensidade,cor[2]*intensidade,1.0))
        objeto_avaliado.to_mesh_clear()
    with (pasta/(nome+'.malha')).open('w') as arquivo:
        arquivo.write('; Triângulos exportados do Blender: posição e cor.\n#(\n')
        for inicio in range(0,len(valores),7):
            arquivo.write(' '.join(f'{valor:.5f}' for valor in valores[inicio:inicio+7])+'\n')
        arquivo.write(')\n')
    resumo.append(f'{nome}: {len(valores)//21} triângulos')
# As coleções de peças podem ser editadas isoladamente no arquivo fonte.
for nome, colecao in colecoes.items():
    colecao.hide_render = nome != 'posto'
    colecao.hide_viewport = nome != 'posto'
bpy.ops.wm.save_as_mainfile(filepath=str(pasta/'rimefall.blend'))
(pasta/'inventario.txt').write_text('\n'.join(resumo)+'\n')
print('\n'.join(resumo))
