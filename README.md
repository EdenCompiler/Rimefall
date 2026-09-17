# Rimefall — demo ampliada e guerra ártica

Sobrevivência tática em primeira pessoa durante um cerco ártico. O modo **Defesa do posto** é o tutorial solo com quatro soldados e três ondas de criaturas cegas. O modo **Guerra** acrescenta dois exércitos fictícios, cinco setores e uma batalha offline de 8 contra 8 com bots.

Implementado em **Common Lisp/SBCL**, exclusivamente com **LWLGL** para OpenGL 3.3, entrada e OpenAL. Os modelos são autorais, construídos e exportados pelo **Blender MCP**. O peso das armas, a mira, as recargas deliberadas e a vulnerabilidade seguem a referência de sensação de Hell Let Loose. A guerra usa uma frente móvel e monstros atraídos pelo som; a conexão direta usa lockstep determinístico com relé e hashes.

A interface segue a linguagem de um centro de operações: briefing de missão à esquerda, lista de destacamentos à direita, paleta carvão/verde-oliva/bronze e cartões de situação para a frente. O visual é inspirado em jogos de guerra de grande escala, mantendo textos e símbolos próprios de Rimefall.

## Executar

O repositório contém código-fonte, modelos e documentação. Na pasta do projeto, execute pelo código-fonte:

```bash
sbcl --script executar.lisp
```

Para gerar e executar o binário localmente:

```bash
sbcl --script compilar.lisp
./distribuicao/rimefall
```

O executável gerado contém o SBCL e o programa carregado. Mantenha `distribuicao/modelos/` ao lado dele. Não é necessário ter Blender ou SBCL instalado para usar esse executável. Binários e pacotes da demo não são versionados no repositório.

Para executar a simulação de guerra offline pelo terminal:

```bash
sbcl --script executar.lisp --guerra
```

Para abrir diretamente a guerra jogável, sem passar pelo menu:

```bash
sbcl --script executar.lisp --guerra-grafica
```

O botão **INICIAR GUERRA / 8 CONTRA 8** abre a batalha na janela; o atalho **G** faz a mesma transição caso o ponteiro ainda não esteja dentro da janela. A Aurora nasce no ponto de reunião avançado, em **X -6 / Z -55**, dentro da estrada sul do mapa, voltada para a frente; a Bruma usa o ponto oposto, em **X -6 / Z 55**. O HUD de orientação desaparece após quatro segundos para liberar a visão do mapa; **Tab** mostra ou oculta o HUD novamente. WASD move o soldado local; 1, 2 e 3 enviam ordens de ataque, defesa e reunião. Esc pausa a batalha e Q retorna ao menu. O painel usa o mesmo passo fixo, setores, bots, reforços e invasões do núcleo.

**Dependências nativas:** Linux x86-64, driver com OpenGL 3.3, GLFW 3 e OpenAL. Para executar ou compilar o código-fonte: SBCL, ASDF, Quicklisp e LWLGL instalada, por exemplo em `~/quicklisp/local-projects/LWLGL`. A inicialização procura o Quicklisp em `~/quicklisp/setup.lisp`. A biblioteca usada no desenvolvimento foi a LWLGL 2.2.0 local.

A janela inicia em 1280 × 720. No menu, **Nova sessão** começa outro cerco e substitui o progresso salvo; **Continuar** restaura o último estado. O combate restaurado começa pausado.

## Controles padrão

| Ação | Controle |
|---|---|
| Mover / olhar | WASD / mouse |
| Mira de ferro ou luneta | Segurar botão direito |
| Disparar | Botão esquerdo; manter para rajadas com a submetralhadora |
| Recarregar | R |
| Correr com mais ruído | Shift |
| Agachar e andar devagar | Ctrl |
| Recolher, trocar arma, recuperar dispositivo ou operar portão | E |
| Lançar pedra sonora | G |
| Instalar isca temporizada | F |
| Apoiar ou soltar a arma | B |
| Pausa e controles | Esc |
| Navegar nos menus | Mouse ou Tab e Enter |
| Histórico entre vidas | H |
| Editar diário e rótulos | Clicar no campo; Ctrl+V cola; Esc termina a edição |
| Selecionar célula do mapa | Clique ou setas, entre vidas |

Os atalhos de teclado do combate são configuráveis. Se uma nova tecla já estiver em uso, os dois comandos trocam de tecla. Esc, Tab e Enter ficam reservados à interface. Mirar e disparar continuam nos botões direito e esquerdo.

Na guerra, **4** e **5** percorrem o arsenal compartilhado (incluindo os fuzis de precisão), **Esc** pausa a simulação e **Q** retorna ao menu. A troca conserva a quantidade total de munição disponível.

**Configurações** também permite ajustar sensibilidade, campo de visão, resolução, tela cheia, VSync, partículas de neve e volumes geral, de efeitos e ambiente. Tela cheia é aplicada na próxima abertura; os demais ajustes são aplicados durante a execução. O volume não altera a audição das criaturas.

## Primeira sessão

1. Escolha o fuzil básico nas notas. As opções bloqueadas mostram seus critérios quando apontadas ou selecionadas com Tab.
2. Entre com André Nunes. A escopeta fica à direita da saída do abrigo.
3. Encontre o portão central e use E para operá-lo. O rangido atrai criaturas; fechado, ele bloqueia passagem, disparos e parte do som.
4. Caminhe com atenção às superfícies. Madeira ressoa mais que neve; metal é ainda mais ruidoso. Gelo frágil estala na primeira passagem e permanece quebrado entre vidas.
5. Explore o setor norte para buscar carabina e submetralhadora. Os fuzis com luneta ficam nas áreas laterais ampliadas. São desvios opcionais, com munição finita.
6. Após morrer, leia as evidências, anote o mapa conhecido e prepare outro soldado.

O primeiro ataque recebido causa um ferimento permanente; o segundo mata. Os ataques têm preparação perceptível. As ondas têm **3, 4 e 5 inimigos**, com oito segundos de intervalo. Eliminar as três vence a sessão; perder o quarto soldado encerra o cerco. Inimigos restantes, corpos, suprimentos consumidos, clima e dispositivos continuam entre vidas. A preparação e a pausa suspendem a simulação.

## Seis armas

Só uma arma pode ser carregada. Trocar deixa a anterior no chão; a munição já recolhida permanece separada por tipo. Descobrir uma arma não desbloqueia seu preparo imediatamente: é preciso eliminar uma criatura com ela e transmitir a experiência na morte.

| Arma | Kit por vida: carregada + reserva | Funcionamento |
|---|---:|---|
| Fuzil de ferrolho | 4 + 8 | Preciso, ferrolho automático lento, recarga por cartucho |
| Escopeta de patrulha | 2 + 6 | Forte de perto, telha animada e recarga por cartucho |
| Carabina semiautomática | 8 + 16 | Um clique por tiro; dois impactos no torso de perto |
| Submetralhadora | 20 + 20 | Disparo contínuo, recuo acumulado e carregador destacável |
| Fuzil de precisão | 10 + 10 | Semiautomático, luneta 2×, dois impactos no torso |
| Fuzil de franco-atirador | 5 + 5 | Luneta 4×, ferrolho mais lento, um impacto no torso |

As lunetas ampliam a cena sem remover neve, neblina ou obstáculos. Impactos altos recebem multiplicador de dano; não há confirmação visual de acerto, barra de vida inimiga ou indicador de posição.

A recarga insere cartuchos um a um, exceto na submetralhadora, que troca o carregador. Disparar pode interromper a recarga com a munição já disponível; um cartucho ainda em animação não entra no inventário. Ferrolhos, culatras, telha, carregador, braços, cartuchos e movimento de saque são animados separadamente. Movimentar-se, correr e respirar afeta a apresentação da arma.

## Conhecimento e equipamento experimental

O acervo coletivo guarda evidências estruturadas, com origem e instante. Aprendizados repetidos acrescentam histórico sem multiplicar benefícios. Os desbloqueios duram até começar outra sessão e não são consumidos.

| Preparo | Descoberta necessária | Benefício |
|---|---|---|
| Disciplina de silêncio | Atrair uma criatura e ficar silencioso até ela concluir a busca | Passos com metade do alcance audível |
| Distração sonora | Uma pedra desviar uma criatura que investigava um ruído seu | Quatro pedras iniciais, em vez de duas |
| Isca temporizada | Desviar a investigação de um ruído seu com o dispositivo | Dispositivo recuperável: espera 3 s e emite ruído por 5 s |
| Bipé portátil | Eliminar uma criatura usando o apoio do bipé | Apoio ao agachar mesmo em terreno aberto |

Escolha **até um preparo inicial**. Além dele, é possível carregar **um equipamento experimental encontrado**. Outro equipamento ocupa esse mesmo espaço e deixa o anterior no chão. Duplicatas não acumulam benefícios. Recupere uma isca instalada antes de trocar o dispositivo que a originou.

F instala a isca; E permite recuperá-la e desarmá-la, inclusive antes do disparo. Um dispositivo deixado por um soldado morto permanece no campo. Ele não se duplica no corpo.

B apoia a arma junto de cobertura baixa quando o soldado está parado. Com bipé, também funciona ao agachar no chão. O apoio reduz a oscilação e não aumenta o dano. Movimento, recarga ou troca de arma solta o apoio; levantar-se também solta o bipé.

## Mapa, diário e memorial

O terreno observado entra primeiro no registro individual: distância, cone de observação e oclusão limitam a descoberta. Esse mapa só passa ao esquadrão **na morte**. A tela **Mapa explorado e marcas** fica nas notas entre vidas e nunca mostra inimigos ou suprimentos automaticamente.

Clique numa célula conhecida, escreva um rótulo e grave. Há até 24 marcas, com 48 caracteres cada; gravar no mesmo local substitui a marca. A seleção também funciona pelas setas. As marcas não alteram a simulação.

O diário aceita até 600 caracteres, com acentos, quebras de linha e colagem. A roda do mouse rola o texto. Ele é um registro livre, sem interpretação ou efeito mecânico.

André Nunes, Lúcia Reis, Caio Moura e Helena Duarte possuem nomes e histórias diferentes, mas os mesmos atributos. O memorial conserva identidade, causa da morte, onda, eliminações, evidências e diário de cada vida. O último soldado também transmite suas descobertas.

## Som, vento e criaturas

Passos, armas, recargas, interação, gelo e iscas produzem eventos sonoros com posição, alcance, origem e instante. Paredes e portões fechados atenuam esses eventos. A criatura investiga a **última posição ouvida**, nunca acompanha silenciosamente a posição atual do jogador. Ao chegar, busca por sete segundos sem pistas novas antes de voltar a patrulhar. Contato próximo ainda permite atacar um soldado silencioso.

Cada ciclo climático tem 30–45 segundos de calmaria, quatro de vento crescente e dez de rajada. Durante a rajada, os passos têm metade do alcance audível e a visibilidade cai. Disparos e chamados continuam conspícuos. O clima é determinístico e seus temporizadores são salvos.

Nas ondas dois e três, um **chamador** substitui uma criatura comum. Ao encontrar o soldado por contato, ele prepara um chamado por dois segundos. Eliminá-lo interrompe a ação. O chamado concluído atrai criaturas à posição do chamador, sem compartilhar a posição atual do soldado. Criaturas têm braços e pernas animados, preparação de ataque e queda gradual.

## Guerra do Círculo Polar

O protótipo possui os exércitos originais **União Aurora** e **Liga da Bruma**, com cores, emblemas e uniformes distintos e funções equilibradas. Cada lado começa com dois esquadrões de quatro; a meta de escala é quatro esquadrões de oito, ou 32 contra 32.

O mapa principal da guerra mede **1 km²**. Ele liga os QGs por uma frente contínua com Passagem do Rio, Aldeia de Gelo, Linha das Trincheiras, Pátio Industrial e Colina do Farol. O arquivo `mapas/guerra.dat` é a referência de setores e caches; `modelos/guerra.blend` e `modelos/guerra.malha` são a cena low-poly criada no Blender MCP, com rio congelado, estradas, casas, floresta, trincheiras, galpões, tanques, farol e quatro caches opcionais.

Os cinco setores — Passagem do Rio, Aldeia de Gelo, Linha das Trincheiras, Pátio Industrial e Colina do Farol — formam uma frente única. A presença superior captura a zona; contestação interrompe o progresso e a equipe adversária pode recuperar o setor. A partida dura até 60 minutos, até um quartel-general ser destruído ou até a reserva de reforços acabar.

Cada setor possui um **ponto forte** sinalizado pela cobertura local. Permanecer dentro dele vale por dois soldados na disputa, então uma equipe menor consegue segurar uma posição preparada. Tiros que passam perto acumulam **supressão**: a mira oscila, a resposta dos bots fica menos precisa e a pressão decai gradualmente quando o fogo cessa.

Fuzileiros, médicos, suporte, engenheiros e comandantes têm kits básicos próprios. O médico estabiliza e reanima uma vez um soldado incapacitado durante uma janela de 45 segundos. Mortes confirmadas consomem a reserva compartilhada e entram na fila do ponto de reunião. Caminhões transportam passageiros, munição e reforços; morteiros exigem operador e observador.

Ruídos acumulam pressão sonora. Depois do limite e de um aviso, uma grande invasão ataca a região mais ruidosa, podendo atingir setores, comboios e quartéis. Monstros podem destruir qualquer QG e derrotar o exército. O relé de conexão direta apenas ordena comandos e compara hashes; cada cliente executa a simulação determinística.

## Salvamento

Uma única sessão é gravada a cada cinco segundos de combate, ao sair normalmente e imediatamente nas mortes e transições. Inclui munição, equipamentos, inimigos, dispositivos, corpos, recargas, clima, ondas, exploração, marcas, notas e memorial. Não há seleção de salvamentos antigos.

Caminhos padrão:

- Sessão: `~/.local/share/rimefall/sessao.sexp`, respeitando `XDG_DATA_HOME`.
- Preferências: `~/.config/rimefall/preferencias.sexp`, respeitando `XDG_CONFIG_HOME`.

A gravação usa arquivo temporário e substituição atômica. O leitor aceita somente dados, com avaliação e extensões de leitura desativadas. Dados incompatíveis ou danificados são informados na tela e não são substituídos silenciosamente. **Nova sessão** é a ação explícita para começar do zero. Preferências permanecem.

Uma falha de gravação impede iniciar outro soldado até a gravação ser recuperada; o botão **Tentar salvar** repete a tentativa. Uma interrupção abrupta pode perder até cinco segundos desde o último salvamento concluído. As mortes são gravadas imediatamente, sem esperar esse intervalo.

## Compilar e testar

```bash
sbcl --script verificar.lisp
sbcl --script compilar.lisp
```

A compilação executa os testes antes de gerar `distribuicao/rimefall` e copiar as malhas. Os testes de regras não abrem janela. Blender só é necessário para editar ou reconstruir os modelos.

Ensaio gráfico com janela **virtual e áudio inaudível**:

```bash
env -u WAYLAND_DISPLAY LWLGL_GLFW_PLATFORM=x11 ALSOFT_DRIVERS=null \
  xvfb-run -a -s '-screen 0 1280x720x24' \
  ./distribuicao/rimefall --validar
```

Também funciona com `sbcl --script executar.lisp --validar`. São necessários Xvfb e xauth. Forçar X11 e remover `WAYLAND_DISPLAY` impede que o GLFW abra uma janela no Wayland da área de trabalho. `ALSOFT_DRIVERS=null` exercita OpenAL sem reprodução audível. `--sem-audio` desliga completamente a reprodução, preservando a simulação auditiva.

O roteiro prepara situações e usa as mesmas ações de jogo: exploração, coleta, tiro, recarga, descobertas, morte, notas, mapa, segundo soldado, rajada, chamador, gravação, continuação e uso das quatro armas adicionais. Grava capturas reais e usa diretórios de dados isolados dentro de `validacao/`. É um ensaio reproduzível, não uma partida inteira controlada por uma pessoa.

## Organização

## Pipeline de arte do mapa

`modelos/guerra.blend` é a fonte única da frente de combate. O pipeline
`modelos/aplicar-pipeline.py` é executado no Blender MCP e faz quatro passos
repetíveis: cria a atlas fria de 256 × 256, gera UVs determinísticas para cada
malha, associa o material pela superfície (neve, gelo, madeira, metal,
concreto ou terra) e grava propriedades de origem usadas na revisão. A cena
continua sendo a mesma fonte para a exportação de `guerra.malha` e para
`colisoes-guerra.lisp`, evitando que a colisão se afaste do visual.

O resultado fica em `modelos/atlas-frio.png` e
`modelos/materiais-frio.json`. A malha carregada pelo runtime mantém o formato
de cor por vértice como fallback leve da LWLGL; a atlas e os UVs já estão
preparados para o carregador de texturas da biblioteca quando o caminho
texturizado for habilitado. Para reaplicar o acabamento em uma instância
isolada do Blender MCP:

```text
exec(compile(open('modelos/aplicar-pipeline.py', encoding='utf-8').read(),
             'aplicar-pipeline.py', 'exec'))
```

O script é idempotente: pode ser executado novamente depois de editar a
geometria, e sempre sobrescreve a atlas e os metadados com o mesmo resultado
determinístico.

| Arquivo | Responsabilidade |
|---|---|
| `notas-de-campo.lisp` | Catálogo, evidências e validação do preparo |
| `campo.lisp` | Simulação, armas, terreno, audição, navegação, clima e exploração |
| `rimefall.lisp` | Sessão, morte, transições e `rimefall:iniciar-jogo` |
| `persistencia.lisp` | Formato de dados, salvamento, continuação e preferências |
| `guerra.lisp` | Exércitos, esquadrões, funções, setores, reforços e objetivos |
| `rede.lisp` | Lockstep, relé, comandos, hashes e clientes |
| `invasoes.lisp` | Pressão sonora, hordas e dano aos quartéis |
| `logistica.lisp` | Caminhões, morteiros, transporte e suprimentos |
| `comunicacao.lisp` | Ordens, pings, canais e mensagens |
| `apresentacao.lisp` | Gráficos, animações, áudio e ciclo da janela pela LWLGL |
| `interface.lisp` | Menus, notas, memorial, mapa, configurações e entrada |
| `interface-guerra.lisp` | Painel da frente, ordens, reforços e invasões |
| `testes.lisp` | Verificações automáticas sem janela |
| `mapas/posto.dat` | Definição compartilhada do terreno, colisões e suprimentos do tutorial |
| `mapas/guerra.dat` | Definição dos setores, QGs, rio, floresta e caches da guerra |
| `modelos/gerar-modelos.py` | Construção e exportação executadas pelo Blender MCP |
| `modelos/gerar-mapa-guerra.py` | Construção e exportação do mapa principal pelo Blender MCP |
| `modelos/aplicar-pipeline.py` | UVs, atlas fria, materiais e metadados da cena |
| `modelos/atlas-frio.png` | Atlas procedural de superfícies frias (256 × 256) |
| `modelos/materiais-frio.json` | Metadados versionados de materiais e faixas UV |
| `modelos/rimefall.blend` | Fonte editável, com coleções independentes |
| `modelos/guerra.blend` | Fonte editável do mapa de 1 km² da guerra |

`modelos/*.malha` contém posição e cor dos triângulos exportados; não há recursos baixados de terceiros. O jogo não inicia Blender. Os geradores reconstroem as cenas autorais: execute-os somente em instâncias separadas. As coleções incluem as cinco funções de cada exército, metralhadora, pistola, morteiro, rádio, caminhão, três monstros adicionais e o mapa completo da guerra, além das peças móveis animadas nos arquivos `.blend`.

Os parâmetros de ritmo ficam no começo de `campo.lisp`, incluindo `*armamentos*`, velocidades, alcance auditivo e neblina. A simulação usa passo fixo de 1/60 s. Todos os identificadores e comentários autorais são em português; símbolos exigidos por Common Lisp, Python, GLSL e APIs conservam os nomes originais.

Consulte [VALIDACAO.md](VALIDACAO.md) para resultados, capturas e condições reais das medições. O objetivo é 60 FPS; medições em Xvfb com renderização por software não representam o desempenho de uma GPU dedicada.
