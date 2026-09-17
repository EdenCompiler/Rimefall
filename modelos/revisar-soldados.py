"""Pranchas de revisão no Blender; não desloca a geometria de exportação."""
import bpy
from pathlib import Path
from mathutils import Vector

pasta = Path(__file__).resolve().parents[1]/'validacao'
cena = bpy.data.scenes.get('Revisão dos soldados') or bpy.data.scenes.new('Revisão dos soldados')
for objeto in list(cena.objects):
    bpy.data.objects.remove(objeto, do_unlink=True)
bpy.context.window.scene = cena
cena.render.engine = 'BLENDER_WORKBENCH'
cena.render.resolution_x = 1280
cena.render.resolution_y = 720
cena.render.resolution_percentage = 100
cena.render.image_settings.file_format = 'PNG'
cena.display.shading.light = 'STUDIO'
cena.display.shading.color_type = 'MATERIAL'
cena.display.shading.show_shadows = True
cena.display.shading.show_cavity = True
cena.display.shading.cavity_type = 'BOTH'
cena.display.shading.background_type = 'WORLD'
cena.world = bpy.data.worlds.new('Fundo dos soldados')
cena.world.color = (.13,.16,.18)
camera = bpy.data.objects.new('Câmera de revisão', bpy.data.cameras.new('Revisão ortogonal'))
cena.collection.objects.link(camera)
camera.location = (.6,9,3.7)
camera.rotation_euler = (Vector((0,0,.90))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 7.2
cena.camera = camera
for exercito in ('aurora','bruma'):
    instancias = []
    for indice,funcao in enumerate(('fuzileiro','medico','suporte','engenheiro','comandante')):
        objeto = bpy.data.objects.new('Revisão '+funcao, None)
        objeto.instance_type = 'COLLECTION'
        objeto.instance_collection = bpy.data.collections['soldado-'+exercito+'-'+funcao]
        objeto.location = ((indice-2)*1.3,0,0)
        cena.collection.objects.link(objeto)
        instancias.append(objeto)
    cena.render.filepath = str(pasta/('soldados-'+exercito+'.png'))
    bpy.ops.render.render(write_still=True)
    for objeto in instancias:
        bpy.data.objects.remove(objeto, do_unlink=True)
bpy.context.window.scene = bpy.data.scenes['Soldados de Rimefall']
print('Pranchas Aurora e Bruma renderizadas.')
