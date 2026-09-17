"""Executado pelo Blender MCP: cobertura, ruínas e colisões da mesma cena."""
import bpy
from mathutils import Vector
from pathlib import Path

pasta = Path('/home/bruno/projetos/lisp_fps/modelos')
colecao = bpy.data.collections.get('frente-jogavel')
if colecao:
    for objeto in list(colecao.objects):
        bpy.data.objects.remove(objeto, do_unlink=True)
else:
    colecao = bpy.data.collections.new('frente-jogavel')
    bpy.context.scene.collection.children.link(colecao)

def bloco(nome, centro, dimensoes, cor):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(centro[0], -centro[2], centro[1]))
    objeto = bpy.context.object
    objeto.name = nome
    objeto.scale = (dimensoes[0], dimensoes[2], dimensoes[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for grupo in list(objeto.users_collection):
        grupo.objects.unlink(objeto)
    colecao.objects.link(objeto)
    tinta = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    tinta.diffuse_color = (*cor, 1)
    objeto.data.materials.append(tinta)
    return objeto

# Coberturas com corredores laterais: a estrada não fica bloqueada por paredes.
for lado in (-1, 1):
    for indice in range(5):
        z = lado * (30 + indice * 22)
        x = (-1 if indice % 2 else 1) * (12 + indice * 3)
        for camada in range(3):
            for saco in range(5):
                bloco('Cobertura de sacos', (x+saco*1.1, .16+camada*.30, z),
                      (1.04,.28,.7), (.34,.40,.40))
        bloco('Neve sobre cobertura', (x+2.2,.95,z), (5.5,.09,.8), (.76,.85,.87))
    for x in (-32, 32):
        bloco('Ruína de concreto', (x,1.6,lado*64), (1.0,3.2,10), (.30,.35,.36))
        bloco('Ruína de concreto', (x+3,1.0,lado*69), (6,2,1), (.30,.35,.36))
        bloco('Entulho', (x+5,.35,lado*62), (2.4,.7,2.0), (.41,.45,.44))
    bloco('Caixa de munição da frente', (-10,.55,lado*55), (1.8,1.1,1.0), (.30,.37,.29))
    bloco('Tampa de munição', (-10,1.14,lado*55), (1.9,.1,1.1), (.72,.80,.82))

bpy.context.view_layer.update()
valores = []
colisoes = []
luz = Vector((-.35,-.5,1)).normalized()
for objeto in bpy.context.scene.objects:
    if objeto.type != 'MESH':
        continue
    avaliado = objeto.evaluated_get(bpy.context.evaluated_depsgraph_get())
    malha = avaliado.to_mesh()
    malha.calc_loop_triangles()
    matriz = avaliado.matrix_world
    normal_matriz = matriz.to_3x3().inverted().transposed()
    pontos = [matriz @ vertice.co for vertice in malha.vertices]
    if pontos:
        minimo = [min(v[eixo] for v in pontos) for eixo in range(3)]
        maximo = [max(v[eixo] for v in pontos) for eixo in range(3)]
        if maximo[2] > .3 and minimo[2] < 1.8 and not objeto.name.startswith(('Platô', 'Copa', 'Bandeira')):
            colisoes.append(((minimo[0]+maximo[0])/2, -(minimo[1]+maximo[1])/2,
                             maximo[0]-minimo[0], maximo[1]-minimo[1], maximo[2]))
    for triangulo in malha.loop_triangles:
        normal = (normal_matriz @ triangulo.normal).normalized()
        intensidade = .62 + .38 * max(0, normal.dot(luz))
        cor = objeto.data.materials[triangulo.material_index].diffuse_color
        for indice in triangulo.vertices:
            vertice = matriz @ malha.vertices[indice].co
            valores.extend((vertice.x,vertice.z,-vertice.y,cor[0]*intensidade,cor[1]*intensidade,cor[2]*intensidade,1))
    avaliado.to_mesh_clear()
(pasta/'guerra.malha').write_text('; Frente exportada pelo Blender MCP.\n#(\n' +
    ''.join(' '.join(f'{v:.5f}' for v in valores[i:i+7])+'\n' for i in range(0,len(valores),7)) + ')\n')
(pasta.parent/'colisoes-guerra.lisp').write_text('(in-package #:rimefall)\n;;; Volumes extraídos da cena pelo Blender MCP; não editar manualmente.\n(defparameter *volumes-guerra*\n  \'(' +
    '\n    '.join('('+' '.join(f'{v:.5f}' for v in caixa)+')' for caixa in colisoes)+'))\n')
for grupo in bpy.data.collections:
    grupo.hide_viewport = False
    grupo.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=str(pasta/'guerra.blend'))
print('Frente:',len(valores)//21,'triângulos;',len(colisoes),'volumes sólidos.')
