"""Tropas proporcionais e braços de primeira pessoa, criados no Blender MCP.

Metros, pés em Y=0 no jogo, frente em -Z. Executar com __file__ definido.
As propriedades de articulação independem dos nomes e sufixos do Blender.
"""
import bpy
import math
from pathlib import Path
from mathutils import Vector

pasta = Path(__file__).resolve().parent
cena = bpy.data.scenes.get('Soldados de Rimefall') or bpy.data.scenes.new('Soldados de Rimefall')
bpy.context.window.scene = cena
for colecao in list(bpy.data.collections):
    if colecao.name.startswith(('soldado-', 'primeira-pessoa-')):
        for objeto in list(colecao.objects):
            bpy.data.objects.remove(objeto, do_unlink=True)
        bpy.data.collections.remove(colecao)

def ponto(coordenadas):
    x, y, z = coordenadas
    return Vector((x, -z, y))

def tinta(nome, cor):
    material = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    material.diffuse_color = (*cor, 1.0)
    material.use_nodes = True
    superficie = material.node_tree.nodes.get('Principled BSDF')
    superficie.inputs['Base Color'].default_value = (*cor, 1.0)
    superficie.inputs['Roughness'].default_value = .85
    return material

escuro = tinta('Soldados / borracha', (.055, .065, .065))
correia = tinta('Soldados / correias', (.19, .17, .12))
aco = tinta('Soldados / aço', (.24, .28, .28))
vidro = tinta('Soldados / lentes', (.075, .18, .22))
marfim = tinta('Soldados / sinalização', (.83, .84, .73))
ambar = tinta('Soldados / resgate', (.87, .55, .17))
pele = tinta('Soldados / rosto', (.46, .30, .22))

def guardar(objeto, grupo, nome, parte, material):
    objeto.name = nome
    for origem in list(objeto.users_collection):
        origem.objects.unlink(objeto)
    grupo.objects.link(objeto)
    objeto.data.materials.clear()
    objeto.data.materials.append(material)
    objeto['articulacao-rimefall'] = parte
    return objeto

def bloco(grupo, nome, centro, tamanho, parte, material, chanfro=.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=ponto(centro))
    objeto = bpy.context.object
    objeto.scale = (tamanho[0], tamanho[2], tamanho[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if chanfro:
        modificador = objeto.modifiers.new('Costuras e quinas', 'BEVEL')
        modificador.width = min(chanfro, min(tamanho)/3)
        modificador.segments = 1
        bpy.ops.object.modifier_apply(modifier=modificador.name)
    return guardar(objeto, grupo, nome, parte, material)

def perfil(grupo, nome, aneis, parte, material, lados=10):
    """Anéis elípticos formam casaco, pernas, pescoço, rosto e capacete."""
    vertices = []
    for x, y, z, raio_x, raio_z in aneis:
        for indice in range(lados):
            angulo = math.tau*indice/lados
            vertices.append(ponto((x+raio_x*math.cos(angulo),y,z+raio_z*math.sin(angulo))))
    faces = [tuple(reversed(range(lados)))]
    for nivel in range(len(aneis)-1):
        for indice in range(lados):
            seguinte = (indice+1)%lados
            faces.append((nivel*lados+indice,nivel*lados+seguinte,
                          (nivel+1)*lados+seguinte,(nivel+1)*lados+indice))
    faces.append(tuple((len(aneis)-1)*lados+i for i in range(lados)))
    malha = bpy.data.meshes.new(nome)
    malha.from_pydata(vertices, [], [tuple(reversed(face)) for face in faces])
    malha.update()
    objeto = bpy.data.objects.new(nome, malha)
    grupo.objects.link(objeto)
    return guardar(objeto, grupo, nome, parte, material)

def segmento(grupo, nome, inicio, fim, raio_inicio, raio_fim, parte, material):
    primeiro, segundo = ponto(inicio), ponto(fim)
    direcao = segundo-primeiro
    bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=raio_inicio,radius2=raio_fim,
        depth=direcao.length,location=(primeiro+segundo)/2)
    objeto = bpy.context.object
    objeto.rotation_euler = direcao.to_track_quat('Z','Y').to_euler()
    return guardar(objeto, grupo, nome, parte, material)

def grupo_novo(nome):
    grupo = bpy.data.collections.new(nome)
    cena.collection.children.link(grupo)
    grupo['origem-rimefall'] = 'soldados-proporcionais-v2'
    return grupo

for exercito in ('aurora','bruma'):
    aurora = exercito == 'aurora'
    uniforme = tinta('Soldados / '+exercito,(.24,.37,.38) if aurora else (.43,.37,.30))
    tecido = tinta('Soldados / acolchoado '+exercito,(.38,.49,.48) if aurora else (.56,.52,.42))
    for funcao in ('fuzileiro','medico','suporte','engenheiro','comandante'):
        grupo = grupo_novo('soldado-'+exercito+'-'+funcao)
        perfil(grupo,'Casaco térmico',[(0,.78,0,.23,.15),(0,.93,0,.20,.14),
            (0,1.12,0,.21,.145),(0,1.35,0,.25,.16),(0,1.45,0,.23,.13),
            (0,1.50,0,.09,.09)],'tronco',uniforme,12)
        bloco(grupo,'Colete acolchoado',(0,1.23,-.145),(.38,.35,.075),'tronco',tecido,.025)
        bloco(grupo,'Cinto',(0,.97,0),(.44,.055,.32),'tronco',correia)
        bloco(grupo,'Fivela',(0,.97,-.17),(.055,.045,.025),'tronco',aco)
        perfil(grupo,'Gola',[(0,1.46,0,.10,.095),(0,1.55,0,.105,.10)],'tronco',tecido)
        perfil(grupo,'Cabeça',[(0,1.52,-.025,.07,.085),(0,1.59,-.02,.095,.10),
            (0,1.71,0,.105,.105),(0,1.76,0,.075,.08)],'tronco',pele,12)
        bloco(grupo,'Balaclava',(0,1.57,-.09),(.155,.08,.06),'tronco',tecido)
        bloco(grupo,'Nariz',(0,1.645,-.12),(.033,.052,.034),'tronco',pele)
        bloco(grupo,'Armação dos óculos',(0,1.69,-.108),(.208,.066,.04),'tronco',escuro)
        for lado in (-1,1):
            bloco(grupo,'Lente',(lado*.052,1.691,-.133),(.078,.042,.012),'tronco',vidro,.004)
        perfil(grupo,'Capacete',[(0,1.728,0,.139,.15),(0,1.75,0,.14,.145),
            (0,1.81,.012,.102,.11),(0,1.85,.02,.025,.03)],'tronco',uniforme,12)
        bloco(grupo,'Aba do capacete',(0,1.739,-.13),(.245,.02,.10),'tronco',uniforme)
        for lado in (-1,1):
            sufixo = 'esquerda' if lado < 0 else 'direita'
            perna = 'perna-'+sufixo
            x = lado*.13
            perfil(grupo,'Calça '+sufixo,[(x,.16,0,.072,.074),(x,.39,-.005,.081,.085),
                (x,.47,-.025,.083,.092),(x,.68,0,.099,.098),(x,.87,0,.105,.11)],perna,uniforme)
            bloco(grupo,'Joelheira '+sufixo,(x,.445,-.086),(.125,.135,.043),perna,tecido,.018)
            bloco(grupo,'Bota '+sufixo,(x,.10,-.045),(.17,.19,.28),perna,escuro,.03)
            bloco(grupo,'Sola '+sufixo,(x,.019,-.055),(.176,.038,.285),perna,correia,.01)
            braco = 'braco-'+('esquerdo' if lado < 0 else 'direito')
            ombro = (lado*.255,1.42,0)
            cotovelo = (lado*.31,1.12,-.06)
            mao = (.10,1.055,-.28) if lado > 0 else (.055,1.06,-.55)
            segmento(grupo,'Manga superior '+sufixo,ombro,cotovelo,.105,.079,braco,uniforme)
            segmento(grupo,'Antebraço '+sufixo,cotovelo,mao,.080,.055,braco,uniforme)
            bloco(grupo,'Luva '+sufixo,mao,(.095,.087,.115),braco,escuro,.023)
            bloco(grupo,'Bolso frontal',(lado*.115,1.145,-.204),(.10,.14,.062),'tronco',correia)
            segmento(grupo,'Alça da mochila',(lado*.17,1.45,-.14),(lado*.16,1.06,-.18),.018,.018,'tronco',correia)
        bloco(grupo,'Mochila',(0,1.22,.205),(.31,.38,.16),'tronco',correia,.04)
        bloco(grupo,'Tampa da mochila',(0,1.41,.205),(.33,.065,.17),'tronco',tecido)
        segmento(grupo,'Manta enrolada',(-.20,1.49,.18),(.20,1.49,.18),.061,.061,'tronco',tecido)
        bloco(grupo,'Insígnia',(0,1.365,-.19),(.083,.050,.012),'tronco',marfim if aurora else ambar,.002)
        bloco(grupo,'Marca do exército',(0,1.365,-.198),(.025,.025,.009),'tronco',uniforme,.002)
        if funcao == 'medico':
            bloco(grupo,'Bolsa de socorro',(.27,1.04,.07),(.18,.25,.17),'tronco',tecido,.025)
            bloco(grupo,'Sinal de resgate',(.27,1.06,-.022),(.065,.10,.012),'tronco',ambar)
            for x in (-.025,.025):
                bloco(grupo,'Faixa do socorro',(.27+x,1.06,-.03),(.012,.065,.01),'tronco',marfim,.002)
        elif funcao == 'suporte':
            for lado in (-1,1):
                bloco(grupo,'Caixa de munição',(lado*.265,1.04,.045),(.17,.24,.19),'tronco',correia)
                bloco(grupo,'Fecho da caixa',(lado*.265,1.10,-.053),(.05,.045,.013),'tronco',aco)
        elif funcao == 'engenheiro':
            segmento(grupo,'Cabo da pá',(.17,.92,.30),(.17,1.52,.30),.017,.017,'tronco',correia)
            bloco(grupo,'Lâmina da pá',(.17,1.56,.30),(.14,.16,.025),'tronco',aco,.02)
            bloco(grupo,'Bolsa de ferramentas',(-.27,1.03,.05),(.18,.24,.18),'tronco',correia)
        elif funcao == 'comandante':
            bloco(grupo,'Rádio',(0,1.25,.32),(.22,.30,.13),'tronco',escuro)
            segmento(grupo,'Antena',(.075,1.39,.32),(.075,1.79,.32),.006,.004,'tronco',aco)
            bloco(grupo,'Porta-mapas',(.24,1.02,-.02),(.16,.22,.055),'tronco',correia)
        else:
            bloco(grupo,'Cantil',(.27,1.01,.065),(.14,.21,.14),'tronco',aco,.035)
    for lado,nome in ((-1,'esquerdo'),(1,'direito')):
        grupo = grupo_novo('primeira-pessoa-'+exercito+'-'+nome)
        cotovelo = (lado*.32,-.37,.14)
        pulso = (.075,-.16,-.045) if lado > 0 else (-.015,-.17,-.38)
        segmento(grupo,'Manga em primeira pessoa',cotovelo,pulso,.087,.048,'tronco',uniforme)
        segmento(grupo,'Punho acolchoado',tuple(pulso[i]+(cotovelo[i]-pulso[i])*.12 for i in range(3)),
            pulso,.06,.055,'tronco',tecido)
        bloco(grupo,'Luva em primeira pessoa',pulso,(.086,.073,.12),'tronco',escuro,.024)
        bloco(grupo,'Polegar',(pulso[0]+lado*.035,pulso[1]+.027,pulso[2]-.015),
            (.025,.033,.055),'tronco',escuro,.008)

bpy.context.view_layer.update()
cena['soldados-completos-rimefall'] = 'proporcoes-humanas-v2'
cena.unit_settings.system = 'METRIC'
bpy.data.libraries.write(str(pasta/'soldados.blend'), {cena}, fake_user=True)
print('Criados dez soldados de 1,85 m e quatro braços de primeira pessoa.')
