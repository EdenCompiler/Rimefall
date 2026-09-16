"""Constrói o mapa principal da guerra e exporta a malha para Rimefall."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

pasta = Path(__file__).resolve().parent
for objeto in list(bpy.context.scene.objects):
    bpy.data.objects.remove(objeto, do_unlink=True)
for colecao in list(bpy.data.collections):
    if colecao.users == 0 or not colecao.objects:
        bpy.data.collections.remove(colecao)
bpy.context.scene.name = 'Rimefall - mapa principal da guerra'
colecoes = {}
materiais = {}

def material(nome, cor):
    tinta = materiais.get(nome)
    if tinta is None:
        tinta = bpy.data.materials.new(nome)
        tinta.diffuse_color = (*cor, 1)
        materiais[nome] = tinta
    return tinta

neve = material('Neve da frente', (.70, .79, .82))
gelo = material('Rio congelado', (.34, .56, .64))
gelo_claro = material('Gelo exposto', (.56, .72, .76))
terra = material('Terra revolvida', (.23, .25, .24))
madeira = material('Madeira escura', (.22, .16, .12))
concreto = material('Concreto frio', (.27, .32, .34))
metal = material('Metal enferrujado', (.16, .19, .19))
lona_aurora = material('Lona Aurora', (.20, .34, .40))
lona_bruma = material('Lona Bruma', (.34, .29, .31))
branco = material('Tinta de setor', (.82, .87, .86))
verde = material('Pinheiro', (.12, .20, .20))

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
        modificador = objeto.modifiers.new('Quina de neve', 'BEVEL')
        modificador.width = chanfro
        modificador.segments = 1
        bpy.ops.object.modifier_apply(modifier=modificador.name)
    return objeto

def haste(grupo, nome, inicio, fim, raio, tinta, ponta=None):
    primeiro, segundo = ponto(*inicio), ponto(*fim)
    direcao = segundo - primeiro
    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=raio,
                                    radius2=raio if ponta is None else ponta,
                                    depth=direcao.length, location=(primeiro+segundo)/2)
    objeto = bpy.context.object
    objeto.rotation_euler = direcao.to_track_quat('Z', 'Y').to_euler()
    return guardar(objeto, grupo, nome, tinta)

def volume(grupo, nome, centro, escala, tinta):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=ponto(*centro))
    objeto = bpy.context.object
    objeto.scale = (escala[0], escala[2], escala[1])
    return guardar(objeto, grupo, nome, tinta)

def estrada(x, z, largura, comprimento, direcao='z'):
    dimensoes = (largura, .06, comprimento) if direcao == 'z' else (comprimento, .06, largura)
    bloco('estradas', 'Estrada de neve', (x, .015, z), dimensoes, terra)
    for faixa in range(0, int(comprimento/8)):
        deslocamento = -comprimento/2 + faixa*8 + 4
        centro = (x, .055, z+deslocamento) if direcao == 'z' else (x+deslocamento, .055, z)
        tamanho = (.18, .025, 3.2) if direcao == 'z' else (3.2, .025, .18)
        bloco('estradas', 'Marca apagada', centro, tamanho, neve)

def trincheira(x, z, comprimento, direcao='x'):
    """Linha baixa de sacos que serve como cobertura e marco de setor."""
    horizontal = direcao == 'x'
    for camada in range(2):
        for indice in range(int(comprimento/2.0)):
            deslocamento = -comprimento/2 + (indice+.5)*2
            centro = (x+deslocamento, .28+camada*.34, z) if horizontal else (x, .28+camada*.34, z+deslocamento)
            tamanho = (1.8,.30,.62) if horizontal else (.62,.30,1.8)
            bloco('trincheiras', 'Saco de trincheira', centro, tamanho, lona_bruma, .08)
    terra_tamanho = (comprimento+1,.035,2.0) if horizontal else (2.0,.035,comprimento+1)
    bloco('trincheiras', 'Faixa de terra da trincheira', (x,.015,z), terra_tamanho, terra)

def casa(x, z, largura, profundidade, tinta=madeira):
    bloco('aldeia', 'Casa', (x,1.5,z), (largura,3.0,profundidade), tinta, .08)
    bloco('aldeia', 'Telhado de neve', (x,3.15,z), (largura+.35,.32,profundidade+.35), neve, .05)
    bloco('aldeia', 'Porta da casa', (x,1.0,z-profundidade/2-.02), (1.0,2.0,.08), metal)
    for lado in (-1,1):
        bloco('aldeia', 'Janela escura', (x+lado*(largura*.27),1.8,z-profundidade/2-.045), (.55,.5,.04), gelo)

def arvore(x, z, altura):
    haste('floresta', 'Tronco de pinheiro', (x,.0,z), (x,altura*.52,z), .16, madeira, ponta=.11)
    for indice in range(3):
        y = altura*.42 + indice*.55
        volume('floresta', 'Copa de pinheiro', (x,y,z), (1.0-indice*.18, .9, 1.0-indice*.18), verde)

def deposito(x, z, largura, profundidade):
    bloco('industria', 'Galpão', (x,2.0,z), (largura,4.0,profundidade), concreto, .10)
    bloco('industria', 'Telhado do galpão', (x,4.12,z), (largura+.25,.20,profundidade+.25), metal, .04)
    bloco('industria', 'Porta do galpão', (x,1.35,z-profundidade/2-.03), (largura*.45,2.7,.08), metal)

# Terreno de 1 km² e o rio congelado que corta a frente em diagonal.
bloco('mapa-guerra', 'Base de neve de um quilômetro', (0,-.25,0), (1000,.50,1000), neve)
for indice in range(7):
    z = -410 + indice*135
    estrada(0,z,18,118,'z')
estrada(0,0,16,1000,'z')
estrada(-250,0,12,760,'x')
bloco('rio', 'Rio congelado', (205,-.02,0), (52,.08,980), gelo)
for indice in range(26):
    z = -470 + indice*38
    bloco('rio', 'Placa de gelo', (205,.055,z), (45,.035,2.0), gelo_claro)
    bloco('rio', 'Fenda do gelo', (205 + (indice%3-1)*7,.09,z+8), (1.0,.025,13), terra)

# QGs, pontos de reunião e torres de rádio nas extremidades da frente.
for z, tinta, nome in ((-500,lona_aurora,'QG Aurora'), (500,lona_bruma,'QG Bruma')):
    bloco('qgs', nome, (0,2.0,z), (34,4.0,28), tinta, .10)
    bloco('qgs', 'Abrigo do QG', (0,4.15,z), (35,.28,29), neve, .04)
    for lado in (-1,1):
        trincheira(lado*22,z,32,'z')
        haste('qgs', 'Antena de comando', (lado*12,0,z), (lado*12,10,z), .12, metal)
        haste('qgs', 'Travessa da antena', (lado*12,8.5,z), (lado*13.8,8.5,z), .05, metal)
    bloco('qgs', 'Placa do quartel', (0,3.0,z-14), (11,1.5,.08), branco)

# Cinco setores alinhados à frente móvel, correspondentes aos setores da simulação.
setores = [(-240,'Passagem do Rio'),(-120,'Aldeia de Gelo'),(0,'Linha das Trincheiras'),(120,'Pátio Industrial'),(240,'Colina do Farol')]
for indice,(z,nome) in enumerate(setores):
    bloco('setores', 'Marco de setor '+nome, (0,.20,z), (22,.40,.70), branco, .03)
    bloco('setores', 'Placa de setor '+nome, (0,2.1,z-18), (12,3.0,.10), lona_aurora if indice%2==0 else lona_bruma, .02)
    for lado in (-1,1):
        haste('setores', 'Mastro de setor', (lado*10,.20,z-18), (lado*10,5.0,z-18), .045, metal)
        bloco('setores', 'Bandeira de setor', (lado*10,4.5,z-18), (2.0,1.0,.04), lona_aurora if indice%2==0 else lona_bruma)

# Passagem do Rio: pontes, margens escavadas e um posto de controle.
for x in (-18,18):
    trincheira(x,-240,55,'z')
for z in (-275,-205):
    bloco('rio', 'Ponte de madeira', (205,.25,z), (62,.45,10), madeira, .04)
for x in (-25,25):
    bloco('posto-rio', 'Posto de controle', (x,1.4,-240), (5.5,2.8,5), concreto, .06)
    bloco('posto-rio', 'Laje de neve', (x,2.92,-240), (5.8,.18,5.3), neve)

# Aldeia de Gelo: casas, cercas e uma clareira navegável.
for x,z in ((-24,-150),(-5,-110),(21,-145),(35,-95),(-38,-75)):
    casa(x,z,10,8,lona_bruma if x > 10 else madeira)
for indice in range(9):
    x = -42 + indice*10
    haste('aldeia', 'Cerca da aldeia', (x,.0,-167), (x,.9,-167), .09, madeira)
    haste('aldeia', 'Travessa da cerca', (x,.65,-167), (x+10,.65,-167), .06, madeira)

# Linha das Trincheiras: duas linhas paralelas e coberturas intercaladas.
trincheira(-36, -8, 120, 'x')
trincheira(36, 8, 120, 'x')
for x,z in ((-24,22),(0,-22),(24,22),(0,22),(-12,-38),(12,38)):
    bloco('trincheiras', 'Abrigo de trincheira', (x,1.2,z), (8,2.4,4), madeira, .07)
    bloco('trincheiras', 'Neve do abrigo', (x,2.48,z), (8.2,.18,4.2), neve, .03)

# Pátio Industrial: galpões, tanques, guindaste e uma linha de carga.
deposito(-26,95,26,18)
deposito(25,145,30,20)
deposito(-18,155,18,14)
for x in (-44,-30,-16,-2,12,26,40):
    bloco('industria', 'Dormente ferroviário', (x,.08,118), (10,.16,1.1), madeira)
    haste('industria', 'Trilho', (x-5,.22,117.2), (x+5,.22,117.2), .045, metal)
    haste('industria', 'Trilho', (x-5,.22,118.8), (x+5,.22,118.8), .045, metal)
for x in (-42,-20,4,28):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=4.0, depth=6.0, location=ponto(x,3.0,82))
    guardar(bpy.context.object,'industria','Tanque de combustível',metal)
haste('industria','Guindaste', (44,0,90),(44,12,90),.25,metal)
haste('industria','Braço do guindaste',(44,12,90),(10,12,90),.20,metal)

# Colina do Farol: elevação em degraus, torre e mata de cobertura.
for raio, altura in ((78,.6),(58,1.2),(38,2.0),(20,2.8)):
    volume('colina','Platô da colina',(0,altura,240),(raio,altura,raio*.72),neve)
bloco('colina','Base do farol',(0,4.0,240),(8,8,8),concreto, .06)
haste('colina','Torre do farol',(0,4,240),(0,18,240),.38,metal)
volume('colina','Luz do farol',(0,18.5,240),(1.2,1.0,1.2),branco)
for angulo in range(0,360,30):
    arvore(math.cos(math.radians(angulo))*62,240+math.sin(math.radians(angulo))*45,5.0+(angulo%3))

# Floresta de cobertura entre aldeia e indústria, com clareiras para rotas.
for indice in range(95):
    x = -170 + ((indice*37)%310)
    z = -55 + ((indice*53)%230)
    if abs(x) < 48 and -20 < z < 45:
        continue
    arvore(x,z,4.0+(indice%4)*.55)

# Caches e marcos de navegação para as expedições opcionais.
for x,z,tinta in ((-300,-90,lona_aurora),(300,90,lona_bruma),(-260,230,lona_aurora),(260,-230,lona_bruma)):
    bloco('logistica','Cache de campanha',(x,1.0,z),(8,2.0,6),tinta,.08)
    bloco('logistica','Tampa do cache',(x,2.1,z),(8.2,.16,6.2),neve,.04)
    haste('logistica','Baliza do cache',(x+4,0,z),(x+4,4,z),.06,metal)

# Exportação de triângulos com cor por face, igual às outras malhas do jogo.
bpy.context.view_layer.update()
direcao_luz = Vector((-.35,-.5,1)).normalized()
valores = []
for colecao in colecoes.values():
    for objeto in colecao.objects:
        avaliado = objeto.evaluated_get(bpy.context.evaluated_depsgraph_get())
        malha = avaliado.to_mesh()
        malha.calc_loop_triangles()
        matriz = avaliado.matrix_world
        normal_matriz = matriz.to_3x3().inverted().transposed()
        for triangulo in malha.loop_triangles:
            normal = (normal_matriz @ triangulo.normal).normalized()
            intensidade = .62+.38*max(0,normal.dot(direcao_luz))
            cor = objeto.data.materials[triangulo.material_index].diffuse_color
            for indice in triangulo.vertices:
                vertice = matriz @ malha.vertices[indice].co
                valores.extend((vertice.x,vertice.z,-vertice.y,cor[0]*intensidade,cor[1]*intensidade,cor[2]*intensidade,1.0))
        avaliado.to_mesh_clear()

(pasta/'guerra.malha').write_text('; Mapa principal exportado do Blender MCP.\n#(\n' +
                                  ''.join(' '.join(f'{valor:.5f}' for valor in valores[inicio:inicio+7])+'\n'
                                          for inicio in range(0,len(valores),7)) + ')\n')
for nome, colecao in colecoes.items():
    colecao.hide_render = nome != 'mapa-guerra'
    colecao.hide_viewport = nome != 'mapa-guerra'
bpy.ops.wm.save_as_mainfile(filepath=str(pasta/'guerra.blend'))
(pasta/'inventario-guerra.txt').write_text('mapa-guerra: %d triângulos\n' % (len(valores)//21))
print('mapa-guerra: %d triângulos' % (len(valores)//21))
