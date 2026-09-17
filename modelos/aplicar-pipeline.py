"""Aplica o pipeline de arte do mapa de Rimefall.

O script mantém a malha legada exportada para o runtime, mas prepara a cena
Blender para um fluxo de produção repetível: atlas procedural, UVs, materiais
por superfície e metadados. Assim, a mesma cena continua sendo a fonte de
geometria, colisões e acabamento visual.
"""

import bpy
import json
from pathlib import Path


PASTA = Path("/home/bruno/projetos/lisp_fps/modelos")
CAMINHO_ATLAS = PASTA / "atlas-frio.png"
CAMINHO_MATERIAIS = PASTA / "materiais-frio.json"
LADO_ATLAS = 256

if bpy.context.scene.name in ("Soldados de Rimefall", "Revisão dos soldados"):
    raise RuntimeError("Abra a cena do mapa antes de aplicar o atlas; soldados usam materiais próprios.")


def criar_atlas():
    """Cria uma atlas fria em quatro faixas de superfície."""
    imagem = bpy.data.images.get("atlas-frio")
    if imagem is None or imagem.size[0] != LADO_ATLAS or imagem.size[1] != LADO_ATLAS:
        if imagem is not None:
            bpy.data.images.remove(imagem)
        imagem = bpy.data.images.new(
            "atlas-frio", width=LADO_ATLAS, height=LADO_ATLAS, alpha=True
        )

    cores = (
        (0.78, 0.86, 0.88, 1.0),  # neve
        (0.20, 0.30, 0.34, 1.0),  # gelo
        (0.24, 0.16, 0.11, 1.0),  # madeira
        (0.24, 0.28, 0.30, 1.0),  # metal/concreto
    )
    pixels = [0.0] * (LADO_ATLAS * LADO_ATLAS * 4)
    for y in range(LADO_ATLAS):
        faixa = min(3, y // 64)
        for x in range(LADO_ATLAS):
            # Ruído determinístico evita que o resultado varie entre execuções.
            variacao = (((x * 17 + y * 31) % 19) - 9) / 180.0
            base = cores[faixa]
            indice = (y * LADO_ATLAS + x) * 4
            pixels[indice : indice + 4] = [
                max(0.0, min(1.0, base[0] + variacao)),
                max(0.0, min(1.0, base[1] + variacao)),
                max(0.0, min(1.0, base[2] + variacao)),
                1.0,
            ]
    imagem.pixels = pixels
    imagem.filepath_raw = str(CAMINHO_ATLAS)
    imagem.file_format = "PNG"
    imagem.save()
    return imagem


def criar_materiais(imagem):
    nomes = {
        "neve": "Rimefall / Neve",
        "gelo": "Rimefall / Gelo",
        "madeira": "Rimefall / Madeira",
        "metal": "Rimefall / Metal",
        "concreto": "Rimefall / Concreto",
        "terra": "Rimefall / Terra",
    }
    materiais = {}
    for chave, nome in nomes.items():
        material = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
        material.use_nodes = True
        principled = material.node_tree.nodes.get("Principled BSDF")
        textura = material.node_tree.nodes.get("Atlas de frio")
        if textura is None:
            textura = material.node_tree.nodes.new("ShaderNodeTexImage")
            textura.name = "Atlas de frio"
            textura.label = "Atlas de frio"
        textura.image = imagem
        textura.interpolation = "Linear"
        if principled is not None:
            for ligacao in list(material.node_tree.links):
                if ligacao.to_node == principled and ligacao.to_socket == principled.inputs["Base Color"]:
                    material.node_tree.links.remove(ligacao)
            material.node_tree.links.new(textura.outputs["Color"], principled.inputs["Base Color"])
            principled.inputs["Roughness"].default_value = 0.88 if chave in ("neve", "gelo") else 0.72
            if "Specular IOR Level" in principled.inputs:
                principled.inputs["Specular IOR Level"].default_value = 0.25
        material["pipeline-rimefall"] = "uv-atlas-frio-v1"
        material["material-superficie"] = chave
        materiais[chave] = material
    return materiais


def classificar_superficie(nome):
    texto = nome.lower()
    if any(palavra in texto for palavra in ("neve", "gelo", "placa", "crista")):
        return "neve"
    if any(palavra in texto for palavra in ("madeira", "casa", "saco", "lona", "caixa", "pallet")):
        return "madeira"
    if any(palavra in texto for palavra in ("metal", "trilho", "antena", "tanque", "guindaste", "ferro")):
        return "metal"
    if any(palavra in texto for palavra in ("terra", "vala", "barro")):
        return "terra"
    return "concreto"


def aplicar_uvs_e_materiais(materiais):
    # Cada faixa ocupa 25% da atlas. A rotação de UV por objeto evita repetição
    # visível em paredes longas, sem depender de dados externos.
    faixas = {"neve": 0, "gelo": 1, "madeira": 2, "metal": 3, "concreto": 3, "terra": 3}
    quantidade = 0
    for objeto in bpy.context.scene.objects:
        if objeto.type != "MESH":
            continue
        malha = objeto.data
        uv = malha.uv_layers.get("UVMap") or malha.uv_layers.new(name="UVMap")
        chave = classificar_superficie(objeto.name)
        base_faixa = faixas[chave]
        minimo = min((vertice.co for vertice in malha.vertices), key=lambda vetor: vetor.x, default=None)
        deslocamento = (abs(minimo.y) if minimo is not None else 0.0) * 0.031
        for indice_poligono in malha.polygons:
            for indice_loop in indice_poligono.loop_indices:
                vertice = malha.vertices[malha.loops[indice_loop].vertex_index].co
                u = (vertice.x * 0.08 + vertice.z * 0.03 + deslocamento) % 1.0
                v = (base_faixa + 0.08 + ((vertice.y * 0.05) % 0.84)) / 4.0
                uv.data[indice_loop].uv = (u, v)
        # Uniformes e insígnias têm materiais próprios por exército. O atlas
        # cobre o cenário; preservar esses materiais mantém a identificação
        # visual das tropas Aurora e Bruma na cena editável.
        colecoes = [colecao.name.lower() for colecao in objeto.users_collection]
        eh_soldado = any(nome.startswith("soldado-aurora") or nome.startswith("soldado-bruma")
                         for nome in colecoes)
        if not eh_soldado:
            malha.materials.clear()
            malha.materials.append(materiais[chave])
        elif any(nome.startswith("soldado-aurora") for nome in colecoes):
            chave = "uniforme-aurora"
        else:
            chave = "uniforme-bruma"
        objeto["pipeline-rimefall"] = "uv-atlas-frio-v1"
        objeto["material-superficie"] = chave
        objeto["origem-colisao"] = "cena-guerra-blend"
        quantidade += 1
    return quantidade


def salvar_metadados(quantidade):
    dados = {
        "versao": 1,
        "atlas": "atlas-frio.png",
        "resolucao": [LADO_ATLAS, LADO_ATLAS],
        "objetos_mapeados": quantidade,
        "faixas": {
            "neve": [0.0, 0.25],
            "gelo": [0.25, 0.50],
            "madeira": [0.50, 0.75],
            "metal_concreto_terra": [0.75, 1.0],
        },
        "colisoes": "../colisoes-guerra.lisp",
        "exportacao_runtime": "guerra.malha",
        "observacao": "A malha do runtime mantém cor por vértice como fallback LWLGL.",
    }
    CAMINHO_MATERIAIS.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


imagem = criar_atlas()
materiais = criar_materiais(imagem)
quantidade = aplicar_uvs_e_materiais(materiais)
salvar_metadados(quantidade)
bpy.context.scene["pipeline-rimefall"] = "uv-atlas-frio-v1"
bpy.context.scene["fonte-colisoes"] = "cena-guerra-blend"
bpy.ops.wm.save_as_mainfile(filepath=str(PASTA / "guerra.blend"))
print("Pipeline aplicado: %d objetos, atlas-frio.png e materiais-frio.json." % quantidade)
