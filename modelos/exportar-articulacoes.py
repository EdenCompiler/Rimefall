"""Exporta partes dos soldados da cena original para animação no jogo."""
import bpy
from pathlib import Path
from mathutils import Vector

pasta = Path('/home/bruno/projetos/lisp_fps/modelos')
luz = Vector((-.35,-.5,1)).normalized()
for grupo in bpy.data.collections:
    if not grupo.name.startswith('soldado-'):
        continue
    partes = {nome: [] for nome in ('tronco','perna-esquerda','perna-direita','braco-esquerdo','braco-direito')}
    for objeto in grupo.objects:
        nome = objeto.name.lower()
        parte = 'tronco'
        if nome.startswith(('perna','bota')):
            parte = 'perna-esquerda' if 'esquerd' in nome else 'perna-direita'
        elif nome.startswith('braço'):
            parte = 'braco-esquerdo' if 'esquerd' in nome else 'braco-direito'
        elif nome.startswith('rifle'):
            continue
        avaliado = objeto.evaluated_get(bpy.context.evaluated_depsgraph_get())
        malha = avaliado.to_mesh()
        malha.calc_loop_triangles()
        matriz = avaliado.matrix_world
        normal_matriz = matriz.to_3x3().inverted().transposed()
        for triangulo in malha.loop_triangles:
            normal = (normal_matriz @ triangulo.normal).normalized()
            intensidade = .62 + .38*max(0,normal.dot(luz))
            cor = objeto.data.materials[triangulo.material_index].diffuse_color
            for indice in triangulo.vertices:
                v = matriz @ malha.vertices[indice].co
                partes[parte].extend((v.x,v.z,-v.y,cor[0]*intensidade,cor[1]*intensidade,cor[2]*intensidade,1))
        avaliado.to_mesh_clear()
    for parte, valores in partes.items():
        (pasta/(grupo.name+'-'+parte+'.malha')).write_text('; Articulação exportada pelo Blender MCP.\n#(\n'+
            ''.join(' '.join(f'{v:.5f}' for v in valores[i:i+7])+'\n' for i in range(0,len(valores),7))+')\n')
print('Exportadas 50 malhas articuladas dos dez soldados.')
