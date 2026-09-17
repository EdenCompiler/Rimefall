"""Exporta a mesma geometria completa e articulada, com matrizes atualizadas."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

pasta = Path(__file__).resolve().parent
luz = Vector((-.35,-.5,1)).normalized()
bpy.context.view_layer.update()
grafo = bpy.context.evaluated_depsgraph_get()
inventario = {}

def gravar(nome, valores):
    assert valores and len(valores) % 21 == 0, nome
    (pasta/(nome+'.malha')).write_text('; Modelo autoral exportado pelo Blender MCP; metros, Y para cima.\n#(\n'+
        ''.join(' '.join(f'{v:.5f}' for v in valores[i:i+7])+'\n' for i in range(0,len(valores),7))+')\n', encoding='utf-8')
    inventario[nome] = {'triangulos': len(valores)//21,
        'minimo': [round(min(valores[eixo::7]),5) for eixo in range(3)],
        'maximo': [round(max(valores[eixo::7]),5) for eixo in range(3)]}

for grupo in sorted(bpy.context.scene.collection.children, key=lambda c:c.name):
    if not grupo.name.startswith(('soldado-', 'primeira-pessoa-')):
        continue
    partes = {nome: [] for nome in ('tronco','perna-esquerda','perna-direita','braco-esquerdo','braco-direito')}
    for objeto in grupo.objects:
        if objeto.type != 'MESH':
            continue
        parte = objeto['articulacao-rimefall']
        avaliado = objeto.evaluated_get(grafo)
        malha = avaliado.to_mesh()
        malha.calc_loop_triangles()
        matriz = avaliado.matrix_world.copy()
        normal_matriz = matriz.to_3x3().inverted().transposed()
        for triangulo in malha.loop_triangles:
            normal = (normal_matriz @ triangulo.normal).normalized()
            intensidade = .65 + .35*max(0,normal.dot(luz))
            cor = malha.materials[triangulo.material_index].diffuse_color
            for indice in triangulo.vertices:
                v = matriz @ malha.vertices[indice].co
                partes[parte].extend((v.x,v.z,-v.y,cor[0]*intensidade,cor[1]*intensidade,cor[2]*intensidade,1))
        avaliado.to_mesh_clear()
    completo = [v for valores in partes.values() for v in valores]
    gravar(grupo.name, completo)
    if grupo.name.startswith('soldado-'):
        assert abs(min(completo[1::7])) < .001, 'Pés fora do solo'
        assert 1.80 < max(completo[1::7]) < 1.9, 'Altura fora da escala humana'
        assert max(completo[0::7]) - min(completo[0::7]) < .90, 'Largura excessiva'
        for parte, valores in partes.items():
            gravar(grupo.name+'-'+parte, valores)
(pasta/'inventario-soldados.json').write_text(json.dumps(inventario,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Exportadas %d malhas; escala e origem verificadas.' % len(inventario))
