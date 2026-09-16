# Validação da demo ampliada

**Versão 0.3.0 · 16 de setembro de 2026 · Linux x86-64**

## Resultado

- **246 verificações do núcleo aprovadas**, executadas novamente pela compilação final.
- Executável gerado com SBCL 2.5.2 e LWLGL 2.2.0, com Bruno como autor no ASDF.
- Seis armas funcionais, incluindo fuzil de precisão com luneta 2× e fuzil de franco-atirador com luneta 4×.
- Mapa de testes ampliado para 84 × 84 metros, preservando quatro soldados, três ondas de 3/4/5 criaturas e morte após dois ataques.
- Quarenta e oito grupos de malha do posto e 38.680 triângulos do mapa principal, todos criados pelo Blender MCP, com fontes editáveis e geradores incluídos. O cenário do posto contém 18.972 triângulos; os novos grupos cobrem funções Aurora e Bruma, armas de apoio, caminhão e três monstros.
- Ensaio completo do executável iniciado a partir de `/tmp`, carregando seus modelos independentemente da pasta de trabalho.
- Interação nativa por teclado e mouse aprovada em uma janela virtual: configurações, remapeamento, diário acentuado, coleta, recarga, mira, gravação, continuação, marcas no mapa e dispositivo.
- Protótipo offline da guerra validado com 16 soldados, quatro esquadrões, cinco setores, ordens, pings, incapacitação, fila de reforços, logística, invasão e salvamento acíclico.

## Cobertura das regras

Os testes sem janela verificam critérios e evidências de descobertas, transmissão exclusivamente na morte, deduplicação com histórico, limites do preparo, diário sem efeito mecânico, quatro identidades com atributos iguais, continuidade do cerco, vitória, derrota e reinício limpo.

O combate é verificado quanto à conservação de munição, interrupção de recarga, ciclos das armas, tiro contínuo, apoio e bipé. Os testes também cobrem superfícies, gelo, portão aberto e fechado, mascaramento por rajadas, busca da última origem sonora, ausência de detecção visual e chamado interrompido ou concluído.

Equipamentos são exercitados na descoberta, troca, recuperação, morte e permanência no mundo. A exploração respeita distância, cone de observação e obstáculos; a mira com luneta não revela terreno periférico. O conhecimento do mapa só é transmitido na morte.

A persistência é testada com estado completo, temporizadores, gravação imediata da morte, retomada sem avanço fora do jogo, dados malformados, versão incompatível, restrições do leitor e preferências independentes da audição da IA.

## Ensaio gráfico e interface

O roteiro gráfico posiciona situações controladas e usa as mesmas funções do jogo para explorar, obter a escopeta, recarregar, eliminar criaturas, descobrir táticas, morrer, transmitir conhecimento, editar notas, marcar o mapa, preparar o substituto, usar equipamentos experimentais, exercitar clima e chamador, salvar e continuar. Também dispara e recarrega as quatro armas adicionais e verifica suas descobertas.

O roteiro de interação nativa envia eventos reais do X11 ao executável. Além de capturas, ele abre os dados salvos e confere arma, munição, diário com acentos, campo de visão, tecla remapeada, segundo soldado, preparo temporizado, dispositivo instalado e marca manual. Utiliza diretórios XDG temporários.

Um ensaio adicional do memorial com dez descobertas confirmou duas páginas acessíveis, sem truncamento. As capturas foram inspecionadas para avaliar legibilidade, notas, mapa, configurações, armas, miras e neblina.

Esses ensaios são automatizados; não equivalem a uma avaliação humana prolongada da dificuldade, do equilíbrio ou da sensação das armas. O áudio posicional foi exercitado com saída silenciosa, sem avaliação auditiva pelos alto-falantes.

## Ambiente e desempenho

Blender e jogo foram executados exclusivamente em X11 virtual, com `WAYLAND_DISPLAY` removido e backend X11 forçado. Nenhuma janela de validação foi aberta na área de trabalho. O dispositivo nulo do OpenAL manteve os testes inaudíveis.

Renderizador observado: **llvmpipe (LLVM 19.1.7, 256 bits)**, **OpenGL 4.5 Core Profile**, **Mesa 25.0.7-2+deb13u1**. A aplicação utiliza a interface OpenGL 3.3.

O executável final mediu **49,6 quadros/s em 1280 × 720**, com **3.750 quadros em 75,65 segundos**, VSync desativado no ensaio.

Trata-se de renderização por software em Xvfb, incluindo capturas e telas de interface. A meta de 60 quadros/s não foi atingida nesse ensaio; não foi medido o desempenho desta versão em uma GPU dedicada.

## Evidências

- [Testes do núcleo](validacao/testes.txt) e [compilação final](validacao/compilacao.txt)
- [Execução do binário](validacao/execucao-compilada.txt)
- [Interação nativa](validacao/interacao.txt) e [memorial](validacao/memorial.txt)
- [Diário acentuado](validacao/interacao-diario.png) e [mapa anotado](validacao/interacao-mapa.png)
- [Configurações](validacao/interacao-configuracoes.png)
- [Fuzil de precisão em mira](validacao/quadro-2950.png)
- [Fuzil de franco-atirador em mira](validacao/quadro-3630.png)
- [Inventário de malhas](modelos/inventario.txt)
- [Mapa principal da guerra](validacao/mapa-guerra.png) e [inventário da guerra](modelos/inventario-guerra.txt)

## Reproduzir

```bash
sbcl --script verificar.lisp
sbcl --script compilar.lisp
env -u WAYLAND_DISPLAY LWLGL_GLFW_PLATFORM=x11 ALSOFT_DRIVERS=null \
  xvfb-run -a -s '-screen 0 1280x720x24' ./distribuicao/rimefall --validar
```

Para repetir os eventos nativos, instale também Python 3, xdotool, xclip e ImageMagick. O arquivo `validacao/dados/memoria.sexp` é uma situação de teste obtida após uma morte no roteiro gráfico, incluída para reproduzir a tela de notas; não é o salvamento pessoal do usuário.

```bash
env -u WAYLAND_DISPLAY LWLGL_GLFW_PLATFORM=x11 ALSOFT_DRIVERS=null \
  xvfb-run -a -s '-screen 0 1280x720x24' python3 validacao/roteiro-interface.py
```

Os resultados acima registram a compilação local. O repositório distribui somente fontes, modelos e documentação; executável, pacote e seus arquivos SHA-256 ficam fora do versionamento. Ao compilar, mantenha os modelos ao lado do executável. Preferências e partidas normais são guardadas nos diretórios XDG.
